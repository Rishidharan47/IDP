"""System architecture diagram for the review deck."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "results", "figures")

NAVY = "#1E2761"
BLUE = "#2a78d6"
AQUA = "#1baf7a"
ORANGE = "#eb6834"
GREY = "#6b7280"
LIGHT = "#eef2f9"
INK = "#0b0b0b"
WHITE = "#ffffff"


def box(ax, x, y, w, h, title, sub, fc, tc=WHITE, fs=11, done=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.012,rounding_size=0.02",
                                facecolor=fc, edgecolor="none", zorder=3))
    ax.text(x + w / 2, y + h * 0.60, title, ha="center", va="center",
            fontsize=fs, fontweight="bold", color=tc, zorder=4)
    if sub:
        ax.text(x + w / 2, y + h * 0.26, sub, ha="center", va="center",
                fontsize=fs - 2.6, color=tc, alpha=0.9, zorder=4)
    if done is not None:
        # High-contrast badges that read on every box colour
        badge_fc = WHITE if done == "BUILT" else NAVY
        badge_tc = NAVY if done == "BUILT" else WHITE
        ax.text(x + w - 0.014, y + h - 0.028, done, ha="right", va="top",
                fontsize=8.0, fontweight="bold", color=badge_tc,
                bbox=dict(boxstyle="round,pad=0.28", facecolor=badge_fc,
                          edgecolor="none"), zorder=5)


def arrow(ax, x1, y1, x2, y2, color="#9aa3b2", style="-|>"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=15, linewidth=1.8,
                                 color=color, zorder=2,
                                 shrinkA=2, shrinkB=2))


def main():
    os.makedirs(FIG, exist_ok=True)
    fig, ax = plt.subplots(figsize=(13.0, 6.3), dpi=200)
    fig.patch.set_facecolor(WHITE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.012, 0.955, "System Architecture", fontsize=17,
            fontweight="bold", color=NAVY)
    ax.text(0.012, 0.905,
            "BUILT = working code demonstrated at this review        "
            "PHASE 2 = designed, scheduled for next review",
            fontsize=9.6, color=GREY)

    # ---- Row 1: capture + channel ---------------------------------------
    box(ax, 0.012, 0.66, 0.155, 0.175, "Call Audio", "live stream / wav",
        NAVY, done="BUILT")
    box(ax, 0.195, 0.66, 0.205, 0.175, "Telephony Channel",
        "G.711 · G.726 · Opus · MP3", ORANGE, done="BUILT")
    box(ax, 0.428, 0.66, 0.185, 0.175, "Framing + VAD",
        "2.5 s window, 0.5 s hop", BLUE, done="BUILT")
    box(ax, 0.641, 0.66, 0.175, 0.175, "LFCC Front End",
        "20 ceps +Δ +ΔΔ, CMVN", BLUE, done="BUILT")
    box(ax, 0.844, 0.66, 0.144, 0.175, "Feature Cache", ".npz tensors",
        GREY, done="BUILT")

    for x1, x2 in [(0.167, 0.195), (0.400, 0.428), (0.613, 0.641), (0.816, 0.844)]:
        arrow(ax, x1, 0.7475, x2, 0.7475)

    # ---- Row 2: training ------------------------------------------------
    ax.text(0.012, 0.585, "TRAINING PATH", fontsize=9.5, fontweight="bold", color=GREY)
    box(ax, 0.012, 0.365, 0.215, 0.175, "Codec Augmentation",
        "randomised channel + loss", AQUA, done="BUILT")
    box(ax, 0.255, 0.365, 0.215, 0.175, "ResNet Embedding",
        "324 K params, 128-dim", BLUE, done="BUILT")
    box(ax, 0.498, 0.365, 0.195, 0.175, "OC-Softmax Loss",
        "one-class, angular margin", BLUE, done="BUILT")
    box(ax, 0.721, 0.365, 0.267, 0.175, "Threshold Calibration",
        "dev-set abstention band", AQUA, done="BUILT")
    for x1, x2 in [(0.227, 0.255), (0.470, 0.498), (0.693, 0.721)]:
        arrow(ax, x1, 0.4525, x2, 0.4525)
    arrow(ax, 0.90, 0.66, 0.90, 0.545, color=BLUE)

    # ---- Row 3: inference + phase 2 -------------------------------------
    ax.text(0.012, 0.293, "INFERENCE PATH", fontsize=9.5, fontweight="bold",
            color=GREY)
    box(ax, 0.012, 0.075, 0.215, 0.175, "Streaming Scorer",
        "23 ms/window, RTF 0.05", BLUE, done="BUILT")
    box(ax, 0.255, 0.075, 0.235, 0.175, "3-Way Decision",
        "genuine / uncertain / synthetic", AQUA, done="BUILT")
    box(ax, 0.518, 0.075, 0.215, 0.175, "Scam-Intent Branch",
        "ASR → text classifier", "#f3d34a", tc=NAVY, done="PHASE 2")
    box(ax, 0.761, 0.075, 0.227, 0.175, "Fusion + Alert",
        "score fusion → user warning", "#f3d34a", tc=NAVY, done="PHASE 2")

    arrow(ax, 0.12, 0.365, 0.12, 0.250, color=BLUE)
    for x1, x2 in [(0.227, 0.255), (0.490, 0.518), (0.733, 0.761)]:
        arrow(ax, x1, 0.1625, x2, 0.1625)

    fig.tight_layout()
    out = os.path.join(FIG, "00_architecture.png")
    fig.savefig(out, facecolor=WHITE, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    main()
