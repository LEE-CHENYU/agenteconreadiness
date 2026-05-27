# Cited Papers — Curated Index (deep-dive synopses)

Auto-extracted bibliographies from the 3 anchor papers (TERMS-Bench / EconEvals / Revealed Rationality).
Master list: [`references_master.yaml`](references_master.yaml) (160 entries). Three PDFs in [`pdfs/`](pdfs/) for papers without public URLs (Andrews 2026, Chadwick 2025, Gneiting & Raftery 2007); the rest are accessible via the arxiv/DOI links in this file or via [`links.md`](links.md). The full PDF collection (53 papers) lives in the source repo (`rationale`) — request access from Cheney if you need drill-down (see proposal §15 "Available on request").
Generated: 2026-05-26 (refreshed 2026-05-26 with cross-doc clarification).

**Relationship to other reference docs**:

- [`references_master.yaml`](references_master.yaml) — **master machine-readable bibliography** (160 entries, full metadata)
- [`../reading_list.txt`](../reading_list.txt) — **priority list** with T1/T2/T3 tiers, [AXIS-N] anchor tags, per-paper one-line rationales, + reading-paths-by-role; lists ~14 T1 papers including the 3 anchor benchmarks AERead integrates (TERMS-Bench / Andrews 2026 / EconEvals)
- **THIS file (`_INDEX.md`)** — **deep-dive curated synopses** for ~12 supporting-literature papers (multi-agent, cognitive-modeling, mechanism-design); does NOT re-synopsize the 3 anchor benchmarks because they are covered in detail in [`../proposal.md`](../proposal.md) §1-§3 + [`../methodology.md`](../methodology.md)
- [`links.md`](links.md) — **URL accessibility layer** for every cited paper

Each doc serves a different question. Use this file when you want 5-6 paragraphs of analysis + AERead-relevance discussion for one of the 12 papers below; use `reading_list.txt` when you want "what should I read first?"

Anchor abbreviations used below reference the master plan (in the source repo): **§1.5.X** = methodology subsections; **§7.AX/BX/CX** = dimension implementations; **§15.6** = oracle-gap decomposition; **§17** = commercial-tier model; **D2/D3** = v2 dimension candidates currently in scope (bargaining, agentic vendor selection — see proposal §2 and [`../layer3_candidates.md`](../layer3_candidates.md) for the full open pool).

---

## Tier 1: Read in full (deep-dive synopses — supporting literature)

Twelve papers that directly inform the methodology paper's §2 (related work) or §3 (test-design choices), or whose findings AERead adopts as ground truth for a specific dimension's design. **The 3 anchor benchmarks AERead integrates** (TERMS-Bench / Andrews 2026 / EconEvals) are NOT re-synopsized here — they are covered in [`../proposal.md`](../proposal.md) §1-§3 and listed first in [`../reading_list.txt`](../reading_list.txt) T1. This index complements that coverage by providing depth on the surrounding literature.

### 1. STEER: Assessing the Economic Rationality of Large Language Models (Raman et al., 2024)
- arxiv: [2402.09552](https://arxiv.org/abs/2402.09552) | category: llm_rationality_core
- Authors: Raman, Lundy, Amouyal, Levine, Leyton-Brown, Tennenholtz (UBC / Tel Aviv / Stanford / AI21 / Technion)
- **Synopsis.** Surveys the economic-rationality literature and decomposes "rational agent" into a taxonomy of fine-grained "elements" with explicit dependencies between them. Proposes STEER, a tuneable benchmark distribution that scores LLMs against each element and combines those scores with a user-supplied rubric into an aggregate rationality score. This is the closest prior art to the AgentEcon Readiness thesis: a multi-dimensional benchmark of LLM economic rationality with a deliberately modular score.
- **AgentEcon Readiness relevance.** Direct ancestor of our §1.5.2 three-layer hierarchy (axiom→parameter→outcome). STEER's "elements + dependencies" decomposition is the structural template we extend by adding (a) cardinal calibration via persona-fit (§7.C1) that STEER does not address, (b) context-conditional axiomatization (§1.5.5, D1) that resolves STEER's all-or-nothing-axiom problem, and (c) judge-free scoring (§1.5.7). Must cite as the primary "what's different about AgentEcon Readiness" anchor in §2.

### 2. Economic Rationality under Specialization (Wen, 2025)
- arxiv: [2501.18190](https://arxiv.org/abs/2501.18190) | category: llm_rationality_core
- Author: ShuiDe Wen (Tsinghua Shenzhen)
- **Synopsis.** Extends Chen et al. (2023) by running budget-allocation and risk experiments on persona-specialized GPT agents (biotech expert, economist) vs. the generic base model. Finds that specialization *degrades* economic rationality: more GARP violations, lower CCEI, larger deviations under high-risk conditions. Coins "rationality shift" as the conflict between domain specialization and axiomatic compliance.
- **AgentEcon Readiness relevance.** This is the canonical anchor for §1.5.5 (context-conditional axiomatization) — the empirical evidence that compliance with classical axioms is *not* context-invariant when LLMs are given a role, persona, or domain. Resolves the §7.A1/A2/A3 design problem of "do we test on generic or persona-conditional prompts?" Answer: both, and the gap between them *is* a measurable dimension (D1). Cite in §1.5.5 opener and again in §7.C1 motivation.

### 3. Recovering Event Probabilities from LLM Embeddings via Axiomatic Constraints (Zhu, Yan, Griffiths, 2025)
- arxiv: [2505.07883](https://arxiv.org/abs/2505.07883) | category: llm_rationality_core
- Authors: Jian-Qiao Zhu (Princeton), Haijiang Yan (Warwick), Tom Griffiths (Princeton)
- **Synopsis.** LLM-emitted event probabilities violate basic probability axioms (additivity, complementarity). Authors train a VAE on LLM embeddings with an additivity-constraint penalty and recover probabilities from the latent space that are more coherent and closer to ground truth than the model's verbal outputs. Demonstrates that representations encode coherent beliefs even when token-level outputs do not.
- **AgentEcon Readiness relevance.** Foundational for §1.5.6 (measurement-model pluralism) and §15.6 (oracle-gap decomposition). Direct evidence that a model can fail the axiom on emitted output while satisfying it in representation space — i.e., the gap between "capability" and "elicited behavior" is real and measurable. Justifies why we need both verbal and representation-level measurement models in §7.A* dimensions. Pair with paper #11 (Yamin et al.) below.

### 4. Sparks of Rationality: Do Reasoning LLMs Align with Human Judgment and Choice? (Tak et al., 2026)
- arxiv: [2601.22329](https://arxiv.org/abs/2601.22329) | category: llm_rationality_core
- Authors: Tak, Banayeeanzade, Bolourani, Bahrani, Chaubey, Karimireddy, Schwarz, Gratch (USC / ICT)
- **Synopsis.** Evaluates reasoning-enabled LLMs (with thinking modes, in-context priming, and rep-level steering) on (i) classical axioms of rational choice and (ii) behavioral-economics decision domains (Allais, framing, certainty effects). Finds reasoning mode shifts models toward EU-maximizing answers and away from human-like biases — a dual-process pattern.
- **AgentEcon Readiness relevance.** Direct evidence for §1.5.1 (descriptive-vs-normative split): the *same* model can be tuned by thinking-budget toward either rational-axiom compliance or human-like bias replication. Cite in §1.5.1 to motivate why we score both axes separately, and in §7.B1/B2/B3 to justify reporting thinking-mode-on and thinking-mode-off conditions side by side. Most recent (Jan 2026) and directly germane.

### 5. When Agents Say One Thing and Do Another: Validating Elicited Beliefs from LLMs (Yamin et al., 2026)
- arxiv: [2602.06286](https://arxiv.org/abs/2602.06286) | category: llm_rationality_core
- Authors: Yamin, Tang, Cortes-Gomez, Sharma, Horvitz, Wilder (CMU / Microsoft Research)
- **Synopsis.** Decision-theoretic framework that elicits both probability judgments and decisions from an LLM and tests internal consistency: is there *any* near-rational utility function that rationalizes the action given the stated belief? The framework is utility-free (no assumption on the utility shape). Applied to clinical-diagnosis tasks; finds frontier models' belief reports are imperfect summaries of decision-revealed information, but the gap is small for strong models.
- **AgentEcon Readiness relevance.** This is the methodological anchor for §1.5.7 (judge-free by design): rationality testing without assuming a specific utility shape. The "is there *any* utility that rationalizes the data" framing is exactly the inverse-revealed-preference logic we adopt in §7.C1 (persona-fit) and the consistency tests across dimensions. Adopt their consistency-testing framework directly. Also direct support for §15.6 (oracle-gap intervention decomposition) — emitted-vs-revealed gap is their core finding.

### 6. Utility Engineering: Analyzing and Controlling Emergent Value Systems in AIs (Mazeika et al., 2025)
- arxiv: [2502.08640](https://arxiv.org/abs/2502.08640) | category: llm_rationality_core
- Authors: Mazeika et al. (Center for AI Safety / Penn / Berkeley) — Hendrycks group
- **Synopsis.** Tests whether independently-sampled LLM preferences form coherent utility functions. Surprising finding: structural coherence increases with model scale; frontier models exhibit measurable, stable utility functions over outcomes. Documents specific "shocking" preferences (e.g., AIs valuing themselves over humans). Proposes "utility engineering" — controlling emergent utilities, demonstrated on political-bias reduction via citizen-assembly alignment.
- **AgentEcon Readiness relevance.** Foundational for §7.A1 (transitivity), §7.A2 (monotonicity), and the entire Category A premise. Provides the empirical claim ("LLMs *do* have coherent utilities at scale") that justifies measuring axiom compliance as a meaningful signal rather than noise. Cite as the affirmative evidence in §1.5.1 ("descriptive prong is non-empty"). Also relevant to §17 commercial tiers — utility-control diagnostics are an obvious paid feature for alignment teams.

### 7. Algorithmic Collusion by Large Language Models (Fish, Gonczarowski, Shorrer, 2024)
- arxiv: [2404.00806](https://arxiv.org/abs/2404.00806) | category: llm_rationality_core
- Authors: Fish (Harvard), Gonczarowski (Harvard Econ+CS), Shorrer (Penn State)
- **Synopsis.** LLM-based oligopoly pricing agents quickly and autonomously settle into supracompetitive collusive prices, with the equilibrium sensitive to seemingly innocuous prompt variations ("price-war concerns" framing increases collusion). Result extends to auctions. Establishes that LLM agents *behaviorally* deviate from competitive Nash and that prompt phrasing materially shapes equilibrium selection.
- **AgentEcon Readiness relevance.** Anchor for §1.5.3 (prompt-sensitivity is a measurement problem, not just noise) and §17 Tier 3 (regulatory/policy diagnostics). The strongest empirical case for why benchmarks must hold prompts constant across models — and conversely why prompt-sensitivity scoring is itself a useful dimension. Also directly motivates D2 wrap of TERMS-Bench: bargaining behavior depends on identical content-bearing factors. Cite in §1.5.3 and §7.B3 (social preferences / strategic interaction).

### 8. EconAgents at Auction Arena: Put Your Money Where Your Mouth Is (Chen et al., 2024)
- arxiv: [2310.05746](https://arxiv.org/abs/2310.05746) | category: llm_as_economic_agent
- Authors: Jiangjie Chen et al. (Fudan + AI2)
- **Synopsis.** AucArena — multi-round auctions as a benchmark for LLM agent planning, budget management, risk-management, and goal-adherence. Finds GPT-4 has the key skills but variance is high and simpler heuristic baselines sometimes outperform. Establishes auctions as a tractable strategic environment for LLM evaluation.
- **AgentEcon Readiness relevance.** Direct precedent for §7.B1 (risk preferences elicited in resource-constrained multi-round play) and D3 (agentic tool selection — bidding-as-tool-choice). The "GPT-4 sometimes loses to simple heuristics" finding is critical: it bounds the ceiling effect claim in §7.A1 — frontier models are not uniformly dominant on strategic tasks even when they pass axiomatic checks. Cite in §7.A1 ceiling-effect treatment and §7.B1 sizing-under-uncertainty implementation.

### 9. How Far Are We on the Decision-Making of LLMs? (Huang et al., 2025)
- arxiv: [2403.11807](https://arxiv.org/abs/2403.11807) | category: llm_as_economic_agent
- Authors: Huang et al. (CUHK / Tencent AI Lab) — γ-Bench
- **Synopsis.** γ-Bench: eight classical game-theory scenarios in multi-agent settings, with a dynamic scoring scheme that adapts to game parameters (test-set leakage-resistant). Evaluates 13 LLMs across 6 families. Best score 69.8/100 (Gemini-1.5-Pro). Decomposes robustness vs generalizability separately.
- **AgentEcon Readiness relevance.** Methodological precedent for §1.5.4 (leakage-resistance via dynamic instance generation) and §7.B3 (social preferences via game theory). Their robustness/generalizability decomposition maps cleanly onto our prompt-sensitivity and OOD scoring. Best-model 70/100 finding is the empirical scaffold for our §17 Tier 1 free-tier headline-number positioning (multi-dim score with no model saturated). Cite in §1.5.4 and §7.B3.

### 10. Cooperate or Collapse: Sustainable Cooperation in a Society of LLM Agents (Piatti et al., 2024)
- arxiv: [2404.16698](https://arxiv.org/abs/2404.16698) | category: llm_as_economic_agent
- Authors: Piatti, Jin, Kleiman-Weiner et al. (ETH / MPI / Toronto / UW / Michigan) — GovSim
- **Synopsis.** Multi-agent commons-governance simulation. Finds that all but the most powerful LLMs fail to reach sustainable cooperation (survival rate <54%); failure traced to inability to formulate and reason about long-term equilibrium effects. "Universalization" prompting (Kantian-style moral reasoning) significantly improves outcomes.
- **AgentEcon Readiness relevance.** Anchor for §7.B3 (social preferences / cooperation) and v2 D2 bargaining. Demonstrates a clean dimension where capability differences across frontier models are *large* (not ceiling-effected) — useful for §1.5.4 design discussion. Universalization-prompting result also motivates §1.5.3 prompt-conditional scoring. Cite in §7.B3 and v2 D2 motivation.

### 11. Cognitive Models Can Reveal Interpretable Value Trade-offs in LLMs (Murthy et al., 2026 ICLR)
- arxiv: [2506.20666](https://arxiv.org/abs/2506.20666) | category: alignment_values
- Authors: Murthy, Zhao, Hu, Kakade, Wulfmeier, Qian, Ullman (Harvard Kempner / DeepMind / Harvard Psych)
- **Synopsis.** Adapts the polite-speech cognitive model (Bayesian utility-weighting of competing speaker goals) to LLMs. Recovers stable utility-weight profiles per model. Shows: (a) profiles shift predictably with prompt-stated goals, (b) reasoning budgets amplify shifts, (c) profiles diagnose sycophancy. Tracks post-training dynamics: large shifts early, persistent base-model effects, alignment method matters less than feedback dataset.
- **AgentEcon Readiness relevance.** Foundational for §1.5.6 (measurement-model pluralism). This is the cleanest demonstration that a *cognitive-model* measurement layer recovers interpretable parameters that token-level scoring misses. Adopt their utility-weight recovery as one of the canonical measurement models in §7.A1/A2/A3. Also relevant to §7.C1 (persona-fit) since their per-model utility weights are exactly the "implicit values" we infer in our persona dimension. Cite in §1.5.6 opener and §7.C1 measurement-model selection.

### 12. Using LLMs to Simulate Multiple Humans and Replicate Human Subject Studies (Aher, Arriaga, Kalai, 2023)
- arxiv: [2208.10264](https://arxiv.org/abs/2208.10264) | category: llm_as_economic_agent
- Authors: Aher (Olin), Arriaga (Georgia Tech), Kalai (Microsoft Research)
- **Synopsis.** Turing Experiments — replicate Ultimatum Game, Garden Path Sentences, Milgram, Wisdom of Crowds with LLMs simulating populations. First three replicate classic findings; Wisdom of Crowds reveals "hyper-accuracy distortion" (LLMs over-perform on factual tasks compared to human samples).
- **AgentEcon Readiness relevance.** Methodological precedent for §7.C1 (persona-fit calibration) — using LLMs to simulate distributions of human respondents and validating against known experimental ground truth. Hyper-accuracy distortion is a key threat-model: persona-conditioned LLMs may over-perform on calibration tasks if they recognize the task structure. Cite in §7.C1 threat-model discussion and §1.5.7 judge-free motivation (judges may be hyper-accurate in different directions per model).

---

## Tier 2: Read selectively (relevant to specific dimensions or v2 extensions)

### LLM-rationality and game theory

**Alympics: LLM Agents Meet Game Theory** (Mao et al., 2024; 2311.03220). Water Allocation Challenge: multi-round auction over scarce resources. Demonstrates LLM agents emulating human strategic behavior in survival-resource bargaining. Cite in §7.B3 and v2 D2; useful for designing high-stakes resource-allocation tasks.

**GTBench: Strategic Reasoning Limitations of LLMs** (Duan et al., 2024; 2402.12348). 10 board/card games across complete/incomplete, dynamic/static, probabilistic/deterministic taxonomy. Finds LLMs fail in deterministic-complete-information games yet compete well in probabilistic ones; code pre-training helps; CoT and ToT don't always help. Maps directly to §1.5.6 — different measurement models needed across game types. Cite in §7.B3 and §1.5.6.

**Automated Social Science** (Manning, Zhu, Horton, 2024; 2404.11794). LLM-based structural causal models for in-silico social-science experiments (negotiation, bail hearing, job interview, auction). Key finding: LLMs can predict signs but not magnitudes; predictions improve when conditioned on the fitted SCM. Useful for §7.C1 measurement and v2 D2; cite as evidence that LLMs "know more than they can tell" (motivates representation-level measurement in §1.5.6).

**Can LLMs Explore In-Context?** (Krishnamurthy et al., 2024; 2403.15371). Bandit-exploration experiments find LLMs do not robustly explore without external scaffolding. Only GPT-4 + CoT + externally-summarized history succeeded. Cite in §7.B1 (sequential risk) and §15.6 (intervention decomposition — what scaffolding closes the gap?).

**NegotiationArena** (Bianchi et al., 2024; 2402.05863). Ultimatum, trading, price-negotiation scenarios; LLMs can boost payoffs ~20% via behavioral tactics (e.g., "desolate" framing). Quantifies LLM irrational negotiation behaviors. Cite in v2 D2 (bargaining wrap) and §7.B3.

**Measuring Bargaining Abilities of LLMs** (Xia et al., 2024; 2402.15813). AmazonHistoryPrice dataset; formalizes bargaining as asymmetric incomplete-information game. Finds buyer is much harder than seller; size doesn't fix buyer-side. OG-Narrator (deterministic price + LLM verbalizer) raises buyer deal-rate from 26% to 88%. Cite in v2 D2 implementation; direct precedent for the §7 design pattern "deterministic engine + LLM verbalizer."

**Game-theoretic LLM: Agent Workflow for Negotiation Games** (Hua et al., 2024; 2411.05990). Workflow framework for complete-information and incomplete-information negotiation games. Cite in v2 D2; useful for agent-architecture design but less for benchmark design.

**AgenticPay** (Liu, Gu, 2026; 2602.06008). Multi-agent buyer-seller benchmark with 110+ tasks spanning bilateral bargaining to many-to-many markets. Most recent of the bargaining benchmarks. Cite in v2 D2 as the closest large-scale precedent we'd wrap.

**MERIT Feedback** (Oh et al., 2026; 2602.10467). AGORABench with nine challenging bargaining settings (deception, monopoly); human-aligned utility-theory metrics (agent utility, negotiation power, acquisition ratio). Most recent (Mar 2026) of the bargaining benchmarks; metrics framework worth adopting in v2 D2.

**AgreeMate** (Chatterjee, Miller, Parepally, 2024; 2412.18690). Modular bargaining architecture, prompt-engineering + fine-tuning ablations; attention-probing analysis. Less central; cite in v2 D2 only if probing-based measurement is added.

**How Personality Traits Influence Negotiation Outcomes** (Huang, Hadfi, 2024; 2407.11549). Big-Five personality conditioning of buyer/seller agents; observes behavioral shifts with personality. Cite in §7.C1 as a persona-fit precedent (parameterized personality → measurable behavioral shift).

**Big Five and AI Capability Effects in LLM-Simulated Negotiation** (Cohen et al., 2025; 2506.15928). Sotopia testbed; agreeableness and extraversion affect believability/goal-achievement/knowledge-acquisition; AI transparency/competence/adaptability affect job-negotiation outcomes. Cite in §7.C1 and v2 D2; methodologically careful (causal discovery).

**Negotiating with LLMs: Prompt Hacks, Skill Gaps, Reasoning Deficits** (Schneider, Haag, Kruse, 2024; 2312.03720). 41-user human-vs-LLM price negotiation study. Documents prompt-hack vulnerabilities and the wide spread of human outcomes (literacy gap). Cite in §1.5.3 (prompt sensitivity) and v2 D2 robustness testing.

**Hierarchical Text Generation and Planning for Strategic Dialogue** (Yarats, Lewis, 2018; 1712.05846). Pre-LLM-era hierarchical-latent-variable model for negotiation; decouples semantics from realization. Background — useful citation for the modeling-history thread in v2 D2 but not core.

### LLM-as-economic-agent and behavioral

**Artificial Intelligence and Auction Design** (Banchio, Skrzypacz, 2022; 2202.05947). Q-learning agents in first-price vs second-price auctions: first-price tacitly collude, second-price don't. Cite in §7.B3 strategic-interaction section and §17 Tier 3 — auction-design diagnostics are a regulator/platform use case. Predates LLM era but mechanism insight transfers.

**Which Economic Tasks Are Performed with AI?** (Handa et al., 2025; 2503.04761). Anthropic analysis of 4M Claude conversations mapped to O*NET tasks/occupations. 36% of occupations use AI for >25% of tasks; 57% augmentation vs 43% automation. Cite in §17 commercial-model positioning (where the demand actually is) and §7 dimension-prioritization rationale.

**On the Fairness of Machine-Assisted Human Decisions** (Gillis, McLaughlin, Spiess, 2023; 2110.15310). Theoretical + lab evidence that omitting protected-group info from predictions can *increase* downstream disparities when a biased human makes the final call. Cite in §17 Tier 4 (regulator/audit positioning) and as a methodological caveat on §15.6 intervention decomposition — interventions interact with the human-in-the-loop.

**How Do LLMs Navigate Conflicts Between Honesty and Helpfulness?** (Liu, Sumers, Dasgupta, Griffiths, 2024; 2402.07282). Uses psychological models to test honesty/helpfulness tradeoff in LLMs. RLHF improves both; CoT skews toward helpfulness over honesty; GPT-4 Turbo shows human-like context sensitivity. Cite in §1.5.6 (cognitive-model measurement) and §7.B3 (social preferences over honesty).

**Promptable Behaviors** (Hwang et al., 2023; 2312.09337). Multi-objective RL with three preference-inference modes (demonstrations, comparisons, language). Embodied-AI focus, but the multi-objective-utility design pattern transfers. Cite only if §7.C1 needs an MORL precedent.

### Behavioral & ethical

**MACHIAVELLI Benchmark** (Pan et al., 2023; 2304.03279). 134 Choose-Your-Own-Adventure games, half a million labeled scenarios; measures power-seeking, disutility, ethical violations. Reward-maximizing RL agents are demonstrably Machiavellian; simple steering helps. Cite in §7.B3 (social preferences with ethical tradeoffs) and §17 Tier 4 (safety-aligned diagnostic).

**On the Meaning of the CCEI** (Echenique, 2022; 2109.06354). Critical methodological note: CCEI is hard to interpret, can disagree with other measures of irrationality, "wasted income" framing is questionable; one agent can have more unstable preferences yet higher CCEI. **Must cite in §7.A1** as the explicit caveat against using CCEI as the sole rationality metric — directly motivates §1.5.6 measurement-model pluralism (use multiple indices, not just CCEI).

### LLM-evaluation methodology

**Vending-Bench** (Backlund, Petersson, 2025; 2502.15840). Vending-machine simulation testing long-term coherence (>20M tokens per run). Finds high variance, "meltdown loops" uncorrelated with context-window fullness. Cite in §7.B2 (intertemporal — sustained decision quality across horizons) and §15.6 (degradation interventions).

**GDPval** (Patwardhan et al., 2025; 2510.04374). OpenAI's benchmark of 44 occupations across 9 GDP sectors; frontier models approaching expert quality on deliverables; scaling roughly linear in time. Cite in §17 (commercial positioning — economically grounded eval is the comparison reference) and §1.5.4 (real-world task design).

**TheAgentCompany** (Xu et al., 2025; 2412.14161). Benchmark of LLM agents in simulated office environment (browse, code, run, communicate). Best agent autonomously completes 30%. Cite in v2 D3 (agentic tool/vendor selection) as the closest precedent for agentic-economic-decision benchmarking at scale.

**FinanceBench** (Islam et al., 2023; 2311.11944). 10,231 finance QA pairs, 16 model configs tested. GPT-4-Turbo + retrieval still fails 81% on a 150-case sample. Cite in §7.C1 (financial-decision context) and §17 (finance-vertical positioning).

### LLM training (methodology context)

**DeepSeek-R1** (DeepSeek-AI, 2025; 2501.12948). Pure-RL training for reasoning emergence. Cite in §1.5.3 as the empirical case that reasoning *can* be incentivized without human reasoning traces — affects how we score reasoning-mode-on conditions in §7.A* and §7.B*.

**GEPA: Reflective Prompt Evolution** (Agrawal et al., 2026 ICLR Oral; 2507.19457). Prompt-evolution outperforms GRPO by 6-20% with 35x fewer rollouts. Cite in §1.5.3 (prompt sensitivity vs prompt optimization is itself a measurement axis) and §17 Tier 3 (intervention recommendations).

**Tülu 3** (Lambert et al., 2024; 2411.15124). Open post-training recipe. Background — cite in §1.5 only if discussing open-vs-closed-model comparability.

---

## Tier 3: Background / context (skim only)

- **PlanBench** (Valmeekam et al., 2022; 2206.10498) — Planning benchmark; LLM planning vs retrieval. Adjacent to §7.B2 sequential planning.
- **Voyager** (Wang et al., 2023; 2305.16291) — Minecraft lifelong-learning agent. Background on agentic capabilities; not core to economic rationality.
- **SWE-bench** (Jimenez et al., 2024; 2310.06770) — Code-engineering benchmark; methodology reference for real-world task curation only.
- **FrontierMath** (Glazer et al., 2025; 2411.04872) — Advanced math benchmark; ceiling-effect calibration reference.
- **ARC Prize 2024** (Chollet et al., 2024; 2412.04604) — Novel-task generalization benchmark; cite only if discussing benchmark-design philosophy.
- **Humanity's Last Exam** (Phan et al., 2026; 2501.14249) — Capability frontier benchmark; commercial-tier reference.
- **HumanEval / Codex** (Chen et al., 2021; 2107.03374) — Founding LLM-code benchmark; historical reference.
- **ReAct** (Yao et al., 2023; 2210.03629) — Reasoning + acting interleaving; background on agent architecture.
- **Toolformer** (Schick et al., 2023; 2302.04761) — Self-supervised tool use; background for v2 D3.
- **Writing-Zero** (Jia et al., 2025; 2506.00103) — RLVR for non-verifiable tasks via GenRM; background on judge-design tradeoffs.
- **Infrastructure for AI Agents** (Chan et al., 2025; 2501.10114) — Governance/protocol framing for agent ecosystems; background for §17 Tier 4 commercial positioning.
- **CyberSecEval 2** (Bhatt et al., 2024; 2404.13161) — LLM cybersecurity eval; reference for safety-utility tradeoff framing only.
- **Logical Induction** (Garrabrant et al., 2020; 1609.03543) — MIRI's logical-uncertainty framework; deep background for §1.5.6 measurement-model design — coherent-belief assignment as no-Dutch-book trading. Only cite if going formal on the coherence-axiom motivation.

---

## Skipped (no download)

- Books, classic 1950s-1970s economics papers (Nash, Savage, Knight, Afriat originals — DOI-only / paywalled / non-arxiv).
- Total: 9 not-downloadable + 96 without arxiv IDs (see `references_master.yaml`).

---

## Summary tally

- **Tier 1**: 12 papers (target was ~10-15) — STEER, Wen-specialization, Zhu-axiomatic-VAE, Tak-sparks, Yamin-belief-validation, Mazeika-utility-engineering, Fish-collusion, AucArena, γ-Bench, GovSim, Murthy-cognitive-models, Aher-Turing-experiments.
- **Tier 2**: 28 papers — bargaining/negotiation (14), LLM-as-economic-agent (5), behavioral & ethical (2), eval methodology (4), training context (3, with Tülu 3 borderline).
- **Tier 3**: 13 papers — broader context, skim only.
- **Total**: 12 + 28 + 13 = **53** of 53 downloaded.
- **Borderline / re-check**: *MACHIAVELLI*, *Vending-Bench*, *GDPval* were close calls between Tier 2 and Tier 3 — all kept in Tier 2 because they map to specific §7 or §17 sections. *Logical Induction* and *CyberSecEval 2* were close calls held in Tier 3. *Promptable Behaviors* held in Tier 2 as a borderline persona-precedent. *Tülu 3* in Tier 2 only as methodology context for open-model comparability.
