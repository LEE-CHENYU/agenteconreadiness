# Layer 3 Use Case Candidates — Open List

This is the **open candidate pool** for AERead Layer 3 (real-world economic decision use cases). v0 ships with **2 deep games** (C2 ProductProcurementGame + D3 VendorSelectionGame); the rest are listed here as candidates we'll evaluate for v0.5 / v1 / v1.5 / v2 expansion. **Listing is harmless** — having the full pool visible prevents us from missing high-leverage cases later.

## Selection criteria

A good Layer 3 case satisfies:

1. **Real economic decision** — has a dollar/utility-equivalent outcome; not an abstract axiom probe
2. **OracleDecomposable** — admits the (hidden state + controllable simulator + Bayes-optimal oracle + scalar utility) interface that supports the Eq. 4 decomposition (Δ_inf + Δ_unc + Δ_ctrl)
3. **Deployment-relevant** — agents actually do this in the wild today, OR will within ≤ 12 months
4. **Distinct domain** — extends the OracleDecomposable generalization claim into a new structural form (bargaining ≠ matching ≠ auction ≠ forecasting)
5. **Tractable simulator** — can be implemented in ≤ 1 week with reasonable data/code; some can wrap existing benchmarks (TERMS-Bench, EconEvals)

Cases that fail (1) are Layer 1/2 (axiom probes / parameter fits). Cases that fail (2) belong in a different framework. Cases that fail (3) are fine but lower priority.

## Value × testability matrix

Every candidate can be placed on two axes:

- **Economic value** (vertical): how high is the dollar / utility stake of getting this decision right? High = revenue-leaking deployments (pricing, matching) or life-stakes (kidney exchange, healthcare); Medium = enterprise efficiency (procurement, scheduling); Low = academic interest only (Allais paradox)
- **Testability** (horizontal): how cleanly can we evaluate it? High = closed-form oracle + cheap simulator + deterministic ground truth; Medium = tractable but data-dependent; Low = ground truth requires long observation, proprietary data, or unsettled methodology

The **top-right quadrant** (high value × high testability) is where AERead's leaderboard headline value sits — and where the methodology paper's §3 generalization claim ("OracleDecomposable Eq. 4 across non-bargaining domains") gets the strongest empirical demonstration. Top-middle and middle-right are good v1+ adds. Bottom row is methodologically interesting + clean for §3 falsification testing but doesn't drive leaderboard impact. Anything in the low-testability column needs methodology work before we can ship it.

|                    | **High testability** (closed-form oracle, cheap sim) | **Medium testability** (data-dependent, approximate oracle) | **Low testability** (hard ground truth, contested method) |
|---|---|---|---|
| **High economic value** | A2 EconEvals pricing • A6 two-sided matching (kidney exchange / residency) • B3 algorithmic trading | B1 Calvano collusion • A7 price discrimination | (Zihao mechanism-design candidates land here?) |
| **Medium value** | A1 EconEvals procurement • A3 EconEvals scheduling • A4 sealed-bid auction • A5 ascending auction • C2 ProductProcurementGame (v0 game 1) • D3 VendorSelectionGame (v0 game 2) • D2 bargaining (roadmap wrap) | C1 persona-fit (roadmap; v0.5+ Layer 3 case) • C7 multi-issue negotiation • D9 election prediction • G18 insurance / risk pooling | C6 coalitional bargaining • F14 customer-service triage |
| **Low value** | D8 weather forecasting • G15 iterated ultimatum • G17 Allais paradox | C3 commons governance • C4 repeated PD • C5 multi-agent coord (γ-Bench) • G16 trust game | E11 budget-constraint learning • F13 web browsing under budget |

**What the matrix tells us**:
- **The top-right quadrant is the primary methodology-validation surface** — pricing, matching, trading, procurement, scheduling, auctions. These are the cases with both economic stakes and clean oracle decomposition, making them the strongest demonstration sites for the OracleDecomposable Eq. 4 generalization across non-bargaining domains (the methodology paper §3 contribution).
- **The top-middle is the highest-priority "needs methodology work" zone** — B1 Calvano collusion + A7 price discrimination both have high economic value but require multi-round simulator engineering before they're testable at AERead's plug-and-play standard.
- **The bottom-right is the academic-credibility cluster** — weather forecasting, iterated ultimatum, Allais paradox. These are clean, citable, and load-bearing for methodology-paper §3 validation across non-bargaining domains.
- **The high-value × high-testability cell is sparser than ideal** — A2 EconEvals pricing, A6 two-sided matching, B3 algorithmic trading are listed there, but each has substantive oracle-derivation work pending before the OracleDecomposable interface ships clean. Mechanism-design contribution (per §9.3 Phase-0 option D below or external contributions via the OracleDecomposable submission channel): theoretically formalize the oracle for these cases to harden their testability score.

**Open ask for Zihao** (per §9.3 (D) in the proposal): two complementary mechanism-design contributions, either of which closes the matrix gap:

1. **Propose new candidates** that aren't yet in this doc — strong theoretical formalization + deployment relevance (spectrum auctions, prediction markets, generalized second-price / AdWords, market-maker bid-ask spread, etc. are likely missing). Land them in the high-value rows wherever the testability allows.
2. **Formalize the oracle policy for existing high-value cases** that currently sit in medium testability (A2 EconEvals pricing or B1 Calvano collusion are highest-leverage). Deriving the closed-form oracle moves them into the high-testability column — strongest demonstration sites for the methodology paper §3 generalization claim.

**Open contribution channel for external researchers**: the OracleDecomposable abstraction *is* the contribution interface — any economic-decision use case admitting (hidden state + controllable simulator + oracle policy + scalar utility) with declared OOD axes (per [`aeread_env_design.md`](aeread_env_design.md) §6) lands somewhere in the matrix above. The methodology paper §3 cites contributors whose cases enter v0.5 or later releases. **This is part of AERead's pre-commercial citation strategy**: the contribution channel itself is engagement bait — frontier-lab researchers who submit cases become co-authors on the methodology paper's generalization claim.

## Status quo (v0 / roadmap)

| Code | Case | Status | Source |
|---|---|---|---|
| C2 | **ProductProcurementGame** (qualitative-evidence procurement) | **v0 — game 1** | Novel; primary demonstration site for Q3 qualitative-feature scoring discipline |
| D3 | **VendorSelectionGame** (single-agent risk/uncertainty supplier selection) | **v0 — game 2** | Novel single-agent simpler form; the agentic marketplace extension is roadmap |
| D2 | Bilateral bargaining | **Roadmap (wrap)** | Zhang et al. 2026 TERMS-Bench ([paper](https://arxiv.org/abs/2605.13909) + [live leaderboard](https://terms-bench.github.io)) |
| C1 | Persona-fit (IRL on 13F investor decisions) — Layer 2 parameter-fit case study | **Roadmap (v0.5+ Layer 3 case)** | Novel; rationale source repo's IRL infrastructure continues to develop this for v0.5+ |
| Agentic marketplace | D3 multi-agent + agentic tool-use extension | **Roadmap (v1+ extends D3)** | EconEvals precedent |

## Candidate pool (open)

Organized by structural cluster. Each row: case, source, OracleDecomposable hint, pros, cons, priority assessment.

### A. Auctions + market mechanisms

| # | Case | Source | OracleDecomposable hint | Pros | Cons | Priority |
|---|---|---|---|---|---|---|
| A1 | **EconEvals procurement** (multi-vendor under budget) | Fish/Gonczarowski 2026 | Hidden = vendor cost/quality matrix; oracle = optimal allocation under budget | Already published; mutual citation benefit with EconEvals; wraps cleanly | EconEvals at 1 cite — we may pull them up rather than vice versa | **Tier A (v0.5)** |
| A2 | **EconEvals pricing** (dynamic pricing under uncertain demand) | Fish/Gonczarowski 2026 | Hidden = demand-curve parameters; oracle = revenue-maximizing price | Highest dollar-value deployment surface; calibration directly leaks revenue | Pricing dynamics may not OracleDecompose cleanly if demand has long-tail uncertainty | **Tier A (v0.5)** |
| A3 | **EconEvals scheduling** (task assignment/timing) | Fish/Gonczarowski 2026 | Hidden = task durations + dependencies; oracle = Hungarian/LP-optimal assignment | Hungarian algorithm gives clean closed-form oracle; widely deployed (gig dispatch, project mgmt) | Less rationality-specific than pricing; could feel like generic combinatorial benchmark | **Tier B (v1)** |
| A4 | **Sealed-bid auction (first-price + second-price)** | Banchio & Skrzypacz 2022 + auction theory | Hidden = competitor valuations; oracle = bid-shading formula under assumed competitor distribution | Diagnoses bid-shading, collusion; mechanism-design hooks for §10 Discussion | Pure auction theory may feel narrow vs broader "real-cases" framing | **Tier B (v1)** |
| A5 | **Ascending (English) auction** | Auction theory; natural extension of A4 | Hidden = competitor reservation prices; oracle = dominant-strategy bid-up-to-value | Tests jump-bidding + shilling resistance; widely deployed (eBay, real estate) | Almost-trivial dominant strategy may give ceiling effects on frontier models | **Tier C (v1.5)** |
| A6 | **Two-sided matching (Gale-Shapley)** | Gale & Shapley 1962; school-choice + residency lit | Hidden = participant preference orders; oracle = stable matching (Gale-Shapley DA algorithm) | Roth in TERMS-Bench acknowledgments; strong mechanism-design anchor; school-choice + medical residency are real deployments | Strategic preference reporting is the interesting part — pure matching is not | **Tier B (v1)** |
| A7 | **Price discrimination / menu design** | Kadiyala et al. 2023 | Hidden = buyer type/willingness-to-pay; oracle = revenue-optimal discriminatory pricing | E-commerce personalization deployment | Ethically fraught (price discrimination); may attract negative attention | **Tier D (parked)** |

### B. Algorithmic strategy / competition

| # | Case | Source | OracleDecomposable hint | Pros | Cons | Priority |
|---|---|---|---|---|---|---|
| B1 | **Repeated pricing — collusion detection** | Calvano et al. 2020 AER; Fish et al. 2024 (algorithmic collusion in LLMs); `docs/papers/cited/algorithmic_collusion/` | Hidden = competitor strategy profile; oracle = competitive Nash equilibrium | Calvano is highly cited; LLM-collusion is regulator-relevant; pairs with A2 pricing for a "do agents collude?" story | Multi-round + multi-agent — heavier simulator | **Tier A (v0.5)** — pair with A2 |
| B2 | **Dynamic pricing under competition (Bertrand + capacity)** | Extension of B1 | Hidden = competitor capacity + demand; oracle = capacity-constrained Bertrand equilibrium | Captures airline/hotel revenue mgmt; more realistic than pure Bertrand | Same multi-agent overhead as B1 | **Tier B (v1)** |
| B3 | **Algorithmic trading / portfolio rebalancing** | HFT lit + standard finance | Hidden = price-process parameters; oracle = optimal stopping / Merton portfolio | Direct extension of C1 to multi-period; finance domain consistency | Existing alpha-research benchmarks already cover this (LLM4Trading, GuruAgents) | **Tier C (v1.5)** |

### C. Multi-agent coordination + cooperation

| # | Case | Source | OracleDecomposable hint | Pros | Cons | Priority |
|---|---|---|---|---|---|---|
| C3 | **Commons governance** (tragedy of commons sustainability) | Piatti et al. 2024 NeurIPS; `docs/papers/cited/algorithmic_collusion/` | Hidden = other agents' extraction profiles; oracle = sustainable-Nash extraction rate | Environmental/policy relevance; multi-agent gives §10 mechanism-design hooks | Hard to make economically-grounded (utility units fuzzy) | **Tier C (v1.5)** |
| C4 | **Repeated Prisoner's Dilemma / Trust game** | Akata et al. 2025 Nature Human Behaviour | Hidden = opponent strategy (tit-for-tat / GRIM / etc.); oracle = best-response to inferred opponent | Long history; well-defined oracle; tests cooperation/defection learning | Heavily-studied; may not differentiate AERead enough | **Tier C (v1.5)** |
| C5 | **Multi-agent coordination under incomplete info** (γ-Bench) | Huang et al. 2025 ICLR | Hidden = others' types/beliefs; oracle = Bayesian Nash equilibrium | 8 classical scenarios; pre-built benchmark to wrap | γ-Bench coverage may overlap our other game-theoretic D-dimensions | **Tier C (v1.5)** |
| C6 | **Coalitional bargaining + side-payments** | Hart 1992; Cooperation-or-Collapse | Hidden = others' reservation values; oracle = Shapley value or core allocation | Multi-firm JV deployment context; senior advisor mechanism-design hook | N-player simulators get combinatorially expensive | **Tier D (parked)** |
| C7 | **Mediated multi-issue negotiation** | Multi-issue bargaining lit; Lewis et al. DealOrNoDeal | Hidden = other party's utility over multi-dim bundle; oracle = Pareto-optimal split | Extends D2 (bilateral price) to multi-attribute; more realistic enterprise context | Risk of feeling like a TERMS-Bench variant rather than distinct | **Tier B (v1)** |

### D. Probabilistic judgment / forecasting

| # | Case | Source | OracleDecomposable hint | Pros | Cons | Priority |
|---|---|---|---|---|---|---|
| D8 | **Weather / event probability forecasting** | Zhu & Griffiths 2024 (already cited Axis 5); meteorology lit | Hidden = true posterior given observed data; oracle = Bayes-optimal forecast | Zhu-Griffiths gives probabilistic-identity probe set already; pairs with Axis 5 calibration | Pure forecasting may feel less "economic decision" than other cases | **Tier B (v1)** — high diagnostic value |
| D9 | **Election prediction / poll aggregation** | Qiu et al. 2026 Bayesian teaching | Hidden = electorate latent state; oracle = Bayesian posterior under aggregation model | Multi-round Bayesian updating tests Qiu's teaching framework; deployment-relevant (polling firms, prediction markets) | Election models are politically charged; risk of attracting controversy | **Tier C (v1.5)** |
| D10 | **Geopolitical forecasting under ambiguity** | Ellsberg-style; Gilboa-Schmeidler | Hidden = true model uncertainty (genuine ambiguity, not just risk); oracle = ambiguity-averse decision (maxmin EU) | Tests Layer 2 extension to ambiguity-aversion utility class (per the "v1.5+ instantiations" framing) | Hard to operationalize without privileging one ambiguity-attitude model | **Tier C (v1.5)** |

### E. Resource allocation + budget reasoning

| # | Case | Source | OracleDecomposable hint | Pros | Cons | Priority |
|---|---|---|---|---|---|---|
| E11 | **Sequential budget-constraint learning** | Afriat/GARP applied to sequential consumption | Hidden = agent's budget; oracle = revealed-preference CCEI fit | Tests Layer 1 GARP in deployment context; personal-finance relevance | Closely overlaps existing Cat A monotonicity tests | **Tier D (parked)** — too close to Cat A |

### F. Long-horizon agentic tasks

| # | Case | Source | OracleDecomposable hint | Pros | Cons | Priority |
|---|---|---|---|---|---|---|
| F12 | **Vending machine management** (long-horizon task coherence) | Vending-Bench (Backlund & Petersson 2025) | Hidden = customer demand patterns + supply costs; oracle = revenue-maximizing restock + price policy | Tests 20M+ token coherence (rare in benchmarks); autonomous-retail deployment | Long-horizon evals are expensive (API spend); coherence axis (#11) overlaps existing AERead Axis 5 metacog | **Tier B (v1)** |
| F13 | **Web browsing under budget** | BrowseComp / WebArena + budget constraint | Hidden = page-content distribution; oracle = optimal information acquisition under budget | Tests tool-use under economic constraint; deployment-relevant (research-assistant agents) | Web evaluation is messy (web changes, breakage); not finance-pure | **Tier C (v1.5)** |
| F14 | **Customer-service triage / escalation** | Standard CS lit | Hidden = customer urgency/value; oracle = expected-value-maximizing escalation policy | Massive deployment surface (every enterprise has this) | Hard to ground in objective outcomes without proprietary data | **Tier C (v1.5)** |
| F15 | **Market-Bench wrap** (procurement + retail competition + supply-chain balance-sheet trajectories) | Market-Bench 2026 ([arxiv 2604.05523](https://arxiv.org/abs/2604.05523)) | Hidden = competitor strategies + market state; oracle = profit-maximizing policy per environment | Direct overlap with AERead's economic-agent framing; published benchmark to wrap (similar pattern to TERMS-Bench / EconEvals wraps) | Multi-agent + multi-period; expensive simulator | **Tier A (v0.5)** — high-fit wrap candidate |
| F16 | **PolyBench live prediction-market forecasting + trading** | PolyBench 2026 ([arxiv 2604.14199](https://arxiv.org/abs/2604.14199)) | Hidden = true outcome distribution; oracle = Bayes-optimal forecast + Kelly-optimal trading | Contamination-resistant (live data); pairs naturally with Axis 5 calibration + Brier/CRPS scoring; pairs with C1 financial-decision framing | Requires live prediction-market data access; long-horizon validation | **Tier A (v0.5)** — high diagnostic value + clean ground truth |
| F17 | **AI-mediated commerce (role coherence + willingness-to-pay leakage)** | "When Agents Shop for You" 2026 ([arxiv 2604.26220](https://arxiv.org/abs/2604.26220)) | Hidden = principal's true preferences; oracle = principal-faithful purchase | Directly relevant to C2 product selection + agentic commerce deployment (Visa AI-agent platform, Anthropic Economic Index) | Methodologically harder to formalize the "role coherence" notion | **Tier B (v1)** — natural extension of C2 |

### G. Behavioral game ports

| # | Case | Source | OracleDecomposable hint | Pros | Cons | Priority |
|---|---|---|---|---|---|---|
| G15 | **Ultimatum game (iterated)** | Aher et al. 2023 ICML (Turing experiments) | Hidden = responder reservation value; oracle = subgame-perfect minimum-offer | Tests fairness-norm sensitivity; classic experimental game | Single-shot version is solved (offer ε); iterated more interesting but already studied | **Tier C (v1.5)** |
| G16 | **Trust game (multi-round)** | Berg-Dickhaut-McCabe 1995 + LLM replications | Hidden = trustee return policy; oracle = backward-induction equilibrium | Tests cooperation building; pairs with C4 PD as cooperation cluster | Same coverage as C4 effectively | **Tier D (parked)** — covered by C4 |
| G17 | **Allais paradox decision** | Allais 1953 + behavioral-econ lit | Hidden = agent's true risk attitude; oracle = expected-utility maximization (under chosen functional class) | Direct test of Layer 1 independence axiom in deployment context | Pure behavioral test; doesn't add deployment relevance | **Tier D (parked)** — covered by B1 risk in Cat B |
| G18 | **Insurance / risk pooling** | Standard insurance lit | Hidden = loss-distribution parameters; oracle = risk-adjusted premium | Real deployment (auto insurance, P&C); tests B1 risk preferences in context | Heavy actuarial structure; specialized | **Tier C (v1.5)** |

## Top selection priority (recommended additions beyond v0)

If we add cases after shipping v0 (C2 ProductProcurementGame + D3 VendorSelectionGame), this is the recommended priority order for v0.5+ expansion (which also reintegrates the roadmap items: D2 TERMS-Bench wrap, C1 persona-fit, agentic marketplace, NegotiationGame, PricingCompetitionGame):

| Rank | Code | Case | Justification |
|---|---|---|---|
| 1 | A2 | EconEvals pricing | Highest dollar-value deployment; calibration directly leaks revenue; mutual citation benefit with Harvard |
| 2 | A1 | EconEvals procurement | Already published; cleanest wrap; extends C2 generalization story |
| 3 | B1 | Repeated pricing / collusion (Calvano-style) | Pairs with A2 for the regulator story; LLM-collusion is novel + topical |
| 4 | D8 | Weather/event probability forecasting | Pairs with Axis 5 calibration; gives Zhu-Griffiths probe set a natural home |
| 5 | C7 | Multi-issue negotiation | Extends D2 (bilateral price) to multi-attribute; enterprise-realistic |
| 6 | A6 | Two-sided matching (Gale-Shapley + strategic reporting) | Roth-anchored; school-choice + residency are real deployments |
| 7 | A3 | EconEvals scheduling | Completes the EconEvals wrap trio; Hungarian gives clean oracle |
| 8 | F12 | Vending-Bench (long-horizon coherence) | Tests something no other AERead case tests (20M+ token coherence) |
| 9 | A4 | Sealed-bid auction | Mechanism-design hook for §10; first/second-price comparison is instructive |
| 10 | B2 | Dynamic pricing under competition | If A2 + B1 land successfully, this is the natural v1.5 extension |
| 11 | F15 | Market-Bench wrap (procurement + retail + supply-chain) | Published competitor benchmark; direct overlap with AERead economic-agent framing — same wrap pattern as TERMS-Bench / EconEvals |
| 12 | F16 | PolyBench live prediction-market forecasting + trading | Contamination-resistant; clean Bayes-optimal oracle; pairs with Axis 5 calibration + C1 financial-decision framing |

**Tier S → A → B → C → D mapping**:
- **S (v0, shipping)**: C2 ProductProcurementGame + D3 VendorSelectionGame (the two v0 first-paper games)
- **A (v0.5, ~3-4 months post-launch)**: D2 TERMS-Bench wrap + C1 persona-fit (Layer 2 case) + A1 EconEvals procurement + A2 EconEvals pricing + B1 collusion + F15 Market-Bench + F16 PolyBench (substrate also adds NegotiationGame + PricingCompetitionGame here)
- **B (v1, ~6 months post-launch)**: A3, A4, A6, C7, D8, F12, F17, agentic marketplace extension
- **C (v1.5, ~9-12 months post-launch)**: A5, B2, B3, C3, C4, C5, D9, D10, F13, F14, G15, G18
- **D (parked, may never ship)**: A7, C6, E11, G16, G17

## Open questions for the candidate pool

1. **Which v0.5 case do we wrap first** — A2 pricing (highest dollar-value, but EconEvals pricing's OracleDecomposable cleanliness needs validation) or A1 procurement (already cleanly OracleDecomposable, but lower revenue-narrative leverage)?
2. **Do we batch all EconEvals wraps (A1+A2+A3) together** for a single "AERead wraps EconEvals" announcement, or stagger to build distinct momentum?
3. **Calvano-style multi-round collusion (B1)** — do we need primary data (real oligopoly histories) or can we run synthetic + cite Calvano? Affects feasibility timing.
4. **Vending-Bench (F12)** — wrap their runtime as-is, or run our own long-horizon eval? Affects whether we're in their citation graph or vice versa.
5. **Forecasting cases (D8/D9/D10)** — these are calibration-heavy and natural for Axis 5; but do they belong in Layer 3 (real cases) or as standalone Axis 5 probe-set extensions? Borderline.

## Source-paper attribution

All candidates traced to papers in this repo's bibliography. Drill-down references:

- **Zhang et al. 2026 TERMS-Bench** → D2 (already in v2), informs D8/D9/D10 forecasting framework
- **Fish/Gonczarowski 2026 EconEvals** → A1, A2, A3
- **Calvano et al. 2020 AER + Fish et al. 2024** → B1, B2
- **Piatti et al. 2024 NeurIPS** → C3 commons
- **Akata et al. 2025 Nature Human Behaviour** → C4 PD
- **Huang et al. 2025 ICLR (γ-Bench)** → C5 multi-agent coord
- **Hart 1992 + Cooperation-or-Collapse** → C6 coalitional
- **Banchio & Skrzypacz 2022 EC** → A4, A5 auctions
- **Gale & Shapley 1962 + Roth lit** → A6 matching
- **Zhu & Griffiths 2024** → D8 weather
- **Qiu et al. 2026** → D9 elections (Bayesian teaching context)
- **Aher et al. 2023 ICML** → G15 ultimatum
- **Backlund & Petersson 2025 Vending-Bench** → F12

Full bibliographic metadata in [`papers/references_master.yaml`](papers/references_master.yaml); curated annotations in [`papers/_INDEX.md`](papers/_INDEX.md).
