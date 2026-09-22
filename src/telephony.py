"""
Telephony channel degradation pipeline.

This module is the core novelty of the project. The base paper
(Garcia Martinez-Echevarria et al., Electronics 2026) states as its first
limitation:

    "All experiments were run on clean benchmark audio, and the models were
     not tested under conditions that characterize real vishing calls
     (telephone bandwidth and codec compression, background noise,
     reverberation, or emotional and conversational speech)."

We close that gap by passing audio through the codecs actually used on real
voice calls, using ffmpeg's real encoder/decoder implementations rather than
a synthetic noise approximation:

    G.711 mu-law   - PSTN / landline                       (64 kbps, 8 kHz)
    GSM 06.10      - legacy cellular                       (13 kbps, 8 kHz)
    G.726 ADPCM    - DECT / cordless                       (16-40 kbps, 8 kHz)
    Opus           - WhatsApp, Signal, Zoom, WebRTC VoIP    (6-64 kbps)
    MP3 / AAC      - recorded-call storage and forwarding

Plus packet-loss simulation, which VoIP suffers and codecs alone do not model.
"""

import os
import subprocess
import tempfile
import numpy as np
import soundfile as sf

# name -> (ffmpeg codec args, container ext, sample rate)
CODEC_PROFILES = {
    "g711_ulaw": (["-acodec", "pcm_mulaw", "-ar", "8000"], "wav", 8000),
    "g711_alaw": (["-acodec", "pcm_alaw", "-ar", "8000"], "wav", 8000),
    "gsm":       (["-acodec", "libgsm", "-ar", "8000", "-ab", "13k"], "wav", 8000),
    "g726_16k":  (["-acodec", "g726", "-ar", "8000", "-ab", "16k"], "wav", 8000),
    "g726_32k":  (["-acodec", "g726", "-ar", "8000", "-ab", "32k"], "wav", 8000),
    "opus_6k":   (["-acodec", "libopus", "-ar", "16000", "-ab", "6k"], "ogg", 16000),
    "opus_12k":  (["-acodec", "libopus", "-ar", "16000", "-ab", "12k"], "ogg", 16000),
    "opus_24k":  (["-acodec", "libopus", "-ar", "16000", "-ab", "24k"], "ogg", 16000),
    "opus_64k":  (["-acodec", "libopus", "-ar", "16000", "-ab", "64k"], "ogg", 16000),
    "mp3_32k":   (["-acodec", "libmp3lame", "-ar", "16000", "-ab", "32k"], "mp3", 16000),
    "mp3_64k":   (["-acodec", "libmp3lame", "-ar", "16000", "-ab", "64k"], "mp3", 16000),
    "aac_32k":   (["-acodec", "aac", "-ar", "16000", "-ab", "32k"], "m4a", 16000),
}

# Realistic deployment channels for evaluation (verified working in this build)
TELEPHONY_CHANNELS = ["g711_ulaw", "g726_32k", "g726_16k",
                      "opus_12k", "opus_24k", "mp3_32k"]


def _run(cmd):
    return subprocess.run(cmd, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL, check=False)


def apply_codec(y, sr, profile, target_sr=16000):
    """
    Encode/decode `y` through a real codec and return audio at `target_sr`.
    Falls back to the input signal if ffmpeg is unavailable for that codec.
    """
    if profile not in CODEC_PROFILES:
        raise ValueError(f"unknown codec profile: {profile}")
    args, ext, _csr = CODEC_PROFILES[profile]

    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "in.wav")
        enc = os.path.join(td, f"enc.{ext}")
        dec = os.path.join(td, "out.wav")
        sf.write(src, y, sr)

        r1 = _run(["ffmpeg", "-y", "-i", src] + args + [enc])
        if r1.returncode != 0 or not os.path.exists(enc):
            return y.astype(np.float32)

        r2 = _run(["ffmpeg", "-y", "-i", enc, "-ar", str(target_sr),
                   "-ac", "1", "-acodec", "pcm_s16le", dec])
        if r2.returncode != 0 or not os.path.exists(dec):
            return y.astype(np.float32)

        out, _ = sf.read(dec, dtype="float32")
        if out.ndim > 1:
            out = out.mean(axis=1)

    # length-match to the input
    if len(out) < len(y):
        out = np.pad(out, (0, len(y) - len(out)))
    else:
        out = out[:len(y)]
    return out.astype(np.float32)


def apply_packet_loss(y, sr, loss_rate=0.03, packet_ms=20, conceal="zero"):
    """
    Simulate VoIP packet loss with optional concealment.
      conceal='zero'   - drop the packet (worst case)
      conceal='repeat' - repeat previous packet (typical PLC behaviour)
    """
    if loss_rate <= 0:
        return y
    plen = max(1, int(sr * packet_ms / 1000))
    out = y.copy()
    n_pkt = int(np.ceil(len(y) / plen))
    rng = np.random.default_rng()
    prev = np.zeros(plen, dtype=y.dtype)
    for i in range(n_pkt):
        s, e = i * plen, min((i + 1) * plen, len(y))
        if rng.random() < loss_rate:
            if conceal == "repeat":
                out[s:e] = prev[:e - s] * 0.6
            else:
                out[s:e] = 0.0
        else:
            prev = y[s:e]
            if len(prev) < plen:
                prev = np.pad(prev, (0, plen - len(prev)))
    return out


def add_noise(y, snr_db):
    """Add white noise at a specified SNR."""
    p_sig = np.mean(y ** 2) + 1e-12
    p_noise = p_sig / (10 ** (snr_db / 10.0))
    return (y + np.sqrt(p_noise) * np.random.normal(0, 1, len(y))).astype(np.float32)


def degrade(y, sr, profile=None, loss_rate=0.0, snr_db=None, target_sr=16000):
    """Full channel simulation: codec -> packet loss -> ambient noise."""
    out = y
    if profile:
        out = apply_codec(out, sr, profile, target_sr=target_sr)
    if loss_rate > 0:
        out = apply_packet_loss(out, target_sr, loss_rate)
    if snr_db is not None:
        out = add_noise(out, snr_db)
    peak = np.max(np.abs(out)) + 1e-9
    return (0.9 * out / peak).astype(np.float32)


def random_channel(y, sr, rng=None, target_sr=16000):
    """
    Randomised channel for TRAINING-TIME AUGMENTATION.
    This is the mechanism we propose to close the base paper's robustness gap.
    """
    if rng is None:
        rng = np.random.default_rng()
    # 20% of the time leave audio clean so the model keeps clean-condition skill
    if rng.random() < 0.20:
        return y.astype(np.float32)
    profile = TELEPHONY_CHANNELS[rng.integers(0, len(TELEPHONY_CHANNELS))]
    loss = float(rng.choice([0.0, 0.0, 0.01, 0.03, 0.05]))
    # additive noise on ~40% of augmented samples
    snr = None
    if rng.random() < 0.40:
        snr = float(rng.choice([30.0, 25.0, 20.0]))
    return degrade(y, sr, profile=profile, loss_rate=loss, snr_db=snr, target_sr=target_sr)


def available_codecs():
    """Probe which codec profiles actually work in this ffmpeg build."""
    sr = 16000
    test = (0.3 * np.sin(2 * np.pi * 300 * np.arange(sr) / sr)).astype(np.float32)
    ok = {}
    for name in CODEC_PROFILES:
        try:
            out = apply_codec(test, sr, name)
            changed = not np.allclose(out, test, atol=1e-6)
            ok[name] = bool(changed and np.any(np.abs(out) > 1e-6))
        except Exception:
            ok[name] = False
    return ok


if __name__ == "__main__":
    print("Probing ffmpeg codec availability...")
    for k, v in available_codecs().items():
        print(f"  {k:12s} {'OK' if v else 'UNAVAILABLE'}")
