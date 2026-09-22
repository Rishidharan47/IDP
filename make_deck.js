const pptxgen = require("pptxgenjs");
const path = require("path");

const FIG = path.join(__dirname, "results", "figures");

// ---- palette -------------------------------------------------------------
const NAVY = "1E2761";
const NAVY_D = "141C45";
const ICE = "CADCFC";
const WHITE = "FFFFFF";
const INK = "16181D";
const MUTED = "5B6472";
const RULE = "E4E8F0";
const AQUA = "1BAF7A";
const ORANGE = "EB6834";
const BLUE = "2A78D6";
const RED = "C62A3C";
const CARD = "F4F7FC";

const HF = "Cambria";   // headings
const BF = "Calibri";   // body

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";            // 13.3 x 7.5
pres.author = "Rishidharan K";
pres.title = "AI Voice-Scam & Deepfake Call Detector - Review II";

const W = 13.3, H = 7.5, M = 0.62;
const COLW = 5.86, COL2 = M + 6.20;   // shared two-column grid

// ---- helpers -------------------------------------------------------------
function titleSlide(s, kicker, title, sub) {
  s.addText(kicker, {
    x: M, y: 0.42, w: 11, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11.5, bold: true, color: BLUE, charSpacing: 1.6,
  });
  s.addText(title, {
    x: M, y: 0.74, w: W - 2 * M, h: 0.72, isTextBox: true, margin: 0,
    fontFace: HF, fontSize: 30, bold: true, color: NAVY,
  });
  if (sub) {
    s.addText(sub, {
      x: M, y: 1.44, w: W - 2 * M, h: 0.42, isTextBox: true, margin: 0,
      fontFace: BF, fontSize: 13.5, color: MUTED,
    });
  }
}

function footer(s, n, onDark) {
  const c = onDark ? ICE : MUTED;
  s.addText("AI Voice-Scam & Deepfake Call Detector  ·  Review II", {
    x: M, y: H - 0.46, w: 7, h: 0.26, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 9.5, color: c,
  });
  s.addText(String(n), {
    x: W - M - 0.6, y: H - 0.46, w: 0.6, h: 0.26, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 9.5, color: c, align: "right",
  });
}

function card(s, x, y, w, h, fill) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, fill: { color: fill || CARD }, rectRadius: 0.09,
    line: { color: fill || CARD, width: 0 },
  });
}

function statCard(s, x, y, w, h, value, label, valColor, fill) {
  card(s, x, y, w, h, fill || CARD);
  s.addText(value, {
    x: x + 0.16, y: y + 0.14, w: w - 0.32, h: h * 0.52, isTextBox: true, margin: 0,
    fontFace: HF, fontSize: 30, bold: true, color: valColor || NAVY, align: "center",
    valign: "middle",
  });
  s.addText(label, {
    x: x + 0.13, y: y + h * 0.60, w: w - 0.26, h: h * 0.34, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 10.5, color: MUTED, align: "center", valign: "top",
  });
}

function numberedRow(s, x, y, w, n, head, body) {
  s.addShape(pres.ShapeType.ellipse, {
    x, y: y + 0.02, w: 0.36, h: 0.36, fill: { color: NAVY },
    line: { color: NAVY, width: 0 },
  });
  s.addText(String(n), {
    x, y: y + 0.02, w: 0.36, h: 0.36, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 13, bold: true, color: WHITE,
    align: "center", valign: "middle",
  });
  s.addText(head, {
    x: x + 0.52, y, w: w - 0.52, h: 0.28, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 13.5, bold: true, color: INK,
  });
  s.addText(body, {
    x: x + 0.52, y: y + 0.28, w: w - 0.52, h: 0.42, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11.5, color: MUTED,
  });
}

let sn = 0;
const next = () => { sn += 1; return sn; };

/* =======================================================================
   1 - TITLE
   ======================================================================= */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addShape(pres.ShapeType.ellipse, {
    x: 9.7, y: -1.5, w: 5.6, h: 5.6, fill: { color: NAVY_D },
    line: { color: NAVY_D, width: 0 },
  });
  s.addText("INNOVATIVE DESIGN PROJECT  ·  REVIEW II", {
    x: M, y: 1.72, w: 10, h: 0.32, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 12, bold: true, color: ICE, charSpacing: 2,
  });
  s.addText("AI Voice-Scam &\nDeepfake Call Detector", {
    x: M, y: 2.18, w: 10.4, h: 1.78, isTextBox: true, margin: 0,
    fontFace: HF, fontSize: 43, bold: true, color: WHITE, lineSpacingMultiple: 1.02,
  });
  s.addText("Real-time detection of synthetic speech under live telephony conditions", {
    x: M, y: 4.08, w: 9.6, h: 0.4, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 15, color: ICE,
  });
  s.addShape(pres.ShapeType.roundRect, {
    x: M, y: 4.82, w: 4.42, h: 0.62, fill: { color: AQUA },
    rectRadius: 0.1, line: { color: AQUA, width: 0 },
  });
  s.addText("Working prototype demonstrated", {
    x: M, y: 4.82, w: 4.42, h: 0.62, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 13, bold: true, color: WHITE,
    align: "center", valign: "middle",
  });
  s.addText("Rishidharan K   ·   BACSE291   ·   AY 2026-27", {
    x: M, y: 6.28, w: 8, h: 0.32, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 12.5, color: ICE,
  });
  s.addNotes(
    "Open by naming the one-line claim: we have a working detector, and we have " +
    "already measured the failure mode that the literature says kills these systems " +
    "in deployment. Everything in this deck is measured, not projected."
  );
}

/* =======================================================================
   2 - PROBLEM / REQUIREMENT UNDERSTANDING
   ======================================================================= */
{
  const s = pres.addSlide();
  titleSlide(s, "THE PROBLEM", "Voice cloning has made vishing cheap, scalable and convincing",
    "Peer-reviewed evidence from our literature survey");

  const stats = [
    ["16.5%", "of people comply with an\nAI-voiced scam call", RED],
    ["36.1%", "comply with a cloned\n“relative in distress” call", RED],
    ["70.3%", "human accuracy at spotting\nan AI caller by voice", ORANGE],
    ["3 sec", "of audio is enough to\nclone a target's voice", NAVY],
  ];
  const cw = 2.78, gap = 0.28;
  stats.forEach((st, i) => {
    statCard(s, M + i * (cw + gap), 2.12, cw, 1.72, st[0], st[1], st[2]);
  });

  card(s, M, 4.14, W - 2 * M, 1.58, CARD);
  s.addText("Why an automated detector is necessary", {
    x: M + 0.3, y: 4.3, w: 11, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 13, bold: true, color: NAVY,
  });
  s.addText([
    { text: "Humans cannot do this reliably. ", options: { bold: true } },
    { text: "Heiding et al. (2026, N = 4,100) found people identify AI callers only 70.3% of the time by voice and 53.0% from text — barely above chance. Familiarity with AI gave no protection at all (54.4% vs 51.2%).", options: {} },
  ], {
    x: M + 0.3, y: 4.64, w: W - 2 * M - 0.6, h: 0.5, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 12, color: INK,
  });
  s.addText([
    { text: "It is already profitable. ", options: { bold: true } },
    { text: "The same study models AI-automated vishing at a positive hourly margin for three of six voice systems, versus a loss for human-operated vishing.", options: {} },
  ], {
    x: M + 0.3, y: 5.14, w: W - 2 * M - 0.6, h: 0.44, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 12, color: INK,
  });

  s.addText("Source: Heiding et al., Expert Systems with Applications, 2026", {
    x: M, y: 5.92, w: 8, h: 0.26, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 9.5, italic: true, color: MUTED,
  });
  footer(s, next());
  s.addNotes(
    "These four numbers are from peer-reviewed sources in our survey, not press coverage. " +
    "The key one for our motivation is 70.3%: humans are poor at this, and being " +
    "familiar with AI does not help. That is the case for an automated detector."
  );
}

/* =======================================================================
   3 - REQUIREMENT ANALYSIS
   ======================================================================= */
{
  const s = pres.addSlide();
  titleSlide(s, "REQUIREMENT ANALYSIS", "What the system must do, and the constraints it must respect");

  card(s, M, 2.05, COLW, 3.55, CARD);
  s.addText("Functional requirements", {
    x: M + 0.28, y: 2.24, w: 5.3, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 13.5, bold: true, color: NAVY,
  });
  s.addText([
    { text: "FR1  Classify call audio as genuine or synthetic", options: { bullet: true, breakLine: true } },
    { text: "FR2  Operate on a live stream, not whole files", options: { bullet: true, breakLine: true } },
    { text: "FR3  Work on codec-compressed telephony audio", options: { bullet: true, breakLine: true } },
    { text: "FR4  Return a confidence, and abstain when unsure", options: { bullet: true, breakLine: true } },
    { text: "FR5  Warn the user discreetly during the call", options: { bullet: true, breakLine: true } },
    { text: "FR6  Generalise to TTS systems not seen in training", options: { bullet: true } },
  ], {
    x: M + 0.28, y: 2.62, w: 5.3, h: 2.8, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11.8, color: INK, paraSpaceAfter: 7,
  });

  card(s, COL2, 2.05, COLW, 3.55, CARD);
  s.addText("Non-functional requirements & constraints", {
    x: COL2 + 0.28, y: 2.24, w: 5.3, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 13.5, bold: true, color: NAVY,
  });
  s.addText([
    { text: "NFR1  Real-time factor < 1.0 (must keep up with the call)", options: { bullet: true, breakLine: true } },
    { text: "NFR2  Low false-alarm rate — wrongly flagging a real caller destroys trust", options: { bullet: true, breakLine: true } },
    { text: "NFR3  Run on commodity hardware, no server GPU", options: { bullet: true, breakLine: true } },
    { text: "NFR4  Privacy: audio processed locally, never uploaded", options: { bullet: true, breakLine: true } },
    { text: "C1  Compute limited to Colab-tier GPU", options: { bullet: true, breakLine: true } },
    { text: "C2  Only open, publicly licensed datasets", options: { bullet: true } },
  ], {
    x: COL2 + 0.28, y: 2.62, w: 5.3, h: 2.8, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11.8, color: INK, paraSpaceAfter: 7,
  });

  card(s, M, 5.82, W - 2 * M, 0.82, NAVY);
  s.addText([
    { text: "Primary stakeholder:  ", options: { bold: true, color: ICE } },
    { text: "elderly and non-technical phone users, the group the literature identifies as most susceptible to family-emergency scams — which is why NFR2 (false alarms) is weighted as heavily as raw accuracy.", options: { color: WHITE } },
  ], {
    x: M + 0.3, y: 5.94, w: W - 2 * M - 0.6, h: 0.6, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 12, valign: "middle",
  });
  footer(s, next());
  s.addNotes(
    "Emphasise NFR2. The base paper's detectors flagged 87.5% of genuine callers as " +
    "fake. A detector that cries wolf is worse than none, because users switch it off. " +
    "That requirement drives our three-way abstention design later in the deck."
  );
}

/* =======================================================================
   4 - LITERATURE SURVEY
   ======================================================================= */
{
  const s = pres.addSlide();
  titleSlide(s, "LITERATURE SURVEY", "30 papers reviewed across seven sub-areas",
    "Each catalogued with dataset, method, reported EER, stated limitations and future work");

  const areas = [
    ["Anti-spoofing benchmarks", "9", "ASVspoof 2015-5, In-the-Wild, MLAAD, ADD, PartialSpoof"],
    ["Detection architectures", "5", "RawNet2, AASIST, wav2vec2, SSL front ends, RawBoost"],
    ["Voice cloning / TTS attacks", "3", "Jia 2018, VALL-E, VALL-E 2"],
    ["Real-time & telephony", "4", "RTCFake, Bhagtani 2024, Shi 2025, Roh 2026"],
    ["Vishing / scam detection", "2", "Heiding 2026, García Martínez-Echevarría 2026"],
    ["Adversarial robustness", "2", "Liu 2019, Wu 2020"],
    ["Surveys & explainability", "5", "Li 2024, Khanjani 2021, Channing 2024, taxonomy survey"],
  ];
  const rowH = 0.46;
  areas.forEach((a, i) => {
    const y = 2.28 + i * (rowH + 0.09);
    s.addShape(pres.ShapeType.roundRect, {
      x: M, y, w: 0.52, h: rowH, fill: { color: NAVY }, rectRadius: 0.06,
      line: { color: NAVY, width: 0 },
    });
    s.addText(a[1], {
      x: M, y, w: 0.52, h: rowH, isTextBox: true, margin: 0,
      fontFace: BF, fontSize: 13, bold: true, color: WHITE,
      align: "center", valign: "middle",
    });
    s.addText(a[0], {
      x: M + 0.68, y, w: 3.3, h: rowH, isTextBox: true, margin: 0,
      fontFace: BF, fontSize: 12.5, bold: true, color: INK, valign: "middle",
    });
    s.addText(a[2], {
      x: M + 4.05, y, w: 8.0, h: rowH, isTextBox: true, margin: 0,
      fontFace: BF, fontSize: 11.5, color: MUTED, valign: "middle",
    });
  });

  s.addText("Coverage spans 2015 to 2026, with four foundational papers retained for grounding.  All 30 PDFs and the metadata tracker are in the project drive.", {
    x: M, y: 6.14, w: W - 2 * M, h: 0.34, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11, italic: true, color: MUTED,
  });
  footer(s, next());
  s.addNotes(
    "If asked how the 30 were chosen: peer-reviewed or arXiv-hosted, prioritising " +
    "2022-2026 with four foundational papers for grounding. Every paper was read to " +
    "the limitations and future-work sections, which is what let us pick the base paper."
  );
}

/* =======================================================================
   5 - BASE PAPER
   ======================================================================= */
{
  const s = pres.addSlide();
  titleSlide(s, "BASE PAPER", "García Martínez-Echevarría et al., Electronics (MDPI) 2026");

  card(s, M, 2.02, 7.2, 3.42, CARD);
  s.addText("“The Generalization Gap: Do Audio Deepfake Detectors Actually Protect Against Modern Vishing?”", {
    x: M + 0.3, y: 2.2, w: 6.6, h: 0.72, isTextBox: true, margin: 0,
    fontFace: HF, fontSize: 14.5, bold: true, color: NAVY,
  });
  s.addText("Electronics, Vol. 15, Issue 13, Article 2846  ·  Universidad Pontificia Comillas + MIT CSAIL  ·  Open access", {
    x: M + 0.3, y: 2.94, w: 6.6, h: 0.32, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 10.5, color: MUTED,
  });
  s.addText([
    { text: "What it does:  ", options: { bold: true } },
    { text: "trains four countermeasures on ASVspoof 2019 (residual CNN on spectrogram / MFCC / CQCC, plus ResNet-18 with OC-Softmax on LFCC) and tests them against nine modern TTS systems.", options: {} },
  ], {
    x: M + 0.3, y: 3.36, w: 6.6, h: 0.78, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11.8, color: INK,
  });
  s.addText([
    { text: "Why we chose it:  ", options: { bold: true } },
    { text: "it is the only 2026 paper in our survey that is a detection paper with a reproducible pipeline, undergraduate-scale compute (4–27 min training runs), and a limitation that maps exactly onto our title.", options: {} },
  ], {
    x: M + 0.3, y: 4.16, w: 6.6, h: 1.0, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11.8, color: INK,
  });

  card(s, M + 7.5, 2.02, 4.56, 3.42, NAVY);
  s.addText("Its headline finding", {
    x: M + 7.78, y: 2.2, w: 4.0, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 12.5, bold: true, color: ICE,
  });
  s.addText("0.92–0.99", {
    x: M + 7.78, y: 2.56, w: 4.0, h: 0.5, isTextBox: true, margin: 0,
    fontFace: HF, fontSize: 26, bold: true, color: WHITE,
  });
  s.addText("AUC on the ASVspoof benchmark", {
    x: M + 7.78, y: 3.04, w: 4.0, h: 0.28, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 10.5, color: ICE,
  });
  s.addText("0.50–0.57", {
    x: M + 7.78, y: 3.46, w: 4.0, h: 0.5, isTextBox: true, margin: 0,
    fontFace: HF, fontSize: 26, bold: true, color: "FF9A8B",
  });
  s.addText("AUC against modern TTS — statistically no better than a coin flip", {
    x: M + 7.78, y: 3.94, w: 4.0, h: 0.5, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 10.5, color: ICE,
  });
  s.addText("87.5%", {
    x: M + 7.78, y: 4.46, w: 4.0, h: 0.4, isTextBox: true, margin: 0,
    fontFace: HF, fontSize: 22, bold: true, color: "FF9A8B",
  });
  s.addText("of genuine callers wrongly flagged as fake (BPCER 0.875)", {
    x: M + 7.78, y: 4.86, w: 4.0, h: 0.44, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 10.5, color: ICE,
  });

  footer(s, next());
  s.addNotes(
    "Be ready for 'why not the other two 2026 papers'. Heiding is a human-subjects " +
    "survey with no model and no released audio. Roh is an attack paper against 7B " +
    "audio LLMs needing roughly 350 GPU-hours. Neither is extendable on our compute."
  );
}

/* =======================================================================
   6 - THE GAP WE ATTACK
   ======================================================================= */
{
  const s = pres.addSlide();
  titleSlide(s, "RESEARCH GAP", "The limitation we selected — in the authors' own words");

  card(s, M, 2.06, W - 2 * M, 1.46, NAVY);
  s.addText("“All experiments were run on clean benchmark audio, and the models were not tested under conditions that characterize real vishing calls — telephone bandwidth and codec compression, background noise, reverberation …”", {
    x: M + 0.42, y: 2.24, w: W - 2 * M - 0.84, h: 0.82, isTextBox: true, margin: 0,
    fontFace: HF, fontSize: 15, italic: true, color: WHITE,
  });
  s.addText("— García Martínez-Echevarría et al. 2026, Section 6 (Limitations)", {
    x: M + 0.42, y: 3.06, w: 9, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 10.5, color: ICE,
  });

  s.addText("Independently confirmed by two other papers in our survey", {
    x: M, y: 3.76, w: 10, h: 0.32, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 13.5, bold: true, color: NAVY,
  });

  numberedRow(s, M, 4.22, 5.9, 1, "Shi et al., EUSIPCO 2025",
    "Detectors “struggle to generalise effectively” once codec compression\nand packet loss are applied.");
  numberedRow(s, M, 5.16, 5.9, 2, "Xue et al., 2025 (RTCFake)",
    "Transmission through real communication platforms degrades\nperformance; platform-invariant features are needed.");

  card(s, COL2, 4.16, COLW, 1.94, CARD);
  s.addText("The gap in one sentence", {
    x: COL2 + 0.28, y: 4.34, w: 5.3, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 12.5, bold: true, color: NAVY,
  });
  s.addText("Every published detector is trained and tested on clean studio audio, but a real scam call arrives through G.711, Opus or GSM at 8 kHz with packet loss — and nobody has measured what that does to detection.", {
    x: COL2 + 0.28, y: 4.7, w: 5.3, h: 1.24, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 12, color: INK,
  });

  footer(s, next());
  s.addNotes(
    "The point to land: we did not invent this gap to justify a project. The base " +
    "paper states it as its own first limitation, and two independent papers confirm " +
    "it. We are the first in our reading to actually measure it end to end."
  );
}

/* =======================================================================
   7 - OBJECTIVES
   ======================================================================= */
{
  const s = pres.addSlide();
  titleSlide(s, "PROBLEM STATEMENT & OBJECTIVES", "Codec-robust deepfake detection for live scam-call screening");

  card(s, M, 2.04, W - 2 * M, 0.96, CARD);
  s.addText([
    { text: "Problem statement:  ", options: { bold: true, color: NAVY } },
    { text: "build a detector that identifies synthetic speech in a live phone call under real telephony channel conditions, and warns the user without an unacceptable false-alarm rate.", options: { color: INK } },
  ], {
    x: M + 0.3, y: 2.22, w: W - 2 * M - 0.6, h: 0.6, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 13, valign: "middle",
  });

  const objs = [
    ["Reproduce the baseline", "Rebuild the base paper's LFCC + OC-Softmax countermeasure and confirm its in-domain performance.", "DONE"],
    ["Quantify the deployment gap", "Measure how far accuracy falls when the same audio passes through real telephony codecs.", "DONE"],
    ["Close the gap", "Introduce codec-realistic augmentation at training time and measure the recovery.", "DONE"],
    ["Control false alarms", "Add a calibrated three-way decision so uncertain calls abstain rather than alarm.", "DONE"],
    ["Validate on real corpora", "Repeat the full protocol on ASVspoof 2019 LA and a modern-TTS evaluation set.", "PHASE 2"],
    ["Add scam-intent analysis", "ASR plus a transcript classifier, fused with the audio branch.", "PHASE 2"],
  ];
  objs.forEach((o, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = M + col * 6.20, y = 3.18 + row * 1.02;
    s.addText(o[0], {
      x, y, w: 4.6, h: 0.28, isTextBox: true, margin: 0,
      fontFace: BF, fontSize: 13, bold: true, color: INK,
    });
    const badgeDone = o[2] === "DONE";
    s.addShape(pres.ShapeType.roundRect, {
      x: x + 4.76, y: y + 0.01, w: 1.1, h: 0.29,
      fill: { color: badgeDone ? AQUA : "F3D34A" }, rectRadius: 0.05,
      line: { color: badgeDone ? AQUA : "F3D34A", width: 0 },
    });
    s.addText(o[2], {
      x: x + 4.76, y: y + 0.01, w: 1.1, h: 0.29, isTextBox: true, margin: 0,
      fontFace: BF, fontSize: 9, bold: true,
      color: badgeDone ? WHITE : NAVY, align: "center", valign: "middle",
    });
    s.addText(o[1], {
      x, y: y + 0.3, w: COLW, h: 0.6, isTextBox: true, margin: 0,
      fontFace: BF, fontSize: 11.3, color: MUTED,
    });
  });

  footer(s, next());
  s.addNotes(
    "Four of six objectives are already complete and measured. That is the basis of " +
    "the roughly 20% implementation claim — not a plan, but working code with results."
  );
}

/* =======================================================================
   8 - ARCHITECTURE
   ======================================================================= */
{
  const s = pres.addSlide();
  titleSlide(s, "SYSTEM DESIGN", "End-to-end architecture");
  s.addImage({ path: path.join(FIG, "00_architecture.png"),
    x: 0.42, y: 1.78, w: 12.46, h: 4.34 });
  s.addText("Phase 1 delivers the complete audio-authenticity path: channel simulation, front end, model, calibration and streaming inference. Phase 2 adds the scam-intent branch and score fusion.", {
    x: M, y: 6.28, w: W - 2 * M, h: 0.4, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11.2, color: MUTED,
  });
  footer(s, next());
  s.addNotes(
    "Walk left to right along the top row, then explain that training and inference " +
    "share the same front end. The two yellow blocks are the only unbuilt parts, and " +
    "their interfaces are already defined — the fusion block takes two scalar scores."
  );
}

/* =======================================================================
   9 - TOOL SELECTION
   ======================================================================= */
{
  const s = pres.addSlide();
  titleSlide(s, "COMPONENT & TOOL SELECTION", "Every choice tied to a technical reason");

  const rows = [
    ["Front-end feature", "LFCC (20 ceps + Δ + ΔΔ)", "Linear filterbank keeps high-frequency resolution where vocoder artefacts sit; best feature in the base paper (3.6% vs 10–15% EER for MFCC/CQCC)."],
    ["Normalisation", "Per-utterance CMVN", "Removes channel and spectral-tilt offsets — essential because codecs change the tilt."],
    ["Model", "ResNet + OC-Softmax", "One-class objective models only genuine speech, so it does not assume the spoof class is well sampled. 324 K parameters — runs on CPU."],
    ["Baseline for comparison", "LFCC-GMM", "The official ASVspoof baseline; gives an honest reference point."],
    ["Channel simulation", "ffmpeg real codecs", "Uses the actual G.711 / G.726 / Opus / MP3 encoders, not a noise approximation."],
    ["Framework", "PyTorch 2.14 (CPU)", "Meets the no-server-GPU constraint; the model trains in minutes."],
  ];
  const hy = 2.08;
  s.addText("Component", { x: M + 0.18, y: hy, w: 2.5, h: 0.3, isTextBox: true, margin: 0, fontFace: BF, fontSize: 10.5, bold: true, color: MUTED, charSpacing: 1 });
  s.addText("Choice", { x: M + 2.78, y: hy, w: 2.6, h: 0.3, isTextBox: true, margin: 0, fontFace: BF, fontSize: 10.5, bold: true, color: MUTED, charSpacing: 1 });
  s.addText("Justification", { x: M + 5.5, y: hy, w: 6.4, h: 0.3, isTextBox: true, margin: 0, fontFace: BF, fontSize: 10.5, bold: true, color: MUTED, charSpacing: 1 });

  rows.forEach((r, i) => {
    const y = 2.46 + i * 0.63;
    if (i % 2 === 0) card(s, M, y - 0.05, W - 2 * M, 0.6, CARD);
    s.addText(r[0], { x: M + 0.18, y, w: 2.5, h: 0.5, isTextBox: true, margin: 0, fontFace: BF, fontSize: 11.2, bold: true, color: INK, valign: "middle" });
    s.addText(r[1], { x: M + 2.78, y, w: 2.6, h: 0.5, isTextBox: true, margin: 0, fontFace: BF, fontSize: 11.2, color: BLUE, bold: true, valign: "middle" });
    s.addText(r[2], { x: M + 5.5, y, w: 6.4, h: 0.5, isTextBox: true, margin: 0, fontFace: BF, fontSize: 10.4, color: MUTED, valign: "middle" });
  });

  footer(s, next());
  s.addNotes(
    "The question to expect is 'why LFCC and not a mel spectrogram'. Answer: the mel " +
    "scale deliberately discards high-frequency resolution to mimic human hearing, but " +
    "that is exactly the band where TTS artefacts live. LFCC keeps it."
  );
}

/* =======================================================================
   10 - INNOVATION
   ======================================================================= */
{
  const s = pres.addSlide();
  titleSlide(s, "INNOVATION", "We replace an approximation with the real thing");

  card(s, M, 2.08, 6.62, 1.66, CARD);
  s.addText("Prior work (RawBoost, Tak et al. 2022)", {
    x: M + 0.28, y: 2.24, w: 6.06, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 12.5, bold: true, color: MUTED,
  });
  s.addText("Simulates channel effects by adding convolutive, impulsive and stationary noise to the waveform. Audio never passes through an actual codec.", {
    x: M + 0.28, y: 2.6, w: 6.06, h: 1.0, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11.5, color: INK,
  });

  card(s, 7.54, 2.08, 5.14, 1.66, AQUA);
  s.addText("Our approach", {
    x: 7.82, y: 2.24, w: 4.6, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 12.5, bold: true, color: WHITE,
  });
  s.addText("Audio is encoded and decoded through the genuine ffmpeg implementations of the codecs used on real calls, with VoIP packet loss on top.", {
    x: 7.82, y: 2.6, w: 4.6, h: 1.0, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11.5, color: WHITE,
  });

  s.addImage({ path: path.join(FIG, "05_codec_spectra.png"),
    x: M, y: 4.02, w: 6.62, h: 2.45 });

  card(s, 7.54, 4.02, 5.14, 2.45, CARD);
  s.addText("Why it matters", {
    x: 7.82, y: 4.2, w: 4.6, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 12.5, bold: true, color: NAVY,
  });
  s.addText("G.711 — the ordinary landline codec — removes everything above 4 kHz.\n\nThat is precisely the band where TTS and vocoder artefacts concentrate, and precisely why LFCC beats MFCC on clean audio.\n\nThe detector's best evidence is deleted before it ever arrives.", {
    x: 7.82, y: 4.56, w: 4.6, h: 1.8, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11, color: INK,
  });

  footer(s, next());
  s.addNotes(
    "The spectrum plot is the intuition for the whole project. Point at the cliff at " +
    "4 kHz. Everything to the right of it is thrown away by a normal phone call, and " +
    "that is where the detector was looking."
  );
}

/* =======================================================================
   11 - PROTOTYPE STATUS
   ======================================================================= */
{
  const s = pres.addSlide();
  titleSlide(s, "PROTOTYPE — INITIAL MODULE DEVELOPMENT", "Seven modules implemented and running");

  const mods = [
    ["audio_synth.py", "Phase-1 corpus generator", "650 utterances"],
    ["telephony.py", "Codec + packet-loss pipeline", "11 codecs verified"],
    ["features.py", "LFCC front end with CMVN", "60-dim × 240 frames"],
    ["models.py", "OC-ResNet + GMM baseline", "324 K parameters"],
    ["train.py", "Three-condition experiment driver", "4 models trained"],
    ["evaluate.py", "EER / AUC / APCER / BPCER", "7 conditions scored"],
    ["realtime_demo.py", "Streaming sliding-window scorer", "23 ms per window"],
  ];
  mods.forEach((m, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = M + col * 6.20, y = 2.16 + row * 0.72;
    card(s, x, y, COLW, 0.62, CARD);
    s.addShape(pres.ShapeType.ellipse, {
      x: x + 0.18, y: y + 0.17, w: 0.28, h: 0.28,
      fill: { color: AQUA }, line: { color: AQUA, width: 0 },
    });
    s.addText("✓", {
      x: x + 0.18, y: y + 0.17, w: 0.28, h: 0.28, isTextBox: true, margin: 0,
      fontFace: BF, fontSize: 11, bold: true, color: WHITE,
      align: "center", valign: "middle",
    });
    s.addText(m[0], {
      x: x + 0.58, y: y + 0.06, w: 2.3, h: 0.26, isTextBox: true, margin: 0,
      fontFace: "Courier New", fontSize: 10.5, bold: true, color: NAVY,
    });
    s.addText(m[1], {
      x: x + 0.58, y: y + 0.31, w: 3.5, h: 0.26, isTextBox: true, margin: 0,
      fontFace: BF, fontSize: 10.5, color: MUTED,
    });
    s.addText(m[2], {
      x: x + 3.9, y: y + 0.17, w: 1.68, h: 0.3, isTextBox: true, margin: 0,
      fontFace: BF, fontSize: 10.5, bold: true, color: BLUE,
      align: "right", valign: "middle",
    });
  });

  const stats = [["2,350", "audio files generated"], ["4", "models trained"],
                 ["7", "test conditions"], ["~1,400", "lines of Python"]];
  stats.forEach((st, i) => {
    statCard(s, M + i * 3.165, 5.30, 2.905, 1.06, st[0], st[1], NAVY, CARD);
  });

  footer(s, next());
  s.addNotes(
    "This slide answers the rubric's 'evidence of approximately 20% implementation'. " +
    "Every module is runnable today; I can execute any of them live if the panel asks."
  );
}

/* =======================================================================
   12 - HEADLINE RESULT
   ======================================================================= */
{
  const s = pres.addSlide();
  titleSlide(s, "RESULT 1", "We measured the gap — and then closed most of it");
  s.addImage({ path: path.join(FIG, "01_headline_gap.png"),
    x: 0.74, y: 1.82, w: 7.3, h: 4.45 });

  card(s, 8.38, 1.9, 4.3, 1.32, NAVY);
  s.addText("42.9%", {
    x: 8.62, y: 2.0, w: 3.9, h: 0.52, isTextBox: true, margin: 0,
    fontFace: HF, fontSize: 27, bold: true, color: "FF9A8B",
  });
  s.addText("EER once real telephony codecs are applied — near random guessing", {
    x: 8.62, y: 2.52, w: 3.9, h: 0.58, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11, color: ICE,
  });

  card(s, 8.38, 3.36, 4.3, 1.32, AQUA);
  s.addText("16.7%", {
    x: 8.62, y: 3.46, w: 3.9, h: 0.52, isTextBox: true, margin: 0,
    fontFace: HF, fontSize: 27, bold: true, color: WHITE,
  });
  s.addText("EER after codec-realistic augmentation — a 61% relative improvement", {
    x: 8.62, y: 3.98, w: 3.9, h: 0.58, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11, color: WHITE,
  });

  card(s, 8.38, 4.82, 4.3, 1.45, CARD);
  s.addText("AUC tells the same story", {
    x: 8.62, y: 4.94, w: 3.9, h: 0.28, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11.5, bold: true, color: NAVY,
  });
  s.addText("1.000 on clean audio  →  0.596 through codecs  →  0.906 with augmentation.\n\nThe collapse mirrors the base paper's 0.99 → 0.55.", {
    x: 8.62, y: 5.24, w: 3.9, h: 0.92, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 10.8, color: INK,
  });

  footer(s, next());
  s.addNotes(
    "Do not oversell the 0.0% clean figure — say plainly that the Phase-1 corpus is " +
    "synthetic and separable, which is exactly why the 42.9% matters: the same model " +
    "that is perfect in the lab is useless on a phone line. The trend is the finding."
  );
}

/* =======================================================================
   13 - RESULT 2
   ======================================================================= */
{
  const s = pres.addSlide();
  titleSlide(s, "RESULT 2", "Consistent across channels, and an honest negative result");
  s.addImage({ path: path.join(FIG, "02_per_channel.png"),
    x: M, y: 1.82, w: 7.30, h: 3.62 });
  s.addImage({ path: path.join(FIG, "03_roc.png"),
    x: 8.22, y: 1.82, w: 4.46, h: 3.62 });

  card(s, M, 5.66, W - 2 * M, 1.06, CARD);
  s.addText([
    { text: "An honest negative result:  ", options: { bold: true, color: RED } },
    { text: "the same augmentation applied to the LFCC-GMM baseline made it worse (36.2% → 41.4% EER). A 16-component diagonal GMM lacks the capacity to model the far more heterogeneous augmented distribution — so the gain is specific to the neural model, not a free lunch. We report it rather than hide it.", options: { color: INK } },
  ], {
    x: M + 0.3, y: 5.8, w: W - 2 * M - 0.6, h: 0.8, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11.5,
  });

  footer(s, next());
  s.addNotes(
    "Lead with the negative result if the panel seems sceptical — it demonstrates we " +
    "are reporting what we measured. Also flag the Opus 24k case: augmentation costs " +
    "a little accuracy on the cleanest channel, the classic robustness trade-off."
  );
}

/* =======================================================================
   14 - LIVE DEMO
   ======================================================================= */
{
  const s = pres.addSlide();
  titleSlide(s, "LIVE DEMONSTRATION", "Streaming detection on a simulated scam call");

  card(s, M, 2.04, 7.5, 3.9, NAVY_D);
  s.addText("$  python src/realtime_demo.py data/demo/call_switch.wav", {
    x: M + 0.28, y: 2.2, w: 7.0, h: 0.28, isTextBox: true, margin: 0,
    fontFace: "Courier New", fontSize: 10.5, color: AQUA,
  });
  const lines = [
    ["  band: genuine <= -0.995 < uncertain < -0.820 <= synthetic", "8FA0C0"],
    ["  t=  0.0s   OK  GENUINE      score -0.999", ICE],
    ["  t=  2.5s   OK  GENUINE      score -0.999", ICE],
    ["  t=  5.5s   OK  GENUINE      score -0.998", ICE],
    ["  ── attacker swaps in a cloned voice ──", "F3D34A"],
    ["  t=  6.0s   !!  SYNTHETIC    score -0.351", "FF9A8B"],
    ["  t=  7.0s   !!  SYNTHETIC    score +0.901", "FF9A8B"],
    ["  t= 10.0s   ??  UNCERTAIN    score -0.946", "F3D34A"],
    ["  t= 12.5s   !!  SYNTHETIC    score -0.341", "FF9A8B"],
    ["", ICE],
    ["  final verdict: SYNTHETIC", WHITE],
    ["  23.5 ms/window   real-time factor 0.047", AQUA],
  ];
  lines.forEach((l, i) => {
    s.addText(l[0], {
      x: M + 0.28, y: 2.58 + i * 0.29, w: 7.0, h: 0.27, isTextBox: true, margin: 0,
      fontFace: "Courier New", fontSize: 10.5, color: l[1],
      bold: i === 9,
    });
  });

  card(s, M + 7.8, 2.04, 4.28, 1.86, CARD);
  s.addText("What this shows", {
    x: M + 8.06, y: 2.2, w: 3.76, h: 0.28, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 12.5, bold: true, color: NAVY,
  });
  s.addText("The detector tracks a call that begins with a real human and switches to a cloned voice mid-conversation, and flips its verdict within one window of the swap.", {
    x: M + 8.06, y: 2.54, w: 3.76, h: 1.24, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11.2, color: INK,
  });

  card(s, M + 7.8, 4.1, 4.28, 1.84, CARD);
  s.addText("Three-way output", {
    x: M + 8.06, y: 4.26, w: 3.76, h: 0.28, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 12.5, bold: true, color: NAVY,
  });
  s.addText("Thresholds are calibrated on the development set, not hand-picked. Between the two bounds the system abstains rather than alarming — directly addressing the base paper's 87.5% false-alarm problem.", {
    x: M + 8.06, y: 4.6, w: 3.76, h: 1.22, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11.2, color: INK,
  });

  s.addText("Real-time factor 0.047 — roughly 21× faster than the audio arrives, on CPU alone, with no GPU required.", {
    x: M, y: 6.12, w: W - 2 * M, h: 0.34, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11.5, italic: true, color: MUTED,
  });

  footer(s, next());
  s.addNotes(
    "Offer to run this live — it takes about ten seconds. The UNCERTAIN window at " +
    "10.0s is worth pointing out: that is the abstention band working as designed on " +
    "a genuinely ambiguous segment, not a bug."
  );
}

/* =======================================================================
   15 - FEASIBILITY & RISK
   ======================================================================= */
{
  const s = pres.addSlide();
  titleSlide(s, "FEASIBILITY & RISK", "Why this finishes on time");

  const fe = [
    ["Compute", "Model trains in 4 minutes on CPU; 324 K parameters. The base paper's own runs took 4–27 minutes.", AQUA, "LOW RISK"],
    ["Data", "ASVspoof 2019 LA is public and free. Phase-1 pipeline swaps corpora by changing one path.", AQUA, "LOW RISK"],
    ["Tooling", "ffmpeg, PyTorch, scikit-learn — all open source, already working.", AQUA, "LOW RISK"],
    ["No released code", "Base paper publishes no repository. Mitigated: we have already reimplemented it from the two upstream papers.", "F3D34A", "MANAGED"],
    ["Modern-TTS eval set", "SONAR access unconfirmed. Fallback: generate our own set with open TTS over public speech.", "F3D34A", "MANAGED"],
  ];
  fe.forEach((f, i) => {
    const y = 2.12 + i * 0.84;
    card(s, M, y, W - 2 * M, 0.72, CARD);
    s.addText(f[0], {
      x: M + 0.28, y: y + 0.06, w: 2.4, h: 0.6, isTextBox: true, margin: 0,
      fontFace: BF, fontSize: 12.5, bold: true, color: INK, valign: "middle",
    });
    s.addText(f[1], {
      x: M + 2.8, y: y + 0.06, w: 7.6, h: 0.6, isTextBox: true, margin: 0,
      fontFace: BF, fontSize: 11.2, color: MUTED, valign: "middle",
    });
    s.addShape(pres.ShapeType.roundRect, {
      x: M + 10.6, y: y + 0.19, w: 1.4, h: 0.34,
      fill: { color: f[2] }, rectRadius: 0.06, line: { color: f[2], width: 0 },
    });
    s.addText(f[3], {
      x: M + 10.6, y: y + 0.19, w: 1.4, h: 0.34, isTextBox: true, margin: 0,
      fontFace: BF, fontSize: 8.5, bold: true,
      color: f[2] === AQUA ? WHITE : NAVY, align: "center", valign: "middle",
    });
  });

  s.addText("The highest-risk item — reimplementing a paper with no released code — is already behind us, not ahead of us.", {
    x: M, y: 6.42, w: W - 2 * M, h: 0.34, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11.8, italic: true, color: NAVY,
  });

  footer(s, next());
  s.addNotes(
    "If asked about the biggest threat to completion, say the modern-TTS evaluation " +
    "set. We have a concrete fallback: generate our own with open TTS models over " +
    "LibriSpeech, drawing real and fake from the same corpus to avoid a domain confound."
  );
}

/* =======================================================================
   16 - PLAN
   ======================================================================= */
{
  const s = pres.addSlide();
  titleSlide(s, "WORK PLAN", "From here to final review");

  const phases = [
    ["Phase 1", "Complete", "Literature survey, base paper selection, full pipeline, codec augmentation, calibrated streaming detector, measured results.", AQUA, "100%"],
    ["Phase 2", "Next 4 weeks", "Port the pipeline to ASVspoof 2019 LA. Retrain and re-measure the same three conditions on real speech.", BLUE, "0%"],
    ["Phase 3", "Weeks 5–8", "Swap LFCC for a frozen wav2vec2 / WavLM front end. Add the ASR + scam-intent branch and score fusion.", BLUE, "0%"],
    ["Phase 4", "Weeks 9–12", "Cross-corpus evaluation against modern TTS, user-facing alert UI, final report and paper draft.", MUTED, "0%"],
  ];
  phases.forEach((p, i) => {
    const y = 2.1 + i * 1.08;
    card(s, M, y, W - 2 * M, 0.94, CARD);
    s.addShape(pres.ShapeType.roundRect, {
      x: M + 0.22, y: y + 0.19, w: 1.36, h: 0.56,
      fill: { color: p[3] }, rectRadius: 0.07, line: { color: p[3], width: 0 },
    });
    s.addText(p[0], {
      x: M + 0.22, y: y + 0.19, w: 1.36, h: 0.56, isTextBox: true, margin: 0,
      fontFace: BF, fontSize: 12.5, bold: true, color: WHITE,
      align: "center", valign: "middle",
    });
    s.addText(p[1], {
      x: M + 1.78, y: y + 0.14, w: 2.4, h: 0.3, isTextBox: true, margin: 0,
      fontFace: BF, fontSize: 12, bold: true, color: INK,
    });
    s.addText(p[2], {
      x: M + 1.78, y: y + 0.44, w: 9.2, h: 0.44, isTextBox: true, margin: 0,
      fontFace: BF, fontSize: 11, color: MUTED,
    });
    s.addText(p[4], {
      x: W - M - 1.2, y: y + 0.14, w: 0.95, h: 0.3, isTextBox: true, margin: 0,
      fontFace: HF, fontSize: 15, bold: true, color: p[3], align: "right",
    });
  });

  footer(s, next());
  s.addNotes(
    "Phase 2 is deliberately a port rather than new science: the pipeline is written " +
    "so that swapping the corpus is a path change. That is why four weeks is realistic."
  );
}

/* =======================================================================
   17 - SUMMARY
   ======================================================================= */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("SUMMARY", {
    x: M, y: 0.72, w: 10, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 12, bold: true, color: ICE, charSpacing: 2,
  });
  s.addText("What we are claiming at this review", {
    x: M, y: 1.08, w: 11, h: 0.62, isTextBox: true, margin: 0,
    fontFace: HF, fontSize: 30, bold: true, color: WHITE,
  });

  const pts = [
    ["We chose a base paper by reading 30 papers to their limitations sections", "and selected the one whose stated gap matches our title exactly."],
    ["We reproduced the gap it admits to, and measured it", "EER rises from 0.0% to 42.9% and AUC falls to 0.596 once real telephony codecs are applied."],
    ["We proposed a fix and showed it works", "Codec-realistic augmentation recovers EER to 16.7% — a 61% relative improvement."],
    ["We built it as a real-time system, not an offline script", "23 ms per window, real-time factor 0.047, with a calibrated three-way decision."],
  ];
  pts.forEach((p, i) => {
    const y = 2.06 + i * 1.02;
    s.addShape(pres.ShapeType.ellipse, {
      x: M, y: y + 0.03, w: 0.38, h: 0.38,
      fill: { color: AQUA }, line: { color: AQUA, width: 0 },
    });
    s.addText(String(i + 1), {
      x: M, y: y + 0.03, w: 0.38, h: 0.38, isTextBox: true, margin: 0,
      fontFace: BF, fontSize: 13, bold: true, color: WHITE,
      align: "center", valign: "middle",
    });
    s.addText(p[0], {
      x: M + 0.56, y, w: 11.2, h: 0.32, isTextBox: true, margin: 0,
      fontFace: BF, fontSize: 14, bold: true, color: WHITE,
    });
    s.addText(p[1], {
      x: M + 0.56, y: y + 0.34, w: 11.2, h: 0.5, isTextBox: true, margin: 0,
      fontFace: BF, fontSize: 12, color: ICE,
    });
  });

  s.addText("All figures in this deck were produced by our own code from our own experiments.", {
    x: M, y: 6.34, w: 11, h: 0.34, isTextBox: true, margin: 0,
    fontFace: BF, fontSize: 11.5, italic: true, color: ICE,
  });
  footer(s, next(), true);
  s.addNotes(
    "Close on point 4. The distinction between an offline classifier and a real-time " +
    "streaming system is the one most projects skip, and it is the one that makes this " +
    "a product rather than an experiment."
  );
}

pres.writeFile({ fileName: path.join(__dirname, "IDP_Review_II_Voice_Scam_Detector.pptx") })
  .then(f => console.log("wrote", f));
