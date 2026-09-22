"""
Front-end feature extraction for the countermeasure.

LFCC (Linear Frequency Cepstral Coefficients) is the primary front end: it is
the official ASVspoof 2019 baseline feature and the best-performing feature in
the base paper (Garcia Martinez-Echevarria et al. 2026, Table 3: LFCC one-class
reached 0.0364 EER vs 0.105-0.147 for spectrogram/MFCC/CQCC).

Unlike MFCC, LFCC uses a LINEAR filterbank, so it retains resolution in the
high-frequency region where vocoder and TTS artefacts concentrate. The mel
scale deliberately discards that resolution, which is why MFCC underperforms
on this task.

Cepstral mean-variance normalisation (CMVN) is applied per utterance. This
removes channel- and tilt-dependent offsets, which matters doubly here because
our degraded audio has been through band-limiting telephony codecs.
"""

import numpy as np
from scipy.fftpack import dct
from scipy.signal import stft

SR = 16000


def linear_filterbank(n_filters, n_fft, sr, fmin=0.0, fmax=None):
    """Triangular filterbank on a LINEAR frequency scale."""
    if fmax is None:
        fmax = sr / 2
    n_bins = n_fft // 2 + 1
    points = np.linspace(fmin, fmax, n_filters + 2)
    bins = np.floor((n_fft + 1) * points / sr).astype(int)
    bins = np.clip(bins, 0, n_bins - 1)
    fb = np.zeros((n_filters, n_bins))
    for m in range(1, n_filters + 1):
        l, c, r = bins[m - 1], bins[m], bins[m + 1]
        if c == l:
            c = min(l + 1, n_bins - 1)
        if r == c:
            r = min(c + 1, n_bins - 1)
        for k in range(l, c):
            fb[m - 1, k] = (k - l) / max(c - l, 1)
        for k in range(c, r):
            fb[m - 1, k] = (r - k) / max(r - c, 1)
    return fb


def deltas(x, width=3):
    """Regression-based delta coefficients along the time axis."""
    n = (width - 1) // 2
    denom = 2 * sum(i ** 2 for i in range(1, n + 1)) or 1
    pad = np.pad(x, ((0, 0), (n, n)), mode="edge")
    d = np.zeros_like(x)
    for i in range(1, n + 1):
        d += i * (pad[:, n + i: n + i + x.shape[1]] - pad[:, n - i: n - i + x.shape[1]])
    return d / denom


def lfcc(y, sr=SR, n_fft=512, hop=160, n_filters=70, n_ceps=20,
         use_deltas=True, cmvn=True):
    """
    Compute LFCC (+ delta + delta-delta) for a waveform.
    Returns array of shape (n_features, n_frames).
    """
    if len(y) < n_fft:
        y = np.pad(y, (0, n_fft - len(y)))
    _, _, Z = stft(y, fs=sr, nperseg=n_fft, noverlap=n_fft - hop,
                   window="hamming", padded=False, boundary=None)
    power = (np.abs(Z) ** 2)
    fb = linear_filterbank(n_filters, n_fft, sr)
    energies = fb @ power
    logE = np.log(energies + 1e-10)
    c = dct(logE, type=2, axis=0, norm="ortho")[:n_ceps, :]

    if use_deltas:
        d1 = deltas(c)
        d2 = deltas(d1)
        c = np.vstack([c, d1, d2])

    if cmvn:
        # Per-utterance cepstral mean-variance normalisation.
        # Removes channel/tilt offsets introduced by codecs and by our
        # synthesis process, forcing the model onto fine-structure cues.
        c = (c - c.mean(axis=1, keepdims=True)) / (c.std(axis=1, keepdims=True) + 1e-8)
    return c.astype(np.float32)


def fixed_length(feat, n_frames=400):
    """Pad (by wrapping) or crop features to a fixed number of frames."""
    T = feat.shape[1]
    if T == n_frames:
        return feat
    if T < n_frames:
        reps = int(np.ceil(n_frames / T))
        feat = np.tile(feat, (1, reps))
    return feat[:, :n_frames]


def utterance_vector(feat):
    """
    Collapse a feature matrix to a fixed-length utterance vector
    (mean + std + skew-ish stats). Used by the classical GMM/SVM baseline.
    """
    m = feat.mean(axis=1)
    s = feat.std(axis=1)
    p10 = np.percentile(feat, 10, axis=1)
    p90 = np.percentile(feat, 90, axis=1)
    return np.concatenate([m, s, p10, p90]).astype(np.float32)


def extract(path_or_array, sr=SR, mode="matrix", n_frames=400):
    """Convenience loader: accepts a path or an array."""
    import soundfile as sf
    if isinstance(path_or_array, str):
        y, sr = sf.read(path_or_array, dtype="float32")
        if y.ndim > 1:
            y = y.mean(axis=1)
    else:
        y = np.asarray(path_or_array, dtype=np.float32)
    f = lfcc(y, sr=sr)
    if mode == "vector":
        return utterance_vector(f)
    return fixed_length(f, n_frames)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "src")
    from audio_synth import generate_utterance
    rng = np.random.default_rng(0)
    for lab in ["bonafide", "spoof"]:
        x = generate_utterance(lab, 3.0, rng=rng)
        f = lfcc(x)
        v = utterance_vector(f)
        print(f"{lab:9s} lfcc={f.shape} vec={v.shape} "
              f"mean={f.mean():.3f} std={f.std():.3f}")
