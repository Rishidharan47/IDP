"""
Real-time call-screening demo.

Streams a wav file through the detector in sliding windows, exactly as a live
call would arrive, and emits a running verdict. This is the deployment shape the
base paper describes as future work:

    "A possible use case would be a real-time component that monitors a call
     and, when a voice is classified as likely synthetic, issues a discreet
     warning to the user."

Three-way output with an abstention band, rather than a hard binary. The base
paper's detectors flagged 87.5% of genuine callers as fake (BPCER 0.875), which
would make a binary alarm useless in deployment. Abstaining in the uncertain
band keeps false alarms controllable.

Usage:
    python src/realtime_demo.py <file.wav> [--model results/ocresnet_aug.pt]
"""

import os
import sys
import time
import argparse
import numpy as np
import soundfile as sf
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from features import lfcc, fixed_length          # noqa: E402
from models import OCResNet                      # noqa: E402

SR = 16000
WIN_SEC = 2.5
HOP_SEC = 0.5
N_FRAMES = 240

GREEN, YELLOW, RED, RESET, BOLD = (
    "\033[92m", "\033[93m", "\033[91m", "\033[0m", "\033[1m")


class StreamingDetector:
    """Sliding-window scorer with hysteresis and a three-way verdict."""

    def __init__(self, model_path, thr_low=None, thr_high=None, smooth=3,
                 calib_path=None):
        self.model = OCResNet(emb_dim=128)
        self.model.load_state_dict(torch.load(model_path, map_location="cpu"))
        self.model.eval()

        # Thresholds are CALIBRATED on the development set, not hand-picked.
        # The OC-Softmax score distribution is saturated near -1 for bona fide,
        # so a naive band around zero badly under-detects. The abstention band
        # runs from the 95th percentile of bona fide scores to the 10th
        # percentile of spoof scores.
        if calib_path is None:
            calib_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "results", "calibration.json")
        lo, hi = -0.995, -0.820
        if os.path.exists(calib_path):
            import json
            c = json.load(open(calib_path))
            lo, hi = c.get("thr_low", lo), c.get("thr_high", hi)
        self.thr_low = lo if thr_low is None else thr_low
        self.thr_high = hi if thr_high is None else thr_high
        self.history = []
        self.smooth = smooth

    def score_window(self, chunk):
        f = fixed_length(lfcc(chunk, SR), N_FRAMES)
        with torch.no_grad():
            s, _ = self.model(torch.as_tensor(f[None], dtype=torch.float32))
        return float(s.item())

    def verdict(self, score):
        """Smoothed three-way decision."""
        self.history.append(score)
        avg = float(np.mean(self.history[-self.smooth:]))
        if avg >= self.thr_high:
            return "SYNTHETIC", avg
        if avg <= self.thr_low:
            return "GENUINE", avg
        return "UNCERTAIN", avg


def render(label, avg, t, latency_ms, lo=-1.0, hi=1.0):
    colour = {"GENUINE": GREEN, "UNCERTAIN": YELLOW, "SYNTHETIC": RED}[label]
    icon = {"GENUINE": "OK ", "UNCERTAIN": "?? ", "SYNTHETIC": "!! "}[label]
    # score bar spans the calibrated decision range
    span = max(hi - lo, 1e-6)
    pos = int(np.clip((avg - lo) / span, 0, 1) * 30)
    bar = "-" * pos + "|" + "-" * (30 - pos)
    return (f"  t={t:5.1f}s  [{bar}]  {colour}{BOLD}{icon}{label:<10}{RESET}"
            f"  score={avg:+.3f}   {latency_ms:5.1f} ms/window")


def run(path, model_path, calibrate=None):
    det = StreamingDetector(model_path)
    y, sr = sf.read(path, dtype="float32")
    if y.ndim > 1:
        y = y.mean(axis=1)
    if sr != SR:
        import scipy.signal as ss
        y = ss.resample(y, int(len(y) * SR / sr))
    win = int(WIN_SEC * SR)
    hop = int(HOP_SEC * SR)

    print(f"\n{BOLD}AI Voice-Scam & Deepfake Call Detector{RESET}  -- streaming demo")
    print(f"  source : {os.path.basename(path)}")
    print(f"  model  : {os.path.basename(model_path)}")
    print(f"  window : {WIN_SEC}s, hop {HOP_SEC}s")
    print(f"  band   : genuine <= {det.thr_low:+.3f} < uncertain < {det.thr_high:+.3f} <= synthetic  (calibrated on dev set)\n")

    lat = []
    final = "UNCERTAIN"
    for start in range(0, max(1, len(y) - win + 1), hop):
        chunk = y[start:start + win]
        if len(chunk) < win:
            chunk = np.pad(chunk, (0, win - len(chunk)))
        t0 = time.perf_counter()
        s = det.score_window(chunk)
        ms = (time.perf_counter() - t0) * 1000
        lat.append(ms)
        label, avg = det.verdict(s)
        final = label
        print(render(label, avg, start / SR, ms,
                     lo=det.thr_low - 0.01, hi=det.thr_high + 0.30))

    rtf = (np.mean(lat) / 1000) / HOP_SEC
    print(f"\n  {BOLD}final verdict: {final}{RESET}")
    print(f"  mean latency {np.mean(lat):.1f} ms/window   "
          f"real-time factor {rtf:.3f}  "
          f"({'faster' if rtf < 1 else 'SLOWER'} than real time)\n")
    return final, float(np.mean(lat)), float(rtf)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wav", nargs="?", default=None)
    ap.add_argument("--model", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "results", "ocresnet_aug.pt"))
    ap.add_argument("--demo", action="store_true",
                    help="run on one genuine and one synthetic sample")
    a = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if a.demo or a.wav is None:
        for lab in ("bonafide", "spoof"):
            d = os.path.join(root, "data", "wav", "eval", lab)
            f = sorted(os.listdir(d))[0]
            print("=" * 78)
            print(f"GROUND TRUTH: {lab.upper()}")
            run(os.path.join(d, f), a.model)
    else:
        run(a.wav, a.model)


if __name__ == "__main__":
    main()
