"""
Phase-1 pipeline-validation corpus generator.

Generates two classes of speech-like audio using a source-filter vocal tract model:

  BONA FIDE  - models natural human phonation: Liljencrants-Fant style glottal
               excitation, F0 jitter and amplitude shimmer, moving formant
               trajectories, aspiration noise with full phase randomness.

  SPOOF      - models the well-documented artefacts of vocoded / neural TTS
               speech: over-smoothed spectral envelope, suppressed jitter and
               shimmer (unnaturally regular F0), band-limited high frequencies,
               minimum-phase reconstruction (loss of natural phase dispersion),
               and buzzy pulse-train excitation.

These are precisely the cues the anti-spoofing literature reports detectors
exploit (Todisco et al. 2019; Wang & Yamagishi 2021), so a countermeasure
trained here learns a meaningful decision boundary rather than a trivial one.

NOTE: This corpus exists to validate the end-to-end pipeline on a machine with
no dataset access. Phase 2 replaces it with ASVspoof 2019 LA by pointing the
loader at the real corpus - no other code changes are required.
"""

import numpy as np

SR = 16000

# Vowel formant targets (F1, F2, F3, F4) in Hz
VOWELS = {
    "a": (730, 1090, 2440, 3400),
    "e": (530, 1840, 2480, 3500),
    "i": (270, 2290, 3010, 3700),
    "o": (570, 840, 2410, 3300),
    "u": (300, 870, 2240, 3200),
    "ae": (660, 1720, 2410, 3300),
    "schwa": (500, 1500, 2500, 3400),
}
VOWEL_KEYS = list(VOWELS.keys())


def _glottal_pulse_train(f0_contour, sr, jitter, shimmer, rng, buzzy=False):
    """Excitation signal from an F0 contour with optional jitter/shimmer."""
    n = len(f0_contour)
    exc = np.zeros(n, dtype=np.float64)
    t = 0.0
    while t < n - 1:
        idx = int(t)
        f0 = f0_contour[idx]
        if jitter > 0:
            f0 *= 1.0 + rng.normal(0, jitter)
        period = sr / max(f0, 50.0)
        amp = 1.0
        if shimmer > 0:
            amp *= 1.0 + rng.normal(0, shimmer)

        if buzzy:
            # Vocoder-style impulse: sharp, spectrally flat -> buzzy quality
            exc[idx] += amp
        else:
            # Liljencrants-Fant style asymmetric glottal flow derivative:
            # smooth opening, abrupt closure -> natural -12 dB/oct tilt
            plen = int(period)
            if plen < 4:
                plen = 4
            oq = 0.6  # open quotient
            op = int(plen * oq)
            if idx + plen < n and op > 2:
                k = np.arange(op)
                # rising sinusoidal open phase then sharp return
                pulse = np.sin(np.pi * k / op) ** 2
                pulse = np.gradient(pulse)
                exc[idx:idx + op] += amp * pulse / (np.max(np.abs(pulse)) + 1e-9)
        t += period
    return exc


def _formant_filter(x, freqs, bws, sr):
    """Cascade of 2-pole resonators (vocal tract transfer function)."""
    y = x.copy()
    for f, bw in zip(freqs, bws):
        r = np.exp(-np.pi * bw / sr)
        theta = 2 * np.pi * f / sr
        a1 = -2 * r * np.cos(theta)
        a2 = r * r
        gain = (1 - 2 * r * np.cos(theta) + r * r)
        out = np.zeros_like(y)
        y1 = y2 = 0.0
        for i in range(len(y)):
            v = gain * y[i] - a1 * y1 - a2 * y2
            out[i] = v
            y2 = y1
            y1 = v
        y = out
    return y


def _formant_filter_fast(x, freqs, bws, sr):
    """Vectorised resonator cascade using scipy.lfilter (much faster)."""
    from scipy.signal import lfilter
    y = x.copy()
    for f, bw in zip(freqs, bws):
        r = np.exp(-np.pi * bw / sr)
        theta = 2 * np.pi * f / sr
        a = [1.0, -2 * r * np.cos(theta), r * r]
        b = [1 - 2 * r * np.cos(theta) + r * r]
        y = lfilter(b, a, y)
    return y


def _smooth_envelope(x, sr, n_cep=13):
    """
    Over-smooth the spectral envelope via low-order cepstral liftering.
    This is the canonical vocoder artefact: harmonic fine structure is lost and
    formant peaks are broadened, while the overall spectral tilt is preserved.
    """
    from scipy.signal import stft, istft
    nper, nov = 512, 384
    f, t, Z = stft(x, fs=sr, nperseg=nper, noverlap=nov)
    mag = np.abs(Z)
    phase = np.angle(Z)
    logmag = np.log(mag + 1e-10)          # (F, T), F = nper//2 + 1

    # real cepstrum along the frequency axis
    cep = np.fft.irfft(logmag, axis=0)    # length 2*(F-1) = nper
    L = cep.shape[0]
    lifter = np.zeros(L)
    lifter[:n_cep] = 1.0                  # keep low quefrency (envelope)
    lifter[-(n_cep - 1):] = 1.0           # mirror for a real result
    cep = cep * lifter[:, None]

    smooth = np.fft.rfft(cep, axis=0).real[:logmag.shape[0], :]
    Z2 = np.exp(smooth) * np.exp(1j * phase)
    _, y = istft(Z2, fs=sr, nperseg=nper, noverlap=nov)
    if len(y) < len(x):
        y = np.pad(y, (0, len(x) - len(y)))
    return y[:len(x)]


def _match_longterm_spectrum(y, ref, sr, n_cep=40):
    """
    Match y's long-term average spectrum to ref's.

    Modern TTS reproduces the global spectral balance of its training data very
    closely; only fine structure betrays it. Matching the long-term spectrum
    removes an unrealistically easy gross-tilt cue and forces the detector to
    rely on the subtle artefacts a real countermeasure must use.
    """
    from scipy.signal import stft, istft
    nper, nov = 512, 384
    _, _, Zy = stft(y, fs=sr, nperseg=nper, noverlap=nov)
    _, _, Zr = stft(ref, fs=sr, nperseg=nper, noverlap=nov)
    ly = np.log(np.abs(Zy).mean(axis=1) + 1e-10)
    lr = np.log(np.abs(Zr).mean(axis=1) + 1e-10)
    # smooth the correction so we only fix broad tilt, not fine structure
    corr = lr - ly
    c = np.fft.irfft(corr)
    c[n_cep:-(n_cep - 1)] = 0.0
    corr_s = np.fft.rfft(c).real[:len(corr)]
    Z2 = Zy * np.exp(corr_s)[:, None]
    _, out = istft(Z2, fs=sr, nperseg=nper, noverlap=nov)
    if len(out) < len(y):
        out = np.pad(out, (0, len(y) - len(out)))
    return out[:len(y)]


def _griffin_lim_artifact(x, sr, n_iter=12):
    """
    Discard the true phase and reconstruct it iteratively from the magnitude
    spectrogram (Griffin-Lim). This is exactly what magnitude-domain vocoders
    do, and it leaves the characteristic phase-incoherence artefact that
    phase-aware countermeasures are known to detect.
    """
    from scipy.signal import stft, istft
    nper, nov = 512, 384
    f, t, Z = stft(x, fs=sr, nperseg=nper, noverlap=nov)
    mag = np.abs(Z)
    # start from random phase, iterate STFT <-> iSTFT
    rng = np.random.default_rng(0)
    phase = np.exp(2j * np.pi * rng.random(mag.shape))
    Zi = mag * phase
    y = x
    for _ in range(n_iter):
        _, y = istft(Zi, fs=sr, nperseg=nper, noverlap=nov)
        _, _, Z2 = stft(y, fs=sr, nperseg=nper, noverlap=nov)
        ph = np.exp(1j * np.angle(Z2))
        if ph.shape != mag.shape:
            m = min(ph.shape[1], mag.shape[1])
            Zi = mag[:, :m] * ph[:, :m]
        else:
            Zi = mag * ph
    _, y = istft(Zi, fs=sr, nperseg=nper, noverlap=nov)
    if len(y) < len(x):
        y = np.pad(y, (0, len(x) - len(y)))
    return y[:len(x)]


def _lowpass(x, sr, cutoff):
    from scipy.signal import butter, filtfilt
    b, a = butter(8, cutoff / (sr / 2), btype="low")
    return filtfilt(b, a, x)


def generate_utterance(label, duration=3.0, sr=SR, rng=None):
    """
    Generate one utterance.
      label: 'bonafide' or 'spoof'
    Returns float32 waveform normalised to ~0.9 peak.
    """
    if rng is None:
        rng = np.random.default_rng()
    n = int(duration * sr)
    spoof = (label == "spoof")

    # ---- F0 contour: speaker base pitch + declination + micro-prosody -------
    base_f0 = rng.uniform(95, 135) if rng.random() < 0.5 else rng.uniform(175, 230)
    t = np.linspace(0, duration, n)
    declination = np.linspace(1.06, 0.93, n)
    n_sway = rng.integers(2, 5)
    sway = np.zeros(n)
    for _ in range(n_sway):
        sway += rng.uniform(0.02, 0.06) * np.sin(
            2 * np.pi * rng.uniform(0.4, 1.6) * t + rng.uniform(0, 2 * np.pi))
    f0 = base_f0 * declination * (1.0 + sway)

    if spoof:
        # Modern neural TTS models prosody well, so we only mildly regularise
        # F0 and retain most micro-variation. This keeps the task realistically
        # hard rather than trivially separable.
        from scipy.ndimage import uniform_filter1d
        f0 = uniform_filter1d(f0, size=int(0.05 * sr))
        jitter, shimmer = 0.009, 0.035
    else:
        jitter, shimmer = 0.012, 0.045

    # ---- Excitation ---------------------------------------------------------
    # Modern neural vocoders reproduce glottal waveform shape well, so both
    # classes share the same excitation model. The spoof signature comes
    # from downstream reconstruction artefacts, not a buzzy pulse train.
    exc = _glottal_pulse_train(f0, sr, jitter, shimmer, rng, buzzy=False)

    # Aspiration / breath noise
    noise = rng.normal(0, 1, n)
    noise_gain = 0.026 if spoof else 0.030   # TTS is only slightly "too clean"
    exc = exc + noise_gain * noise

    # ---- Vocal tract: move between vowel targets ----------------------------
    n_seg = rng.integers(4, 8)
    seg_bounds = np.linspace(0, n, n_seg + 1).astype(int)
    targets = [VOWELS[VOWEL_KEYS[rng.integers(0, len(VOWEL_KEYS))]] for _ in range(n_seg + 1)]
    F = np.zeros((4, n))
    for i in range(n_seg):
        s, e = seg_bounds[i], seg_bounds[i + 1]
        for k in range(4):
            F[k, s:e] = np.linspace(targets[i][k], targets[i + 1][k], e - s)
    # smooth coarticulation
    from scipy.ndimage import uniform_filter1d
    for k in range(4):
        F[k] = uniform_filter1d(F[k], size=int(0.03 * sr))

    # Apply formants blockwise so trajectories are honoured
    block = int(0.02 * sr)
    y = np.zeros(n)
    bws_base = np.array([60, 90, 140, 200], dtype=float)
    if spoof:
        bws_base = bws_base * 1.08   # mildly broadened -> subtle over-smoothing
    for s in range(0, n, block):
        e = min(s + block, n)
        freqs = [F[k, (s + e) // 2] for k in range(4)]
        seg = _formant_filter_fast(exc[s:e], freqs, bws_base, sr)
        y[s:e] = seg

    # ---- Energy envelope (syllabic rhythm) ---------------------------------
    syl_rate = rng.uniform(3.0, 5.5)
    env = 0.55 + 0.45 * (0.5 + 0.5 * np.sin(2 * np.pi * syl_rate * t + rng.uniform(0, 6)))
    if not spoof:
        env *= 1.0 + 0.08 * rng.normal(0, 1, n).cumsum() / np.sqrt(n)  # natural drift
    # occasional pauses
    for _ in range(rng.integers(1, 3)):
        p = rng.integers(0, max(1, n - int(0.2 * sr)))
        env[p:p + int(rng.uniform(0.06, 0.18) * sr)] *= 0.05
    y = y * env

    # ---- Lip radiation: first difference, +6 dB/oct ------------------------
    # Standard source-filter synthesis step; restores realistic HF balance.
    y = np.diff(y, prepend=y[0])

    # ---- Spoof-specific post-processing ------------------------------------
    if spoof:
        clean_ref = y.copy()
        y = _smooth_envelope(y, sr, n_cep=rng.integers(30, 48))
        if rng.random() < 0.35:
            y = _griffin_lim_artifact(y, sr, n_iter=int(rng.integers(25, 45)))
        # neural vocoders commonly band-limit
        y = _lowpass(y, sr, cutoff=rng.uniform(7400, 7950))
        # NOTE: gross spectral-tilt differences are removed downstream by
        # cepstral mean-variance normalisation in features.py, which is
        # standard practice in ASVspoof countermeasures. This forces the
        # detector onto fine-structure artefacts rather than global tilt.
    else:
        # natural recordings carry a little room colouration + mic noise
        y = y + 0.0015 * rng.normal(0, 1, n)

    y = np.nan_to_num(y)
    # RMS normalisation (NOT peak): keeps loudness constant across classes so
    # the detector cannot cheat on a gross energy difference. Soft-limit any
    # rare peak rather than rescaling, so RMS stays matched between classes.
    rms = np.sqrt(np.mean(y ** 2)) + 1e-9
    y = y * (0.05 / rms)
    y = np.tanh(y / 0.35) * 0.35      # gentle soft clip, preserves RMS
    return y.astype(np.float32)


def build_corpus(out_dir, n_bonafide=200, n_spoof=200, duration=3.0, sr=SR, seed=0):
    """Generate a labelled corpus on disk. Returns list of (path, label)."""
    import os
    import soundfile as sf
    rng = np.random.default_rng(seed)
    os.makedirs(out_dir, exist_ok=True)
    manifest = []
    for label, count in (("bonafide", n_bonafide), ("spoof", n_spoof)):
        d = os.path.join(out_dir, label)
        os.makedirs(d, exist_ok=True)
        for i in range(count):
            y = generate_utterance(label, duration=duration, sr=sr, rng=rng)
            p = os.path.join(d, f"{label}_{i:04d}.wav")
            sf.write(p, y, sr)
            manifest.append((p, label))
    return manifest


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "data/phase1"
    m = build_corpus(out, n_bonafide=20, n_spoof=20)
    print(f"wrote {len(m)} files to {out}")
