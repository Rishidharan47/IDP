"""
Fast difficulty probe: generate a small corpus, train the GMM baseline, report
EER. Used to calibrate the Phase-1 corpus so the task is non-trivial.
"""
import sys
import os
import numpy as np
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio_synth import generate_utterance, SR      # noqa: E402
from features import lfcc, fixed_length             # noqa: E402
from models import LFCCGMM                          # noqa: E402
from evaluate import full_report                    # noqa: E402

N = 60
NF = 240


def _one(args):
    lab, seed = args
    rng = np.random.default_rng(seed)
    y = generate_utterance(lab, 2.5, SR, rng)
    return fixed_length(lfcc(y, SR), NF), (0 if lab == "bonafide" else 1)


def main():
    jobs = []
    s = 7000
    for lab in ("bonafide", "spoof"):
        for i in range(N * 2):
            jobs.append((lab, s))
            s += 1
    with ProcessPoolExecutor(max_workers=2) as ex:
        res = list(ex.map(_one, jobs, chunksize=8))
    X = np.stack([r[0] for r in res])
    y = np.array([r[1] for r in res])
    # split half train / half test per class
    tr, te = [], []
    for c in (0, 1):
        idx = np.where(y == c)[0]
        tr += list(idx[:N])
        te += list(idx[N:])
    tr, te = np.array(tr), np.array(te)
    g = LFCCGMM(16).fit(X[tr], y[tr])
    rep = full_report(y[te], g.score(X[te]))
    print(f"  probe EER = {rep['eer']*100:.2f}%   AUC = {rep['auc']:.4f}")
    return rep["eer"]


if __name__ == "__main__":
    main()
