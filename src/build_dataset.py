"""
Phase-1 dataset builder.

Produces:
  data/wav/{train,dev,eval}/{bonafide,spoof}/*.wav   - clean audio
  data/wav/eval_<channel>/...                        - codec-degraded eval sets
  data/wav/train_aug/...                             - codec-augmented training copy
  data/feat/*.npz                                    - cached LFCC features

The eval-set degradation is what lets us measure the base paper's stated
limitation (clean-only evaluation) directly.
"""

import os
import sys
import time
import numpy as np
import soundfile as sf
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(__file__))
from audio_synth import generate_utterance, SR          # noqa: E402
from telephony import degrade, TELEPHONY_CHANNELS, random_channel  # noqa: E402
from features import lfcc, fixed_length, utterance_vector          # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAV = os.path.join(ROOT, "data", "wav")
FEAT = os.path.join(ROOT, "data", "feat")

SPLITS = {"train": (200, 200), "dev": (50, 50), "eval": (75, 75)}
DURATION = 2.5
N_FRAMES = 240


def _gen_one(args):
    split, label, idx, seed = args
    rng = np.random.default_rng(seed)
    y = generate_utterance(label, duration=DURATION, sr=SR, rng=rng)
    d = os.path.join(WAV, split, label)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"{label}_{idx:04d}.wav")
    sf.write(p, y, SR)
    return p


def generate_clean():
    jobs = []
    seed = 1000
    for split, (nb, ns) in SPLITS.items():
        for label, count in (("bonafide", nb), ("spoof", ns)):
            for i in range(count):
                jobs.append((split, label, i, seed))
                seed += 1
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=2) as ex:
        paths = list(ex.map(_gen_one, jobs, chunksize=8))
    print(f"  generated {len(paths)} clean utterances in {time.time()-t0:.1f}s")
    return paths


def _degrade_one(args):
    src, dst, channel, loss = args
    y, sr = sf.read(src, dtype="float32")
    out = degrade(y, sr, profile=channel, loss_rate=loss, target_sr=SR)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    sf.write(dst, out, SR)
    return dst


def build_degraded_eval():
    """Pass the eval set through each telephony channel separately."""
    jobs = []
    for channel in TELEPHONY_CHANNELS:
        for label in ("bonafide", "spoof"):
            sd = os.path.join(WAV, "eval", label)
            for f in sorted(os.listdir(sd)):
                src = os.path.join(sd, f)
                dst = os.path.join(WAV, f"eval_{channel}", label, f)
                jobs.append((src, dst, channel, 0.0))
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=2) as ex:
        out = list(ex.map(_degrade_one, jobs, chunksize=8))
    print(f"  built {len(out)} degraded eval files "
          f"({len(TELEPHONY_CHANNELS)} channels) in {time.time()-t0:.1f}s")


def _augment_one(args):
    src, dst, seed = args
    rng = np.random.default_rng(seed)
    y, sr = sf.read(src, dtype="float32")
    out = random_channel(y, sr, rng=rng, target_sr=SR)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    sf.write(dst, out, SR)
    return dst


def build_augmented_train(n_copies=2):
    """Codec-augmented copies of the training set (our proposed fix)."""
    jobs = []
    seed = 50000
    for c in range(n_copies):
        for label in ("bonafide", "spoof"):
            sd = os.path.join(WAV, "train", label)
            for f in sorted(os.listdir(sd)):
                src = os.path.join(sd, f)
                dst = os.path.join(WAV, f"train_aug{c}", label, f)
                jobs.append((src, dst, seed))
                seed += 1
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=2) as ex:
        out = list(ex.map(_augment_one, jobs, chunksize=8))
    print(f"  built {len(out)} codec-augmented training files in {time.time()-t0:.1f}s")


def _feat_one(args):
    path, = args
    y, sr = sf.read(path, dtype="float32")
    f = fixed_length(lfcc(y, sr=sr), N_FRAMES)
    v = utterance_vector(f)
    return f, v


def extract_split(split_dir):
    """Extract features for one directory tree -> (X_matrix, X_vector, y)."""
    paths, labels = [], []
    for li, label in enumerate(("bonafide", "spoof")):
        d = os.path.join(WAV, split_dir, label)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            paths.append(os.path.join(d, f))
            labels.append(li)          # 0 = bonafide, 1 = spoof
    with ProcessPoolExecutor(max_workers=2) as ex:
        res = list(ex.map(_feat_one, [(p,) for p in paths], chunksize=8))
    X = np.stack([r[0] for r in res])
    V = np.stack([r[1] for r in res])
    y = np.array(labels, dtype=np.int64)
    return X, V, y


def main():
    os.makedirs(FEAT, exist_ok=True)
    print("[1/4] generating clean corpus ...")
    generate_clean()

    print("[2/4] building codec-degraded eval sets ...")
    build_degraded_eval()

    print("[3/4] building codec-augmented training copies ...")
    build_augmented_train(n_copies=2)

    print("[4/4] extracting LFCC features ...")
    dirs = ["train", "dev", "eval", "train_aug0", "train_aug1"] + \
           [f"eval_{c}" for c in TELEPHONY_CHANNELS]
    for d in dirs:
        if not os.path.isdir(os.path.join(WAV, d)):
            continue
        t0 = time.time()
        X, V, y = extract_split(d)
        np.savez_compressed(os.path.join(FEAT, f"{d}.npz"), X=X, V=V, y=y)
        print(f"  {d:16s} X={X.shape} V={V.shape} "
              f"n_bona={int((y==0).sum())} n_spoof={int((y==1).sum())} "
              f"({time.time()-t0:.1f}s)")
    print("done.")


if __name__ == "__main__":
    main()
