"""Generate presentation figures from results.json and saved checkpoints."""

import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models import OCResNet                       # noqa: E402
from evaluate import roc_points, full_report      # noqa: E402
from telephony import TELEPHONY_CHANNELS          # noqa: E402
import torch                                      # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
FEAT = os.path.join(ROOT, "data", "feat")
FIG = os.path.join(RES, "figures")

# validated palette (dataviz reference instance, slots 1-3)
C_CLEAN = "#2a78d6"   # blue   - clean condition
C_DEG = "#eb6834"     # orange - telephony degraded
C_AUG = "#1baf7a"     # aqua   - with our augmentation
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e3e2de"
SURFACE = "#fcfcfb"

CHANNEL_LABEL = {
    "g711_ulaw": "G.711\n(PSTN)",
    "g726_32k": "G.726 32k\n(DECT)",
    "g726_16k": "G.726 16k\n(DECT)",
    "opus_12k": "Opus 12k\n(VoIP)",
    "opus_24k": "Opus 24k\n(VoIP)",
    "mp3_32k": "MP3 32k\n(stored)",
}


def _style(ax):
    ax.set_facecolor(SURFACE)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=10, length=0)
    ax.yaxis.grid(True, color=GRID, linewidth=1, zorder=0)
    ax.set_axisbelow(True)


def fig_headline(d):
    """The one chart that carries the argument."""
    s = d["summary"]["ResNet+OC-Softmax"]
    vals = [s["clean_eer"], s["telephony_eer"], s["augmented_telephony_eer"]]
    labels = ["Clean audio\n(lab condition)",
              "Telephony codecs\n(deployment)",
              "Telephony + our\naugmentation"]
    colors = [C_CLEAN, C_DEG, C_AUG]

    fig, ax = plt.subplots(figsize=(8.2, 5.0), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    bars = ax.bar(labels, vals, color=colors, width=0.56, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.2, f"{v:.1f}%",
                ha="center", va="bottom", fontsize=15, fontweight="bold", color=INK)
    ax.axhline(50, color=INK2, linestyle=(0, (4, 4)), linewidth=1.4, zorder=2)
    ax.text(2.46, 51, "random guessing", ha="right", va="bottom",
            fontsize=9.5, color=INK2, style="italic")
    ax.set_ylabel("Equal Error Rate  (lower is better)", fontsize=11, color=INK2)
    ax.set_ylim(0, 58)
    ax.yaxis.set_major_formatter(PercentFormatter())
    ax.set_title("A detector that looks perfect in the lab fails on a real phone call",
                 fontsize=13.5, fontweight="bold", color=INK, pad=16, loc="left")
    _style(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "01_headline_gap.png"),
                facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)


def fig_per_channel(d):
    det = d["detail"]
    clean_t = [det[f"OCResNet_clean_trained/{c}"]["eer"] * 100 for c in TELEPHONY_CHANNELS]
    aug_t = [det[f"OCResNet_aug_trained/{c}"]["eer"] * 100 for c in TELEPHONY_CHANNELS]
    x = np.arange(len(TELEPHONY_CHANNELS))
    w = 0.38

    fig, ax = plt.subplots(figsize=(9.6, 5.0), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    b1 = ax.bar(x - w / 2, clean_t, w, label="Trained on clean audio",
                color=C_DEG, zorder=3)
    b2 = ax.bar(x + w / 2, aug_t, w, label="Trained with codec augmentation",
                color=C_AUG, zorder=3)
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.8,
                    f"{b.get_height():.0f}%", ha="center", va="bottom",
                    fontsize=9.5, color=INK)
    ax.axhline(50, color=INK2, linestyle=(0, (4, 4)), linewidth=1.3, zorder=2)
    ax.text(len(x) - 0.55, 51, "random guessing", ha="right", va="bottom",
            fontsize=9, color=INK2, style="italic")
    ax.set_xticks(x)
    ax.set_xticklabels([CHANNEL_LABEL[c] for c in TELEPHONY_CHANNELS], fontsize=9.5)
    ax.set_ylabel("Equal Error Rate", fontsize=11, color=INK2)
    ax.set_ylim(0, 68)
    ax.yaxis.set_major_formatter(PercentFormatter())
    ax.set_title("Augmentation rescues five of six channels; Opus 24k trades a little "
                 "clean accuracy",
                 fontsize=12.5, fontweight="bold", color=INK, pad=16, loc="left")
    leg = ax.legend(frameon=False, fontsize=10.5, loc="upper left",
                    bbox_to_anchor=(0, 1.0), ncol=2)
    for t in leg.get_texts():
        t.set_color(INK2)
    _style(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "02_per_channel.png"),
                facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)


def fig_roc():
    """ROC curves recomputed from the saved checkpoints."""
    def load(split):
        z = np.load(os.path.join(FEAT, f"{split}.npz"))
        return z["X"], z["y"]

    net_clean = OCResNet(emb_dim=128)
    net_clean.load_state_dict(torch.load(os.path.join(RES, "ocresnet_clean.pt"),
                                         map_location="cpu"))
    net_aug = OCResNet(emb_dim=128)
    net_aug.load_state_dict(torch.load(os.path.join(RES, "ocresnet_aug.pt"),
                                       map_location="cpu"))

    Xc, yc = load("eval")
    curves = []
    curves.append(("Clean audio, clean-trained",
                   yc, net_clean.score(Xc), C_CLEAN))

    Xs, ys = [], []
    for ch in TELEPHONY_CHANNELS:
        X, y = load(f"eval_{ch}")
        Xs.append(X)
        ys.append(y)
    Xt = np.concatenate(Xs)
    yt = np.concatenate(ys)
    curves.append(("Telephony codecs, clean-trained", yt, net_clean.score(Xt), C_DEG))
    curves.append(("Telephony codecs, augmentation-trained", yt, net_aug.score(Xt), C_AUG))

    fig, ax = plt.subplots(figsize=(6.6, 6.0), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.plot([0, 1], [0, 1], color=INK2, linestyle=(0, (4, 4)), linewidth=1.2, zorder=2)
    ax.text(0.62, 0.56, "random guessing", fontsize=9, color=INK2,
            style="italic", rotation=36)
    for name, y, s, col in curves:
        fpr, tpr = roc_points(y, s)
        rep = full_report(y, s)
        ax.plot(fpr, tpr, color=col, linewidth=2.2, zorder=3,
                label=f"{name}  (AUC {rep['auc']:.3f})")
    ax.set_xlabel("False positive rate", fontsize=11, color=INK2)
    ax.set_ylabel("True positive rate", fontsize=11, color=INK2)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.set_title("ROC: the clean-trained detector collapses toward chance",
                 fontsize=12.5, fontweight="bold", color=INK, pad=14, loc="left")
    leg = ax.legend(frameon=False, fontsize=9.5, loc="lower right")
    for t in leg.get_texts():
        t.set_color(INK2)
    _style(ax)
    ax.xaxis.grid(True, color=GRID, linewidth=1)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "03_roc.png"), facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)


def fig_training(d):
    hc = d["history_clean"]
    ha = d["history_aug"]
    fig, ax = plt.subplots(figsize=(8.0, 4.6), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.plot([h["epoch"] for h in hc], [h["dev_eer"] * 100 for h in hc],
            color=C_DEG, linewidth=2.2, label="Clean-trained", zorder=3)
    ax.plot([h["epoch"] for h in ha], [h["dev_eer"] * 100 for h in ha],
            color=C_AUG, linewidth=2.2, label="Augmentation-trained", zorder=3)
    ax.set_xlabel("Training epoch", fontsize=11, color=INK2)
    ax.set_ylabel("Development-set EER", fontsize=11, color=INK2)
    ax.yaxis.set_major_formatter(PercentFormatter())
    ax.set_title("Both models converge; the difference appears only at deployment",
                 fontsize=12.5, fontweight="bold", color=INK, pad=14, loc="left")
    leg = ax.legend(frameon=False, fontsize=10.5)
    for t in leg.get_texts():
        t.set_color(INK2)
    _style(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "04_training.png"),
                facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)


def fig_pipeline_spectra():
    """Show what a telephony codec actually does to the signal."""
    import soundfile as sf
    from telephony import degrade
    from scipy.signal import welch
    src = os.path.join(ROOT, "data", "wav", "eval", "bonafide")
    f0 = sorted(os.listdir(src))[0]
    y, sr = sf.read(os.path.join(src, f0), dtype="float32")

    fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    for name, prof, col in [("Original 16 kHz", None, C_CLEAN),
                            ("Opus 12 kbps (VoIP)", "opus_12k", C_AUG),
                            ("G.711 (PSTN landline)", "g711_ulaw", C_DEG)]:
        yy = y if prof is None else degrade(y, sr, profile=prof)
        f, P = welch(yy, sr, nperseg=1024)
        ax.semilogy(f / 1000, P + 1e-14, color=col, linewidth=2.0,
                    label=name, zorder=3)
    ax.set_xlabel("Frequency (kHz)", fontsize=11, color=INK2)
    ax.set_ylabel("Power spectral density", fontsize=11, color=INK2)
    ax.set_xlim(0, 8)
    ax.set_title("Real codecs destroy the high-frequency band where TTS artefacts live",
                 fontsize=12.5, fontweight="bold", color=INK, pad=14, loc="left")
    leg = ax.legend(frameon=False, fontsize=10)
    for t in leg.get_texts():
        t.set_color(INK2)
    _style(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "05_codec_spectra.png"),
                facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(FIG, exist_ok=True)
    with open(os.path.join(RES, "results.json")) as f:
        d = json.load(f)
    fig_headline(d)
    fig_per_channel(d)
    fig_roc()
    fig_training(d)
    fig_pipeline_spectra()
    print("figures written to", FIG)
    for f in sorted(os.listdir(FIG)):
        print("  ", f)


if __name__ == "__main__":
    main()
