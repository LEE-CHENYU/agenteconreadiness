# Prior Art Brief — the 3 anchor benchmarks AERead integrates

A ~3-page synopsis of the three recent anchor benchmarks AERead builds on, spanning **March 2025 (EconEvals) → February 2026 (Andrews) → May 2026 (TERMS-Bench)**. Each section: what the paper does + key methodology contribution + what AERead inherits + what AERead extends + the specific §Future Work question AERead addresses. Use this as a primer before drilling into the full papers; see [`reading_list.txt`](reading_list.txt) for tiered priority + per-axis tagging and [`methodology.md`](methodology.md) for the AERead framework.

> **Reference convention**: anchor-paper §X.Y refs (e.g., Andrews's §3) point to those papers' own sections — accessible via the [PDF in this repo](papers/pdfs/andrews_2026_revealed_rationality.pdf) for Andrews and via [`papers/links.md`](papers/links.md) for the rest. AERead framework references use concept names with parenthetical pointers to [`methodology.md`](methodology.md) section headings (e.g., "judge-free by construction (methodology.md §Five methodological commitments #3)"). No source-repo access needed to follow this brief.

---

## 1. Stanford TERMS-Bench (Zhang et al., May 2026)

**Authors**: Zhang, Zhang, Pappu, El, Blanchet, Athey, Liu, Zou (Stanford School of Engineering + Dept of Economics + GSB)
**Senior advising**: Susan Athey + Jose Blanchet + James Zou; Alvin Roth thanked for early feedback (citing his *Axiomatic Models of Bargaining*)
**Paper**: [arxiv 2605.13909](https://arxiv.org/abs/2605.13909)
**Live leaderboard**: [terms-bench.github.io](https://terms-bench.github.io) — closest UX precedent for AERead
**Repo**: github.com/zou-group/terms-bench (404 as of 2026-05-26; release expected within 1-3 months)
**Coordination target**: Erica Zhang (Stanford School of Engineering)

### What the paper does

A Bayesian-game framework for **bilateral price negotiation** where LLM agents bargain against algorithmically controlled counterparts whose types are drawn from known distributions. 13 LLM agents evaluated across **6 counterpart families** (CANDID / TACITURN / EXPRESSIVE / STRATEGIC + STOCHASTIC / ADVERSARIAL stress) × **3 regimes** (Overlap / Urgency-shift / No-deal). Reports a **4-axis 6-metric** scoreboard rather than a composite: SE⁺ (feasible surplus efficiency), AGR⁺/CSE⁺/FAGR⁻ (agreement-calibration triplet), BEtype (belief error on counterpart type), CritViol% (protocol breaches), Ū (raw utility sanity check). Includes a **data-grounded extension** on Amazon catalog (831 products, 14 categories) and a **bankroll mode** chaining T sessions to surface solvency failures invisible to single-episode metrics. Headline empirical findings: Claude Opus 4.6 leads SE⁺=0.694; GLM-5.1 leads BEtype=0.218 (lowest belief error); GPT-4o-mini bottom at 0.189; **αcue < 0 for every LLM tested** — cue-revealing prompts REDUCE surplus extraction (agents are cue-fooled).

### Key methodology contribution

The **oracle-gap intervention decomposition**: for any task admitting (hidden state, controllable simulator, oracle policy, belief substitution, state reveal, scalar utility), the gap between the oracle's utility and the agent's utility decomposes as

> U(π★) − U(π_base) = Δ_inf + Δ_unc + Δ_ctrl

where Δ_inf = information gap (closed by revealing the hidden state); Δ_unc = uncertainty gap (closed by substituting the agent's beliefs with the oracle posterior); Δ_ctrl = control gap (residual — the agent's policy is suboptimal even given the oracle posterior). Zhang et al. presented this as **bargaining-specific** but the construction is the cleanest formalization of "why did the model lose surplus?" in the LLM-economics literature.

A second contribution: their oracle policy is **simulator-relative Bayes-optimal** — explicitly NOT normative. They reject the framing where "rational" means "matches a particular utility function"; instead they ask "Bayes-optimal given the simulator's specification" and let downstream users decide whether the simulator is normatively interesting. This rejects LLM-as-judge entirely.

### What AERead inherits

- **The Eq. 4 oracle-gap decomposition** — abstracted into the `OracleDecomposable` interface that is AERead's Axis 1 (Information) primary anchor
- **Environment-as-verifier** + **simulator-relative oracle** — AERead's judge-free-by-construction commitment (methodology.md §Five methodological commitments #3) cites TERMS-Bench as one of three concurrent 2025-2026 benchmarks (alongside EconEvals + Revealed Rationality) that independently rejected LLM-as-judge
- **The 7-axis sortable-table leaderboard layout** ([terms-bench.github.io](https://terms-bench.github.io)) — closest UX precedent for AERead's 5-axis radar + sortable composite. AERead's [`proposal.md`](proposal.md) §9.3 (C) Yuecheng Phase-0 frontend prototype explicitly studies this layout.
- **Bankroll mode pattern** — surfacing failures that single-episode metrics miss is the inspiration for AERead's long-horizon Vending-Bench wrap consideration in [`layer3_candidates.md`](layer3_candidates.md) F12.

### What AERead extends

- **OracleDecomposable as a generalizing abstraction**: AERead applies Eq. 4 mechanics across a **collection of use cases** — v0 first paper: C2 ProductProcurementGame (qualitative-evidence procurement) + D3 VendorSelectionGame (risk/uncertainty supplier selection); roadmap: D2 bargaining (TERMS-Bench wrap) + C1 persona-fit (13F IRL portfolio case) + agentic marketplace + NegotiationGame + PricingCompetitionGame + ~25 candidate-pool extensions. Demonstrating the same decomposition across two structurally distinct procurement-style decisions in v0 is the "generalization" claim TERMS-Bench by itself does not stake.
- **Cross-axis integration**: TERMS-Bench's intervention-decomposition is single-axis (information). AERead's 5-axis taxonomy (information × consistency × calibration × computational × meta-cognitive) integrates Δ_inf with 4 other axes via a pre-registered factorial intervention design; cross-decomposition produces a per-(model, task) attribution matrix with main-effect cells + pairwise interaction cells + residual. **Whether main effects explain a high fraction of variance is a per-domain empirical hypothesis** (working hypothesis: 60-75% for clean single-agent procurement, declining to 25-50% for long-horizon agents — full per-domain table in [methodology.md § Q7](methodology.md#q7--how-much-of-the-per-model-task-gap-do-layers-1--2-explain-whats-the-residual)). Pre-registered with falsification criteria per domain; not assumed.
- **Layer 3 wrap path**: AERead plans to wrap TERMS-Bench's runtime as D2 once their code releases — using their bargaining environment for the bargaining axis of AERead's Layer 3 collection.

### What AERead addresses from their §Future Work

TERMS-Bench focuses on bargaining. Their findings — that αcue < 0 universally — raise a question they don't pursue: **does this cue-fooling pattern hold across non-bargaining economic decisions, or is it bargaining-specific?** AERead's collection-of-use-cases design (C1 + C2 + D2 + D3) is the empirical test. If αcue < 0 holds across domains, that's a load-bearing methodology-paper finding ("LLM agents lose surplus when given cues — across procurement, pricing, vendor selection") and a citable generalization claim downstream researchers can build on.

---

## 2. MIT Revealed Rationality (Andrews, February 2026)

**Author**: Isaiah Andrews (MIT Department of Economics + NBER, sole author)
**Paper**: [PDF in this repo](papers/pdfs/andrews_2026_revealed_rationality.pdf) — also at economics.mit.edu/sites/default/files/2026-02/Revealed%20Rationality_1.pdf
**No arxiv preprint** (MIT/NBER working paper)

### What the paper does

Proves that classical decision-theory **representation theorems** can be turned into **label-free, polynomial-time-computable continuous penalties** suitable for LLM training. Three instantiations:

| Layer | Representation theorem | Penalty | Property |
|---|---|---|---|
| Beliefs | de Finetti (1937) probabilistic coherence | L(p) = max_b min_ωⱼ Π(ωⱼ) via Dutch-book LP | Zero iff probabilities are coherent |
| Preferences | Afriat (1967) preference rationality | 1 − CCEI (Critical Cost Efficiency Index) | Zero iff data satisfy GARP |
| Joint | Echenique-Saito (2015) SARSEU | LP-feasibility efficiency index | Zero iff joint beliefs + preferences admit Bayesian rationalization |

The "if and only if" structure of the representation theorems is the load-bearing trick: penalties can be computed **without specifying what the model should value** — they only require knowing that the data admit *some* rationalizing prior + utility. The penalties are polynomial-time (LP-checkable) and require no labeled training data.

The paper also includes a **§4 literature review** of LLM-rationality work (Betz & Richardson 2023, Chen et al. 2023, Hagendorff et al. 2023, Zhu & Griffiths 2024, Chadwick et al. 2025, Wen 2025, Qiu et al. 2026, plus utility engineering via Mazeika 2025) and a **§7 caveat** that is load-bearing for AERead: *"coherence is not sufficient for good behavior… so other training signals remain essential."*

A second contribution that AERead operationalizes: the **§3 non-identification critique**. Representation theorems guarantee **existence** (some rationalizing utility exists) but not **identification** (the rationalizing utility is not unique). Different functional classes (CRRA, CARA, KT prospect, cumulative prospect, Kelly-Markowitz) can rationalize the same observed choice data with different parameters. Any benchmark that claims to "recover" an agent's true utility is overclaiming.

### What AERead inherits

- **Training-signal integration mechanism #1** (training-time penalty regularization): Andrews's three rep-theorem penalties anchor AERead's first training-signal integration variant — per-axis penalties scored on (prompt, response) pairs for use as auxiliary RLHF/DPO losses. This is one of four prior-art-anchored integration mechanisms (Andrews / Chadwick / Qiu / Betz-Richardson) that turn the methodology paper from "report card" into "input to model training."
- **Axis 2 (Consistency) mathematical anchor**: AERead's 5-axis taxonomy cites Andrews as the prior-art anchor for Axis 2; the consistency intervention mechanism (counterfactual axiom probes) operationalizes Andrews's de Finetti / Afriat penalties as runtime tests.
- **§3 non-identification framing for within-class identification**: AERead's Layer 2 (identification) explicitly commits to *within-class* identification (methodology.md §Layer 3 design discipline: predict-then-validate, multi-class robustness paragraph) — meaning we fit parameters within a chosen functional class and **explicitly acknowledge** that another class would yield different parameters that also rationalize the same data. Multi-class robustness (fit all 5 candidate classes; report posterior over them) is the predict-then-validate response to Andrews's critique.
- **§7 caveat as descriptive-not-normative anchor**: AERead's first methodological commitment — "descriptive measurement, not normative ranking" (methodology.md §Five methodological commitments #1) — is Andrews's §7 caveat verbatim. Higher AERead scores ≠ better-aligned; AERead reports a fingerprint, not a verdict.

### What AERead extends

- **Beyond training-signal to deployment-eval**: Andrews's penalties are designed as training signals. AERead operationalizes them as **runtime diagnostic probes** for deployed models — every per-(model, task) Layer 3 result gets a per-axis Axis 2 score derived from counterfactual axiom probes.
- **§4 lit review integrated, not just surveyed**: Andrews's §4 names 8 papers documenting rationality violations but treats them as separate findings. AERead's 5-axis taxonomy **organizes** Andrews's §4 papers into a single attribution framework — Betz + Chadwick anchor Axis 5 (Meta-cognitive) and the training-signal integration mechanisms for inference-time correction + self-supervised consistency training; Chen + Wen anchor the context-conditional axiomatization commitment (methodology.md §Five methodological commitments #4); Zhu-Griffiths anchors Axis 5 coherence probes; Mazeika anchors Axis 3 (Calibration); Qiu anchors the supervised-trace integration mechanism. The methodology paper §3 frames this as "reading these papers in sequence is reading a request for AERead."

### What AERead addresses from their §Future Work

Andrews's penalties are derived but not yet deployed at scale. The open question is **whether the penalties drive measurable rationality improvement in frontier LLMs**. AERead's training-signal integration architecture **describes 4 prior-art-anchored mechanisms** (Andrews + Chadwick + Qiu + Betz-Richardson) in the methodology paper; **v0 implements only Andrews's mechanism** (the simplest, label-free) as a working reference, with the other 3 deferred to a follow-up paper (per methodology.md Q5 scope-trim). The leaderboard + per-axis penalties are the **measurement infrastructure** that lets anyone — including Andrews's own group + frontier-lab researchers building on his penalties — quantify before/after impact of the Andrews mechanism in their own fine-tuning runs; v0.5+ + follow-up paper expand to the other 3 mechanisms.

---

## 3. Harvard EconEvals (Fish, Shephard, Li, Shorrer, Gonczarowski, March 2025)

**Authors**: Fish, Shephard, Li, Shorrer, Gonczarowski (Harvard + Penn State)
**Paper**: [arxiv 2503.18825](https://arxiv.org/abs/2503.18825)
**Repo**: github.com/sara-fish/econ-evals-paper (open source)
**Adoption signal**: 1 cite at 14 months despite Harvard senior author — adoption-traction anti-exemplar AERead's launch strategy explicitly addresses

### What the paper does

Three economic environments — **procurement / scheduling / pricing** — exposed to LLM agents via tool-use APIs. Agents learn the environment in-context across 100 periods at 3 difficulty levels (Basic / Medium / Hard). Three **litmus tests** for tradeoff revelation: Patience vs Impatience (intertemporal), Efficiency vs Equality (task allocation), Collusiveness vs Competitiveness (multi-agent pricing). Each litmus emits a triplet of scores: LITMUS (tradeoff response), RELIABILITY (test-retest coherence), COMPETENCY (capability under single objective, operationalized as a **pre-check** — if competency fails, the litmus score is uninterpretable). Models tested span Claude-3.5 Sonnet through GPT-5 / Gemini 3 Pro Preview. Findings: capability is improving over time (procurement +41 pp/yr, scheduling +50 pp/yr, pricing +18 pp/yr); reasoning-specialist o4-mini scores 3rd-best in procurement (calculation-heavy) but 5th–6th elsewhere; high reliability + competency across frontier models.

### Key methodology contribution

The **competency-pre-check + litmus pattern**: rather than asking "is the agent rational on this task?", EconEvals asks two questions sequentially: (1) can the agent execute the task at all (competency ≥ threshold)?; (2) given competency, what is the agent's tradeoff response (litmus score)? This separates **capability** from **preference**, which is essential when frontier models have such high baseline capability that simple rationality probes hit ceiling effects (per Chen 2023 finding CCEI > 0.997 for GPT-3.5 on budget allocation). The competency pre-check pattern is operationalized via Ross et al. 2024 + Fish et al. 2024's prior work on capability isolation.

A second contribution is the **judge-free environment-as-verifier framing**, stated directly in their abstract: *"These evaluations measure LLM tradeoff responses using human labels—which can be resource-intensive—or LLM-as-a-judge labels—which can be unreliable. By contrast, our litmus tests utilize stylized environments, which means the metrics that measure tradeoff responses are directly grounded in an underlying theoretical model."* This is exactly the judge-free-by-construction commitment (methodology.md §Five methodological commitments #3) AERead inherits.

### What AERead inherits

- **Judge-free environment-as-verifier**: AERead's judge-free-by-construction commitment cites EconEvals alongside TERMS-Bench and Revealed Rationality as the three concurrent 2025-2026 benchmarks that independently adopted this design choice.
- **Competency pre-check pattern**: AERead's Axis 4 (Computational floor) is essentially a competency pre-check — if the agent can't execute the math the choice requires (e.g., compute expected value of a lottery), the higher-axis scores are uninterpretable. AERead operationalizes Axis 4 via quantity-substitution probes (substitute the computational answer in the prompt; rerun; measure delta).
- **Multi-environment Layer 3 structure**: AERead plans to **wrap EconEvals** as v0.5 Layer 3 D-dimensions (D4 procurement / D5 pricing / D6 scheduling per [`layer3_candidates.md`](layer3_candidates.md) A1/A2/A3) — using EconEvals's environments as Cat D candidates in AERead's collection-of-use-cases framing.

### What AERead extends

- **5-axis cross-decomposition that EconEvals lacks**: EconEvals reports per-litmus LITMUS / RELIABILITY / COMPETENCY scores but does not decompose **why** a model fails on a given litmus. AERead's 5-axis taxonomy + cross-decomposition matrix is the diagnostic layer EconEvals's litmus scores point at but don't operationalize.
- **Day-1 leaderboard for adoption**: EconEvals's 1-cite-at-14-months adoption trajectory is the explicit anti-exemplar for AERead's launch playbook (per the §5 traction analysis). AERead commits to Day-1 leaderboard + frontier-lab model-card pre-commitment + plug-and-play UX as hard launch gates — avoiding EconEvals's distribution failure mode despite their identical Harvard senior author + methodologically strong design.
- **Cat C Layer 3 grounding**: EconEvals covers Cat B-C parameter+outcome layer; AERead adds Cat A axiom layer + Category C persona-fit IRL on 13F (the dimension EconEvals doesn't address).

### What AERead addresses from their §Future Work

EconEvals's adoption ceiling is the question their §Future Work doesn't ask but their citation count makes urgent: **what does it take for a methodologically strong economic-rationality benchmark to actually propagate?** AERead's §5 adoption-key findings (analysis of 25 benchmarks) extracts the cross-paper pattern — every benchmark > 200 cites has a live leaderboard + frontier-lab partner + plug-and-play UX; every benchmark without these (EconEvals, Rationality Check!) sits at 0–1 cites despite elite-PI authorship. AERead's launch architecture is engineered to land in the > 200 cite cluster, taking EconEvals's content quality and pairing it with the distribution-side commitments their team didn't make.

---

## Synthesis: how AERead's framework maps to the 3 anchor papers

| AERead component | TERMS-Bench | Andrews 2026 | EconEvals |
|---|---|---|---|
| **3-layer pipeline** | Layer 3 wrap candidate (D2 bargaining) | Layer 1 (existence) penalty math | Layer 3 wrap candidates (D4 procurement, D5 pricing, D6 scheduling) |
| **OracleDecomposable** (Axis 1) | Primary anchor — their Eq. 4 is the construction AERead abstracts | — | — |
| **Axis 2 (Consistency)** | — | Primary anchor — rep-theorem penalties | Adjacent (reliability score = test-retest coherence) |
| **Axis 3 (Calibration)** | — | Adjacent (calibration vs coherence per §7) | Adjacent (competency pre-check + litmus separation) |
| **Axis 4 (Computational floor)** | — | — | Primary anchor — competency-as-pre-check pattern |
| **Axis 5 (Meta-cognitive)** | — | §4 lit-review names Yamin / Zhu-Griffiths / Chadwick as Axis 5 supporters | — |
| **Descriptive-not-normative** (commitment #1) | "Simulator-relative oracle, not normatively-rational" framing | §7 caveat ("coherence not sufficient for good behavior") | — |
| **Measurement-model pluralism** (commitment #2) | — | §3 non-identification critique motivates within-class identification | — |
| **Judge-free by construction** (commitment #3) | Environment-as-verifier | LP-checkable penalties (no judge) | "Directly grounded in theoretical model" |
| **Context-conditional axiomatization** (commitment #4) | — | §4 lit-review names Wen 2025 as anchor | — |
| **Training-signal mechanism 1** (training-time penalty) | — | Primary anchor | — |
| **Training-signal mechanism 2** (inference-time remediation) | — | — | — (Chadwick 2025 anchors this) |
| **Training-signal mechanism 3** (supervised trace mimicry) | — | — | — (Qiu 2026 anchors this) |
| **Training-signal mechanism 4** (self-supervised consistency training) | — | — | — (Betz & Richardson 2023 anchors this) |
| **Adoption strategy** | UX precedent (7-axis sortable leaderboard at terms-bench.github.io) | — | Anti-exemplar (1 cite at 14 months → AERead avoids via Day-1 leaderboard + plug-and-play UX) |

The "reading these papers in sequence is reading a request for AERead" thesis in [`proposal.md`](proposal.md) §3 emerges from this map: each anchor paper independently arrived at one of AERead's structural commitments (judge-free, oracle-grounded, within-class identification, descriptive-not-normative); AERead's contribution is the **integration** across all three plus the diagnostic-and-correction literature ([`reading_list.txt`](reading_list.txt) T1 covers the cluster).

---

**Next read**: see [`methodology.md`](methodology.md) for AERead's framework + [`reading_list.txt`](reading_list.txt) for tiered priority. The 7 papers in the diagnostic-and-correction literature cluster (Chen / Wen / Hagendorff / Zhu-Griffiths / Chadwick / Betz-Richardson / Qiu) are covered in [`reading_list.txt`](reading_list.txt) T1 and in [`proposal.md`](proposal.md) §3.
