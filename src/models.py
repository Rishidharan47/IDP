"""
Countermeasure models.

Two systems, matching the base paper's design:

  1. LFCC-GMM   - the official ASVspoof 2019 baseline. Two Gaussian mixture
                  models (one per class); score = log-likelihood ratio.
                  Fast, no GPU, fully interpretable. Our Phase-1 prototype.

  2. ResNet + OC-Softmax - the base paper's best-performing system
                  (Zhang et al. 2020 one-class learning). A residual CNN over
                  LFCC features trained with a one-class softmax objective that
                  compacts bona fide embeddings on a hypersphere and pushes
                  spoofed samples away by an angular margin.

OC-Softmax is preferred over plain binary cross-entropy because it does not
assume the spoof class is well-sampled: it models only the bona fide class
tightly, which is exactly why the base paper found it generalised best to
unseen synthesis methods.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


# --------------------------------------------------------------------------
# 1. LFCC-GMM baseline
# --------------------------------------------------------------------------
class LFCCGMM:
    """ASVspoof-style two-GMM baseline scoring a log-likelihood ratio."""

    def __init__(self, n_components=16, covariance_type="diag", seed=0):
        from sklearn.mixture import GaussianMixture
        self.gm_bona = GaussianMixture(n_components=n_components,
                                       covariance_type=covariance_type,
                                       random_state=seed, max_iter=100,
                                       reg_covar=1e-4)
        self.gm_spoof = GaussianMixture(n_components=n_components,
                                        covariance_type=covariance_type,
                                        random_state=seed, max_iter=100,
                                        reg_covar=1e-4)

    @staticmethod
    def _frames(X, stride=3):
        """(N, F, T) -> (N*T/stride, F) pooled frame matrix."""
        N, Fdim, T = X.shape
        f = X.transpose(0, 2, 1).reshape(-1, Fdim)
        return f[::stride]

    def fit(self, X, y):
        self.gm_bona.fit(self._frames(X[y == 0]))
        self.gm_spoof.fit(self._frames(X[y == 1]))
        return self

    def score(self, X):
        """Higher score = more likely SPOOF."""
        out = np.zeros(len(X))
        for i, x in enumerate(X):
            f = x.T                      # (T, F)
            lb = self.gm_bona.score_samples(f).mean()
            ls = self.gm_spoof.score_samples(f).mean()
            out[i] = ls - lb
        return out


# --------------------------------------------------------------------------
# 2. ResNet + OC-Softmax
# --------------------------------------------------------------------------
class ResBlock(nn.Module):
    def __init__(self, cin, cout, stride=1):
        super().__init__()
        self.c1 = nn.Conv2d(cin, cout, 3, stride, 1, bias=False)
        self.b1 = nn.BatchNorm2d(cout)
        self.c2 = nn.Conv2d(cout, cout, 3, 1, 1, bias=False)
        self.b2 = nn.BatchNorm2d(cout)
        self.short = None
        if stride != 1 or cin != cout:
            self.short = nn.Sequential(
                nn.Conv2d(cin, cout, 1, stride, bias=False),
                nn.BatchNorm2d(cout))

    def forward(self, x):
        idt = x if self.short is None else self.short(x)
        o = F.relu(self.b1(self.c1(x)))
        o = self.b2(self.c2(o))
        return F.relu(o + idt)


class ResNetEmbedding(nn.Module):
    """Compact ResNet producing an L2-normalisable embedding."""

    def __init__(self, emb_dim=128, widths=(16, 32, 64, 128)):
        super().__init__()
        w = widths
        self.stem = nn.Sequential(
            nn.Conv2d(1, w[0], 3, 1, 1, bias=False),
            nn.BatchNorm2d(w[0]), nn.ReLU(inplace=True))
        self.l1 = ResBlock(w[0], w[0], 1)
        self.l2 = ResBlock(w[0], w[1], 2)
        self.l3 = ResBlock(w[1], w[2], 2)
        self.l4 = ResBlock(w[2], w[3], 2)
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(w[3], emb_dim)

    def forward(self, x):
        if x.dim() == 3:
            x = x.unsqueeze(1)                 # (B, 1, F, T)
        o = self.stem(x)
        o = self.l4(self.l3(self.l2(self.l1(o))))
        o = self.pool(o).flatten(1)
        return self.fc(o)


class OCSoftmax(nn.Module):
    """
    One-class softmax (Zhang et al. 2020).

    Learns a single direction w. Bona fide embeddings are pulled to within
    angular margin m_real of w; spoofed embeddings are pushed beyond m_fake.
    Score used at inference = -cos(theta), so HIGHER = more likely spoof.
    """

    def __init__(self, emb_dim=128, m_real=0.9, m_fake=0.2, alpha=20.0):
        super().__init__()
        self.w = nn.Parameter(torch.randn(1, emb_dim))
        nn.init.kaiming_uniform_(self.w, 0.25)
        self.m_real, self.m_fake, self.alpha = m_real, m_fake, alpha
        self.softplus = nn.Softplus()

    def forward(self, emb, labels=None):
        w = F.normalize(self.w, dim=1)
        e = F.normalize(emb, dim=1)
        cos = e @ w.t()                        # (B, 1)
        cos = cos.squeeze(1)
        if labels is None:
            return -cos, None
        # labels: 0 = bonafide, 1 = spoof
        m = torch.where(labels == 0,
                        torch.full_like(cos, self.m_real),
                        torch.full_like(cos, self.m_fake))
        sign = torch.where(labels == 0,
                           torch.ones_like(cos), -torch.ones_like(cos))
        loss = self.softplus(self.alpha * sign * (m - cos)).mean()
        return -cos, loss


class OCResNet(nn.Module):
    """ResNet embedding + OC-Softmax head."""

    def __init__(self, emb_dim=128, **kw):
        super().__init__()
        self.backbone = ResNetEmbedding(emb_dim=emb_dim)
        self.head = OCSoftmax(emb_dim=emb_dim, **kw)

    def forward(self, x, labels=None):
        return self.head(self.backbone(x), labels)

    @torch.no_grad()
    def score(self, X, device="cpu", batch=32):
        """Higher = more likely spoof."""
        self.eval()
        out = []
        for i in range(0, len(X), batch):
            xb = torch.as_tensor(X[i:i + batch], dtype=torch.float32, device=device)
            s, _ = self(xb)
            out.append(s.cpu().numpy())
        return np.concatenate(out)


def count_params(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
