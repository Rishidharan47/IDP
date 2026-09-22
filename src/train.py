"""
Phase-1 experiments.

Three conditions, designed to demonstrate the base paper's limitation and our
proposed fix in one directly comparable table:

  E1  train CLEAN  -> test CLEAN              in-domain baseline
  E2  train CLEAN  -> test CODEC-DEGRADED     the gap the base paper admits to
  E3  train AUGMENTED -> test CODEC-DEGRADED  our proposed mitigation

E2 minus E1 quantifies the deployment gap. E3 minus E2 quantifies our
contribution.
"""

import os
import sys
import json
import time
import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader

sys.path.insert(0, os.path.dirname(__file__))
from models import LFCCGMM, OCResNet, count_params        # noqa: E402
from evaluate import full_report, format_report           # noqa: E402
from telephony import TELEPHONY_CHANNELS                  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEAT = os.path.join(ROOT, "data", "feat")
RES = os.path.join(ROOT, "results")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
SEED = 0


def load(split):
    d = np.load(os.path.join(FEAT, f"{split}.npz"))
    return d["X"], d["V"], d["y"]


def train_ocresnet(Xtr, ytr, Xdev, ydev, epochs=35, lr=3e-4, bs=32, log=None):
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    model = OCResNet(emb_dim=128).to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.StepLR(opt, step_size=12, gamma=0.5)

    ds = TensorDataset(torch.as_tensor(Xtr, dtype=torch.float32),
                       torch.as_tensor(ytr, dtype=torch.long))
    dl = DataLoader(ds, batch_size=bs, shuffle=True, drop_last=False)

    history = []
    best = {"eer": 1.0, "state": None, "epoch": -1}
    for ep in range(epochs):
        model.train()
        tot, nb = 0.0, 0
        for xb, yb in dl:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            opt.zero_grad()
            _, loss = model(xb, yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step()
            tot += float(loss.item())
            nb += 1
        sched.step()
        dev_scores = model.score(Xdev, device=DEVICE)
        rep = full_report(ydev, dev_scores)
        history.append({"epoch": ep, "loss": tot / max(nb, 1),
                        "dev_eer": rep["eer"], "dev_auc": rep["auc"]})
        if rep["eer"] <= best["eer"]:
            best = {"eer": rep["eer"],
                    "state": {k: v.detach().cpu().clone()
                              for k, v in model.state_dict().items()},
                    "epoch": ep}
        if log and (ep % 5 == 0 or ep == epochs - 1):
            log(f"    epoch {ep:3d}  loss={tot/max(nb,1):.4f}  "
                f"dev_EER={rep['eer']*100:.2f}%  dev_AUC={rep['auc']:.4f}")
    if best["state"] is not None:
        model.load_state_dict(best["state"])
    return model, history, best["epoch"]


def eval_all_channels(score_fn, tag, results, log):
    """Evaluate a scoring function on clean + every codec channel."""
    Xc, Vc, yc = load("eval")
    clean = full_report(yc, score_fn(Xc, Vc))
    results[f"{tag}/clean"] = clean
    log("  " + format_report(f"{tag} clean", clean))

    per_channel = {}
    agg_scores, agg_y = [], []
    for ch in TELEPHONY_CHANNELS:
        X, V, y = load(f"eval_{ch}")
        s = score_fn(X, V)
        rep = full_report(y, s)
        per_channel[ch] = rep
        results[f"{tag}/{ch}"] = rep
        agg_scores.append(s)
        agg_y.append(y)
        log("  " + format_report(f"{tag} {ch}", rep))

    pooled = full_report(np.concatenate(agg_y), np.concatenate(agg_scores))
    results[f"{tag}/telephony_pooled"] = pooled
    log("  " + format_report(f"{tag} POOLED", pooled))
    return clean, pooled, per_channel


def main():
    os.makedirs(RES, exist_ok=True)
    logf = open(os.path.join(RES, "train_log.txt"), "w")

    def log(msg):
        print(msg)
        logf.write(msg + "\n")
        logf.flush()

    log(f"device: {DEVICE}   torch {torch.__version__}")
    Xtr, Vtr, ytr = load("train")
    Xdev, Vdev, ydev = load("dev")
    Xa0, Va0, ya0 = load("train_aug0")
    Xa1, Va1, ya1 = load("train_aug1")

    Xaug = np.concatenate([Xtr, Xa0, Xa1])
    Vaug = np.concatenate([Vtr, Va0, Va1])
    yaug = np.concatenate([ytr, ya0, ya1])

    log(f"train clean {Xtr.shape}   train augmented {Xaug.shape}   dev {Xdev.shape}")
    results = {}

    # ---------------- Model A: LFCC-GMM baseline -------------------------
    log("\n=== Model A: LFCC-GMM (ASVspoof official baseline) ===")
    t0 = time.time()
    gmm = LFCCGMM(n_components=16).fit(Xtr, ytr)
    log(f"  trained in {time.time()-t0:.1f}s")
    eval_all_channels(lambda X, V: gmm.score(X), "GMM_clean_trained", results, log)

    log("\n--- LFCC-GMM trained WITH codec augmentation ---")
    t0 = time.time()
    gmm_aug = LFCCGMM(n_components=16).fit(Xaug, yaug)
    log(f"  trained in {time.time()-t0:.1f}s")
    eval_all_channels(lambda X, V: gmm_aug.score(X), "GMM_aug_trained", results, log)

    # ---------------- Model B: ResNet + OC-Softmax ------------------------
    log("\n=== Model B: ResNet + OC-Softmax (base paper's best system) ===")
    m = OCResNet(emb_dim=128)
    log(f"  trainable parameters: {count_params(m):,}")

    log("\n--- B1: trained on CLEAN audio ---")
    t0 = time.time()
    net_clean, hist_clean, be = train_ocresnet(Xtr, ytr, Xdev, ydev, log=log)
    log(f"  trained in {time.time()-t0:.1f}s (best epoch {be})")
    eval_all_channels(lambda X, V: net_clean.score(X, device=DEVICE),
                      "OCResNet_clean_trained", results, log)

    log("\n--- B2: trained WITH codec augmentation (our proposed fix) ---")
    t0 = time.time()
    net_aug, hist_aug, be2 = train_ocresnet(Xaug, yaug, Xdev, ydev, log=log)
    log(f"  trained in {time.time()-t0:.1f}s (best epoch {be2})")
    eval_all_channels(lambda X, V: net_aug.score(X, device=DEVICE),
                      "OCResNet_aug_trained", results, log)

    # ---------------- Headline summary ------------------------------------
    log("\n" + "=" * 72)
    log("HEADLINE RESULTS (EER %, lower is better)")
    log("=" * 72)
    rows = [
        ("LFCC-GMM", "GMM_clean_trained", "GMM_aug_trained"),
        ("ResNet+OC-Softmax", "OCResNet_clean_trained", "OCResNet_aug_trained"),
    ]
    log(f"{'System':22s} {'Clean':>9s} {'Telephony':>11s} {'Degradation':>12s} "
        f"{'+Aug':>9s} {'Recovered':>10s}")
    summary = {}
    for name, ck, ak in rows:
        c = results[f"{ck}/clean"]["eer"] * 100
        t = results[f"{ck}/telephony_pooled"]["eer"] * 100
        a = results[f"{ak}/telephony_pooled"]["eer"] * 100
        log(f"{name:22s} {c:8.2f}% {t:10.2f}% {t-c:+11.2f} {a:8.2f}% {t-a:+9.2f}")
        summary[name] = {"clean_eer": c, "telephony_eer": t,
                         "augmented_telephony_eer": a,
                         "degradation": t - c, "recovered": t - a,
                         "relative_improvement_pct": (t - a) / t * 100 if t > 0 else 0}
    log("=" * 72)

    with open(os.path.join(RES, "results.json"), "w") as f:
        json.dump({"detail": results, "summary": summary,
                   "history_clean": hist_clean, "history_aug": hist_aug,
                   "channels": TELEPHONY_CHANNELS}, f, indent=2)
    torch.save(net_aug.state_dict(), os.path.join(RES, "ocresnet_aug.pt"))
    torch.save(net_clean.state_dict(), os.path.join(RES, "ocresnet_clean.pt"))
    log(f"\nsaved results.json and model checkpoints to {RES}")
    logf.close()


if __name__ == "__main__":
    main()
