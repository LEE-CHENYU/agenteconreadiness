# AERead v0 Sprint Plan

> **What this is**: the consolidated operational view of the AERead v0 first-paper sprint — what we're actually building in the first 16 weeks, who owns what, what we're deferring. Framework + methodology descriptions live in [`methodology.md`](methodology.md); collaboration ask lives in [`proposal.md`](proposal.md); this doc is the **implementation plan**.
>
> **Why a separate doc**: framework docs (methodology.md, proposal.md, prior_art_brief.md) describe the full AERead framework with inline v0/v0.5+ scope tags. This sprint doc gives the team a **one-stop scan** of everything v0 in one place — no hunting through Q1/Q3/Q4/Q5 to assemble the operational picture.

---

## At a glance

| Dimension | v0 first paper |
|---|---|
| **Team** | Cheney (lead) + Yuecheng + Zihao + Jingyi (candidate per proposal §9.4) |
| **Capacity** | ~25 person-weeks over 16 weeks |
| **Layer 3 use cases** | 2 deep games — C2 ProductProcurementGame + D3 VendorSelectionGame |
| **Methodology paper §3 claim** | Integrative 5-axis taxonomy + OracleDecomposable Eq. 4 generalization across 2 procurement-style decision structures |
| **Citation channel goal** | Methodological engagement from frontier-lab researchers (pre-commercial) |
| **First sync** | 2026-06-02 |
| **4-week checkpoint** | 2026-06-30 |
| **NeurIPS / COLM submission target** | Weeks 13-16 (post-launch) |

---

## v0 implementation scope (consolidated)

### Layer 3 use cases (2 games)

- **C2 ProductProcurementGame** — single-agent, one-shot, qualitative-evidence procurement; **v0 oracle = optimal under single declared utility-weight vector per buyer profile** (per Q3 v0 scope; robust-utility-family is v0.5+ upgrade); 4-tier optimality classification (robust optimal / acceptable / weak / dominated)
- **D3 VendorSelectionGame** — single-agent, risk/uncertainty supplier selection; oracle = Bayes risk minimization given declared utility curvature

These are structurally distinct (qualitative evidence vs probabilistic risk; declared-single-vector oracle vs Bayes-risk oracle) — the pair demonstrates Eq. 4 portability across two distinct procurement-style decision structures.

### Layer 2 functional classes (3 of 5)

- KT prospect '79
- CRRA
- Kelly-Markowitz

**Deferred to v0.5+**: CARA + cumulative prospect TK '92

### Layer 1 axiom tests (2 of 6)

- Transitivity
- Dominance

**Deferred to v0.5+**: CCEI / GARP / WARP / monotonicity / Houtman-Maks

### 5-axis taxonomy instrumentation

| Axis | v0 | v0.5+ extension |
|---|---|---|
| 1 — Information | Full Δ_inf via OracleDecomposable | Belief-substitution beyond state-reveal |
| 2 — Consistency | 2 axiom tests (transitivity + dominance) | Full 6-axiom family |
| 3 — Calibration | Brier/CRPS + within-class utility-fit error | ECE diagnostic + reliability diagrams + full proper-scoring-rule suite |
| 4 — Computational floor | 1 quantity-substitution probe (sketched) | Full computation-substitution suite |
| 5 — Meta-cognitive | Confidence elicitation + Brier on held-out (sketched) | Full Dutch-book / probabilistic-identity / money-pump probe suite |

### Generalization battery (v0 subset of full design)

| Item | v0 status | v0.5+ |
|---|---|---|
| Splits | dev + hidden IID + 1 axis-OOD per game | + compositional-OOD + far-OOD + rotating seasons |
| Counterfactual variants | 2 (paraphrase + preference-flip) | + marketing-robustness + dominated-option + constraint-tightening |
| Reporting | individual split scores + Transfer Ratio | + Generalization Index composite |
| Cross-axis attribution | main effects only | + pairwise interaction matrix |
| Overfit-bot baseline | deferred | v0.5+ |
| Cache layer | yes | + signed ScoreRecords enforcement |

### Q3 qualitative-feature scoring

- Single-stage 4-tier optimality (`robust optimal / acceptable / weak / dominated`)
- Single utility-weight vector per buyer profile
- Pairwise-regret scoring (count clearly-superior alternatives missed)

**Deferred to v0.5+**: Two-stage scoring (qualitative-interpretation diagnostic + buyer-specific procurement primary); robust utility family (family of plausible weight vectors per buyer)

### Q5 RL training-signal mechanisms (1 of 4 implemented)

- **Implemented in v0**: Andrews 2026 training-time penalty (the simplest, label-free, LP-checkable)
- **Described in v0 paper, implementation deferred**: Chadwick 2025 (inference-time correction), Qiu 2026 (supervised trace mimicry), Betz & Richardson 2023 (self-supervised consistency training) → follow-up paper

### Q6 AERead-Train/Dev/Cert naming convention

- **v0**: docs-only convention (paper articulates it; leaderboard webpage labels splits accordingly; submission instructions require provenance declaration)
- **v0.5+**: infrastructure enforcement (automated provenance verification; leaderboard auto-refusal of Dev-only scores reported as "AERead scores"; signed-ScoreRecord verification)

### Infrastructure

| Component | v0 | v0.5+ |
|---|---|---|
| Scorers | 3 (Brier + transitivity + 1 multi-class utility-fit) | Full Bradley-Terry / WST/MST/SST / KT-MLE / isotonic library |
| Generators | ~4 (enough for C2 + D3) | ~11 |
| Cache layer | yes | + signed ScoreRecords |
| CLI | `aeread evaluate / diagnose / init` | + `aeread check` |
| Submission paths | web form only | + Colab + PR |
| Validation runs | 3-5 frontier models | 8+ models |
| Leaderboard frontend | yes | + cross-decomposition matrix on drill-down |
| Diagnostic drill-down | 5-axis radar + main-effect cells | + pairwise interaction matrix |
| lm-evaluation-harness integration | prototype (adapter) | mature production adapter |
| HuggingFace integration | deferred | model-card adoption pipeline |
| Documentation | README + new-task guide + contributor onboarding for v0 scope | + Colab template + full contributor docs |

### Out of v0 entirely

- **AERead-env substrate** ([`aeread_env_design.md`](aeread_env_design.md)) — post-v0-paper follow-up paper, NOT v0.5+. v0 ships 2 standalone games (no shared substrate).
- C1 persona-fit / 13F IRL as a Layer 3 use case — moved to roadmap. The rationale source repo continues developing the IRL infrastructure as Layer 2 parameter-fit work; C1 appears as a v0.5+ Layer 3 case study once v0 framework validates.
- D2 bargaining (TERMS-Bench wrap) — roadmap; wrap when TERMS-Bench releases code

---

## Ownership map (~13 workstreams for 3-4 person team)

### Methodology (5 workstreams)

| # | Workstream | Primary | Supporting |
|---|---|---|---|
| M1 | Layer 1 axiom protocol specs (transitivity + dominance) | Zihao | Yuecheng (scorer impl) |
| M2 | Layer 2 within-class identification framework (3 functional classes) | Zihao | Yuecheng (fit-procedure impl) |
| M3 | Layer 3 OracleDecomposable formalization | Zihao | Cheney (C2 + D3 instantiation) |
| M4 | Layer 3 predict-then-validate train/test split design + Q4 generalization-battery v0 scope | Yuecheng | Zihao (formal justification) |
| M5 | 5-axis taxonomy instrumentation (axes 1+2+3 full; axes 4+5 sketched) | Yuecheng (axes 3-5) + Zihao (axes 1-2) | Cheney |

### Engineering (7-8 workstreams)

| # | Workstream | Primary | Supporting |
|---|---|---|---|
| E1 | lm-evaluation-harness adapter | **Jingyi if she joins per §9.4**; else Yuecheng | Yuecheng (scorer integration regardless) |
| E2 | v0 scorer library subset (3 scorers) | Yuecheng | Zihao (correctness review), Cheney (v0 scaffold) |
| E3 | Generator library + YAML schema (enough for C2 + D3) | Cheney | Yuecheng (refinement) |
| E4 | Cache layer + CLI | Cheney + Yuecheng | — |
| E5 | C2 ProductProcurementGame end-to-end | Cheney | Zihao (oracle formalization), Yuecheng (Q3 scoring impl) |
| E6 | D3 VendorSelectionGame end-to-end | Cheney | Zihao (Bayes-risk oracle), Yuecheng (risk-calibration scorer) |
| E7 | Leaderboard frontend + diagnostic drill-down page | Cheney | Yuecheng (review) |
| E8 | Benchmark validation runs (3-5 frontier models) | Cheney + Yuecheng | — |
| E9 | Documentation (README + contributor onboarding) | Cheney | Yuecheng (technical content) |

### External (3 workstreams)

| # | Workstream | Primary | Supporting |
|---|---|---|---|
| X1 | Methodology paper §1-§8 writing | Cheney | All |
| X2 | Andrews / Gonczarowski / Erica external review coordination | Cheney drafts; Zihao reviews | — |
| X3 | Frontier-lab partner pre-commit + Open Phil grant | Cheney | — |

**Total: ~13 workstreams** for ~25 person-weeks over 16 weeks.

### Per-person rough allocation

- **Cheney**: 5-6 workstreams (E3, E5, E6, E7, E9, X1, X2, X3 — leads researcher-facing surface + 2 games + writing + outreach)
- **Yuecheng**: 3-4 workstreams (M4, M5 stats-side, E2, E8 — leads stats methodology + scorer infrastructure)
- **Zihao**: 2-3 workstreams (M1, M2, M3 — leads §3 methodology core + OracleDecomposable formalization)
- **Jingyi (if she joins)**: 1 workstream (E1 — lm-eval-harness adapter); ~5-8% of v0 total

---

## Phase timeline

| Phase | Calendar | Activity | Deliverables |
|---|---|---|---|
| **Phase 0 — trial collaboration** | Weeks 1-4 (2026-06-02 → 2026-06-30) | Each contributor takes 1-2 Phase-0 items from proposal §9.2 (Zihao) / §9.3 (Yuecheng) / §9.4 (Jingyi if engaged); Cheney drafts §1+§2 in parallel | Phase-0 deliverables for the 4-week checkpoint |
| **Phase 1 — paper draft** | Weeks 5-8 | Methodology paper §3 (5-axis + OracleDecomposable) drafted from Zihao's Phase-0 work; §1+§2 polished; §6 stats-reproducibility polished from Yuecheng's Phase-0 (D); §10 (Zihao) first draft; arxiv preprint target | First paper draft |
| **Phase 2 — preprint + reviews** | Weeks 9-12 | External methodology reviews (Andrews, Gonczarowski); leaderboard launch with 3-5 frontier models; frontier-lab pre-commit conversations | Preprint + live leaderboard |
| **Phase 3 — submission + pilot** | Weeks 13-16 | NeurIPS / COLM submission; Tier 2 audit pilot conversations | Submitted paper + 1-2 design-partner pilots |

### Key milestones

- **2026-06-02**: First sync with Yuecheng + Zihao (+ Jingyi if engaged by then)
- **2026-06-09**: Cheney ships A4 stability dimension end-to-end
- **2026-06-23**: Phase-0 deliverable target for all collaborators
- **2026-06-30**: 4-week checkpoint — decision on continuation + authorship + Phase 1 commitments

---

## v0.5+ extension roadmap (explicit deferrals)

Why we're deferring these (not optional commitments — these are the next-release work):

### Statistical / methodological extensions

- CARA + cumulative prospect TK '92 functional classes (Q1)
- Full 6-axiom family — CCEI / GARP / WARP / monotonicity / Houtman-Maks (Q1 / Axis 2)
- Two-stage qualitative scoring + robust utility family (Q3)
- Full Q4 generalization battery — compositional-OOD + far-OOD + rotating seasons + overfit-bot baseline + Generalization Index composite (Q4)
- Pairwise interaction matrix in cross-axis attribution (5-axis taxonomy)
- 5-counterfactual battery — adds marketing-robustness + dominated-option + constraint-tightening (Q4)
- Axes 4 + 5 full instrumentation (5-axis taxonomy)

### Engineering extensions

- Full scorer library (Bradley-Terry, WST/MST/SST, KT-MLE, isotonic) (proposal §9.5)
- Signed ScoreRecords enforcement (Q4 / Q6)
- Colab + PR submission paths (proposal §7)
- HuggingFace + model-card adoption pipeline (proposal §9.5)
- 8+ frontier-model validation runs (proposal §7)
- Cross-decomposition matrix on diagnostic drill-down page

### Roadmap (v0.5+ or v1+; depends on traction)

- C1 persona-fit / 13F IRL as Layer 3 case (rationale repo's IRL infrastructure continues development; first appears as v0.5+ Layer 3 case once v0 validates)
- D2 bargaining (TERMS-Bench wrap when code releases)
- Agentic marketplace extension (multi-agent extension of D3)
- NegotiationGame + PricingCompetitionGame (per aeread_env_design.md substrate roadmap)

### Out of v0.5+ entirely (separate follow-up paper)

- 3 of 4 RL training-signal mechanisms (Chadwick / Qiu / Betz implementations) — described in v0 paper; implementations are a separate follow-up paper
- **AERead-env substrate** ([`aeread_env_design.md`](aeread_env_design.md)) — separate post-v0-paper follow-up paper, not v0.5+

---

## Status tracker

(Open for ongoing updates as work progresses.)

### Phase 0 status

- [ ] Cheney §1+§2 draft (target 2026-06-23)
- [ ] Cheney A4 stability dimension end-to-end (target 2026-06-09)
- [ ] Zihao Phase-0 item(s) from §9.2 (target 2026-06-23)
- [ ] Yuecheng Phase-0 item(s) from §9.3 (target 2026-06-23)
- [ ] Jingyi outreach + Phase-0 commitment decision (if she engages)

### Open ops slot status

- Jingyi Lu: under consideration; not yet approached (as of 2026-05-27)

### Pending v0 scope decisions (4-week checkpoint)

- **Q10 training-signal validation experiment** — whether to include a small-model (Qwen 0.5B / 3B) training experiment in v0 to causally validate AERead's per-axis penalty as auxiliary training signal. Three options pending checkpoint resolution: (A) defer to follow-up paper; (B) include in v0 (+3 person-weeks, ~$1K compute); (C) hybrid — pre-register in v0, result lands shortly after. **Working recommendation: (C) hybrid**, contingent on Jingyi (or ops collaborator) bandwidth for training-loop-integration. See [methodology.md § Q10](methodology.md#q10--can-aeread-validate-training-signal-quality-without-training-models-ourselves) for the full options table + open subquestions.

### Cross-repo sync status

- agenteconreadiness (this repo): canonical v0 scope (per 2026-05-27 deferral refactor + Jingyi addition + 10-issue review fixes)
- rationale source repo: synced 2026-05-27 — master plan + Open Phil application + pitch v0.2 + runtime spec all carry the 2026-05-27 v0 scope revision banner

---

## Cross-references

- **Full framework + methodology**: [`methodology.md`](methodology.md)
- **Collaboration ask + risks + timeline**: [`proposal.md`](proposal.md)
- **Prior-art primer**: [`prior_art_brief.md`](prior_art_brief.md)
- **Layer 3 candidate pool (post-v0 expansion)**: [`layer3_candidates.md`](layer3_candidates.md)
- **Post-v0-paper substrate roadmap**: [`aeread_env_design.md`](aeread_env_design.md)
- **Repository overview**: [`../README.md`](../README.md)
