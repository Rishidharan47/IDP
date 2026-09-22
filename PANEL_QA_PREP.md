# Panel Q&A prep — Review II

Rubric is 20 marks across 7 parameters. The prototype is only **3 marks**.
Design, architecture, tool justification, innovation, planning and your
individual response carry the other **17** — so do not spend the whole slot on
the demo.

---

## The four numbers to have on the tip of your tongue

| | |
|---|---|
| **42.9%** | EER once real telephony codecs are applied (AUC 0.596 — near chance) |
| **16.7%** | EER after codec-realistic augmentation (AUC 0.906) |
| **61%** | relative improvement from the contribution |
| **23 ms** | per window, real-time factor 0.047, CPU only |

---

## Likely questions, with answers

**"Why this base paper and not the other two 2026 papers?"**
Heiding et al. is a 4,100-person survey study — no model, no dataset, no
trainable pipeline, and the scam audio is deliberately withheld for dual-use
reasons. Roh et al. is an *attack* paper against 7B-parameter audio LLMs needing
roughly 350 GPU-hours; the word "deepfake" appears once, in a reference title.
García Martínez-Echevarría is the only one of the three that is a detection
paper, with a reproducible pipeline and 4–27 minute training runs.

**"Your clean EER is 0.0% — isn't that suspicious?"**
Yes, and I'll say so directly. The Phase-1 corpus is synthetic and the neural
model saturates on it. That is exactly *why* the 42.9% matters: the same model
that looks perfect in the lab is useless on a phone line. The finding is the
trend across conditions, not the absolute number. Phase 2 repeats this on
ASVspoof 2019 LA.

**"Why is the data synthetic? Why not use ASVspoof now?"**
Build-machine constraint, not a design choice. The loader is written so the
corpus swaps by changing one path. Everything downstream — codec pipeline,
features, model, evaluation — is corpus-independent and already tested.

**"Why LFCC and not a mel spectrogram / MFCC?"**
The mel scale deliberately discards high-frequency resolution to mimic human
hearing, but that is precisely the band where vocoder and TTS artefacts
concentrate. LFCC uses a linear filterbank and keeps it. In the base paper LFCC
reached 3.6% EER against 10.5–14.7% for spectrogram, MFCC and CQCC.

**"What exactly is novel? Augmentation isn't new."**
Correct — augmentation is not new. RawBoost (Tak et al. 2022) *approximates* a
channel by adding convolutive, impulsive and stationary noise; the audio never
passes through a codec. We use the genuine ffmpeg encoder/decoder for the codecs
real calls actually use, plus packet loss. Replacing the approximation with the
real thing is the contribution, and the 61% recovery is the evidence.

**"Why did the GMM get worse with augmentation?"**
A 16-component diagonal-covariance GMM does not have the capacity to model a
distribution that now spans six channels plus packet loss and noise. Adding
variance without adding capacity hurts. It is a real result and we report it —
it shows the gain belongs to the neural model, not to augmentation per se.

**"Opus 24k got worse too."**
Yes — 3% to 8%. That is the standard robustness/accuracy trade-off: the model
gives up a little on the cleanest channel to gain a lot on the five degraded
ones. Pooled across channels it is still a 26-point improvement.

**"How is this real-time?"**
2.5-second window, 0.5-second hop, 23 ms of compute per window on CPU. Real-time
factor 0.047, roughly 21× faster than the audio arrives. The model is 324 K
parameters — small enough for a phone.

**"What about false alarms?"**
This is the requirement we weighted most heavily. The base paper's detectors
flagged 87.5% of *genuine* callers as fake, which makes a binary alarm useless —
users switch it off. We output three states with a band calibrated on the
development set: below the lower bound genuine, above the upper bound synthetic,
in between the system abstains rather than alarming.

**"What's the biggest risk to finishing?"**
Getting a modern-TTS evaluation set. SONAR access is unconfirmed. Fallback:
generate our own with open TTS models over public speech, drawing real and fake
from the same source corpus so we don't introduce the domain confound the base
paper itself warns about.

**"What have you personally done?"**
Point at the module map: seven Python modules, ~1,400 lines, all runnable now.
Offer to execute any one of them live.

---

## Demo script (about 90 seconds)

```bash
python src/telephony.py                                  # 11 codecs verified working
python src/realtime_demo.py data/demo/call_switch.wav    # the money demo
```

The second one is a call that starts with a real human and switches to a cloned
voice at 7.5 s. Narrate: verdict flips within one window of the swap; the
UNCERTAIN window at t=10.0 s is the abstention band working as designed on a
genuinely ambiguous segment — not a bug.

Backup if the laptop misbehaves: slide 14 has the captured transcript.

---

## What NOT to claim

- Do not claim state-of-the-art accuracy. Claim a *measured gap* and a *measured
  recovery*.
- Do not present the synthetic corpus as real speech.
- Do not say the system is finished. Four of six objectives are done; two are
  scheduled and their interfaces are already defined.
