"""
Evaluation metrics for spoofing countermeasures.

EER is the primary metric used throughout the ASVspoof literature and by our
base paper. We also report AUC, and APCER/BPCER because the base paper's key
finding was a false-alarm pathology that raw accuracy hides:

    "the comparatively higher raw accuracy of some models is misleading: It
     stems from a strong bias toward labelling speech as spoofed (BPCER above
     0.83 for CQCC and LFCC), so most genuine clips are flagged as synthetic."

APCER = Attack Presentation Classification Error Rate (spoof accepted as real)
BPCER = Bona fide Presentation Classification Error Rate (real rejected)
"""

import numpy as np
from sklearn.metrics import roc_curve, roc_auc_score


def compute_eer(y_true, scores):
    """
    Equal Error Rate.
      y_true: 1 = spoof, 0 = bonafide
      scores: higher = more likely spoof
    Returns (eer, threshold).
    """
    fpr, tpr, thr = roc_curve(y_true, scores, pos_label=1)
    fnr = 1 - tpr
    idx = np.nanargmin(np.abs(fnr - fpr))
    eer = (fpr[idx] + fnr[idx]) / 2.0
    return float(eer), float(thr[idx])


def apcer_bpcer(y_true, scores, threshold):
    """Error rates at a fixed operating threshold."""
    pred_spoof = scores >= threshold
    spoof = y_true == 1
    bona = y_true == 0
    apcer = float(np.mean(~pred_spoof[spoof])) if spoof.any() else float("nan")
    bpcer = float(np.mean(pred_spoof[bona])) if bona.any() else float("nan")
    return apcer, bpcer


def full_report(y_true, scores, threshold=None):
    """Complete metric set for one evaluation condition."""
    y_true = np.asarray(y_true)
    scores = np.asarray(scores, dtype=float)
    eer, eer_thr = compute_eer(y_true, scores)
    thr = eer_thr if threshold is None else threshold
    apcer, bpcer = apcer_bpcer(y_true, scores, thr)
    try:
        auc = float(roc_auc_score(y_true, scores))
    except ValueError:
        auc = float("nan")
    acc = float(np.mean((scores >= thr).astype(int) == y_true))
    # balanced accuracy is the honest headline when classes are skewed
    bal = float(1.0 - (apcer + bpcer) / 2.0)
    return {
        "eer": eer, "auc": auc, "accuracy": acc, "balanced_accuracy": bal,
        "apcer": apcer, "bpcer": bpcer, "threshold": thr,
    }


def format_report(name, rep):
    return (f"{name:22s} EER={rep['eer']*100:6.2f}%  AUC={rep['auc']:.4f}  "
            f"BalAcc={rep['balanced_accuracy']:.4f}  "
            f"APCER={rep['apcer']:.3f}  BPCER={rep['bpcer']:.3f}")


def roc_points(y_true, scores):
    fpr, tpr, _ = roc_curve(y_true, scores, pos_label=1)
    return fpr, tpr
