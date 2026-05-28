# Citation Links

One-stop lookup for every paper cited in this repo's docs. Every entry has either a public URL (arxiv / DOI / publisher) or a local PDF reference. **Never reference a paper without one of these.**

## Anchor papers (the three 2025–2026 benchmarks AERead integrates)

| Paper | Public link | Local PDF |
|---|---|---|
| Zhang et al. 2026 — TERMS-Bench (paper) | https://arxiv.org/abs/2605.13909 | — |
| Zhang et al. 2026 — TERMS-Bench (live leaderboard) | https://terms-bench.github.io | — |
| Fish, Gonczarowski et al. 2026 — EconEvals | https://arxiv.org/abs/2503.18825 | — |
| Andrews 2026 — Revealed Rationality | (MIT/NBER; no arxiv) | [`pdfs/andrews_2026_revealed_rationality.pdf`](pdfs/andrews_2026_revealed_rationality.pdf) |

## 5-axis prior-art anchors

| Paper | Public link | Local PDF |
|---|---|---|
| **Axis 1** — Zhang et al. 2026 TERMS-Bench (same as above) | https://arxiv.org/abs/2605.13909 | — |
| **Axis 2** — Andrews 2026 (same as above) | — | [`pdfs/andrews_2026_revealed_rationality.pdf`](pdfs/andrews_2026_revealed_rationality.pdf) |
| **Axis 2** — Betz & Richardson 2023 — Probabilistic coherence | https://doi.org/10.1371/journal.pone.0281372 | — |
| **Axis 3** — Mazeika et al. 2025 — Utility Engineering | https://arxiv.org/abs/2502.08640 | — |
| **Axis 3** — Guo et al. 2017 — On Calibration of Modern NNs | https://arxiv.org/abs/1706.04599 | — |
| **Axis 3** — Gneiting & Raftery 2007 — Strictly proper scoring rules | (JASA; no arxiv) | [`pdfs/gneiting_raftery_2007_strictly_proper_scoring_rules.pdf`](pdfs/gneiting_raftery_2007_strictly_proper_scoring_rules.pdf) |
| **Axis 5** — Yamin et al. 2026 — Belief coherence | https://arxiv.org/abs/2602.06286 | — |
| **Axis 5** — Zhu & Griffiths 2024 — Incoherent probability judgments | https://arxiv.org/abs/2401.16646 | — |
| **Axis 5** — Chadwick, Kahng, Kipper 2025 — Dutch books and money pumps | (HAR 2025; no arxiv) | [`pdfs/chadwick_kahng_kipper_2025_dutch_books.pdf`](pdfs/chadwick_kahng_kipper_2025_dutch_books.pdf) |

## Diagnostic-and-correction literature (the §3 anchor cluster)

| Paper | Public link | Local PDF |
|---|---|---|
| Chen, Liu, Shan, Zhong 2023 — Emergence of economic rationality in GPT | https://arxiv.org/abs/2305.12763 | — |
| Hagendorff, Fabi, Kosinski 2023 — Thinking-fast-and-slow LLMs | https://arxiv.org/abs/2212.05206 | — |
| Wen 2025 — Economic rationality under specialization | https://arxiv.org/abs/2501.18190 | — |
| Qiu et al. 2026 — Bayesian teaching for probabilistic reasoning | https://arxiv.org/abs/2503.17523 | — |
| Tak et al. 2026 — Sparks of rationality | https://arxiv.org/abs/2601.22329 | — |

## Methodological foundations (Layer 1 + Layer 2)

| Paper | Public link | Local PDF |
|---|---|---|
| Davis-Stober et al. — Transitivity bench | https://arxiv.org/abs/2502.10554 | — |
| Raman et al. 2024 — STEER | https://arxiv.org/abs/2402.09552 | — |
| Echenique, Saito 2015 — SARSEU | https://doi.org/10.3982/QE418 | — |
| Ross, Kim, Lo 2024 — LLM Economicus | https://arxiv.org/abs/2408.02784 | — |
| Kahneman, Tversky 1979 — Prospect theory | https://doi.org/10.2307/1914185 | — |
| Tversky, Kahneman 1992 — Cumulative prospect theory | https://doi.org/10.1007/BF00122574 | — |

## Adoption-traction comparators

| Paper | Public link | Local PDF |
|---|---|---|
| Rationality Check! 2025 (Tsinghua) | https://arxiv.org/abs/2509.14546 | — |
| QEDBench 2026 (Yale-led) | https://arxiv.org/abs/2602.20629 | — |
| Alignment Revisited 2025 | https://arxiv.org/abs/2506.00751 | — |
| GuruAgents 2025 | https://arxiv.org/abs/2510.01664 | — |
| PTCBench | https://arxiv.org/abs/2602.00016 | — |

## Layer 3 wrap candidates (additional published benchmarks)

| Paper | Public link | Layer 3 candidate |
|---|---|---|
| Market-Bench 2026 — procurement / retail / supply-chain | https://arxiv.org/abs/2604.05523 | F15 in layer3_candidates.md |
| PolyBench 2026 — live prediction-market forecasting + trading | https://arxiv.org/abs/2604.14199 | F16 |
| "When Agents Shop for You" 2026 — role coherence + willingness-to-pay leakage | https://arxiv.org/abs/2604.26220 | F17 |
| Vending-Bench 2025 — long-horizon coherence | https://arxiv.org/abs/2502.15840 | F12 |

## Environment / evaluation infrastructure (for AERead-env design)

| Library | Public link | Purpose |
|---|---|---|
| OpenSpiel (DeepMind) — general game substrate | https://github.com/deepmind/open_spiel | API precedent for AERead-env compatibility (see [`aeread_env_design.md`](../aeread_env_design.md)) |
| lm-evaluation-harness (EleutherAI) — LLM eval framework | https://github.com/EleutherAI/lm-evaluation-harness | Adoption channel; AERead-env ships a harness adapter from v0.5 |
| Gymnasium (Farama) — RL environment API | https://github.com/Farama-Foundation/Gymnasium | Bridge adapter for RL practitioner adoption |

## Convention

- **Always provide a public URL** when one exists (arxiv, DOI, publisher, preprint server)
- **If no public URL exists**, the PDF lives in [`pdfs/`](pdfs/) and the reference points there
- **Never reference a paper by local filesystem path** — paths break across machines and break for collaborators reading the repo from GitHub
- **Markdown links** (`[label](url)` or `[label](pdfs/file.pdf)`) make every citation one click away
- When citing inline in prose, link the first occurrence; subsequent mentions in the same doc can be bare ("Andrews 2026") since the reader already has the link

Bibliographic metadata (full author lists, venues, year, abstract anchors) lives in [`references_master.yaml`](references_master.yaml) and [`_INDEX.md`](_INDEX.md). This file is the **link layer** for accessibility.
