# AERead build lab

This copy contains a runnable research scaffold for the current AERead direction.
It is deliberately small and judge-free: task generators expose symbolic ground
truth to the harness, model-visible prompts do not expose oracle answers,
scoring is mechanical, and live API use is restricted to OpenAI model aliases
only.

Current source-doc alignment: the 2026-05-30 refocus/methodology sharpening says
saturation is a `(primitive x regime)` property and tracks oracle availability
under stress, not agent count. Where omniscient optima are not a fair agent bar,
the lab scores against accessible posterior/control targets, local oracles,
proper scoring, bounds, and revealed-preference fit.

## What is implemented

| Build | Why it matters | Command |
|---|---|---|
| `regime` | Four-regime utility battery across even-money, skewed, thin-edge, negative-EV, and hard-barrier gamble families: EV single-shot, Kelly compounding, CVaR under ruin, configured-principal CRRA. This is the re-centered regime-appropriateness axis. | `python -m aeread_lab.cli --task regime --agent offline:oracle` |
| `alignment_tax` | RLHF-appropriateness probe: all listed actions are compliant, but the helpful/customer-approved default can sacrifice configured economic value. | `python -m aeread_lab.cli --task alignment_tax --agent offline:oracle` |
| `principal_inference` | Grade-side revealed-preference task: infer a principal's CRRA risk parameter from prior choices before allocating in a new scenario. | `python -m aeread_lab.cli --task principal_inference --agent offline:oracle` |
| `portfolio` | Multi-asset configured-principal allocation: choose portfolios using CRRA-style variance, tail risk, concentration, and mandate-fit terms. | `python -m aeread_lab.cli --task portfolio --agent offline:oracle` |
| `revealed_allocation` | Stylized 13F-style revealed-preference allocation: infer risk preference from historical portfolio choices, then output continuous target weights. | `python -m aeread_lab.cli --task revealed_allocation --agent offline:oracle` |
| `ambiguity` | Knightian uncertainty task: maxmin and alpha-maxmin choice across plausible priors, with optional signal updates instead of collapsing to one reference prior. | `python -m aeread_lab.cli --task ambiguity --agent offline:oracle` |
| `bargaining` | D2/TERMS-style gate+grade wrapper: generic seller surplus extraction vs configured-principal surplus sharing across take-it-or-leave-it, alternating-offer, and hidden-reservation cases. | `python -m aeread_lab.cli --task bargaining --agent offline:oracle` |
| `belief_bargaining` | TERMS-style cue use and belief calibration: update buyer WTP beliefs from one-shot cues and multi-turn signal sequences before pricing. | `python -m aeread_lab.cli --task belief_bargaining --agent offline:oracle` |
| `market` | Market-Bench-style price competition plus inventory-survival pricing: competitive Nash pricing vs collusive/high-price drift, liquidation, and reserve-aware inventory pricing. | `python -m aeread_lab.cli --task market --agent offline:oracle` |
| `matching` | Matching-market design: choose stable/access-aware matching rules instead of value-only assignments with blocking-pair risk. | `python -m aeread_lab.cli --task matching --agent offline:oracle` |
| `screening` | Adverse-selection contract screening: choose incentive-compatible/participation-safe menus instead of profit-only menus. | `python -m aeread_lab.cli --task screening --agent offline:oracle` |
| `moral_hazard` | Hidden-action contract design: choose incentive contracts that actually induce effort instead of assuming first-best effort for free. | `python -m aeread_lab.cli --task moral_hazard --agent offline:oracle` |
| `auction` | Mechanism-design reserve task: Myerson revenue reserve vs welfare/access reserves under configured objectives. | `python -m aeread_lab.cli --task auction --agent offline:oracle` |
| `common_value` | Winner's-curse auction guardrail: condition on winning as adverse information instead of bidding from a private signal as if it were private value. Live smoke: smaller OpenAI models miss; `gpt-5.5` solves. | `python -m aeread_lab.cli --task common_value --agent offline:oracle` |
| `mechanism` | Mechanism-choice task: choose among auction/allocation rules using configured principal weights, strategic-risk penalties, and incentive-compatibility checks. | `python -m aeread_lab.cli --task mechanism --agent offline:oracle` |
| `strategic_drift` | γ-Bench-style repeated strategic discipline: preserve long-horizon relationship value under deterministic, imperfect-information, and N-player stress instead of drifting to myopic grabs. | `python -m aeread_lab.cli --task strategic_drift --agent offline:oracle` |
| `exploration` | EconEvals-style unknown-environment learning: decide when information value justifies a pilot before deployment. | `python -m aeread_lab.cli --task exploration --agent offline:oracle` |
| `experiment_design` | Imperfect-signal experiment design: choose whether and how to run one-step or adaptive two-step noisy experiments before deployment, then update by Bayes rule. | `python -m aeread_lab.cli --task experiment_design --agent offline:oracle` |
| `retail` | Vending-Bench-style inventory/runway management: one-cycle and multi-period demand paths with carrying costs, terminal salvage, and reserve checks at every period. | `python -m aeread_lab.cli --task retail --agent offline:oracle` |
| `procurement` | v0 `ProductProcurementGame`: discrete-action qualitative procurement with a utility-vector oracle. | `python -m aeread_lab.cli --task procurement --agent offline:oracle` |
| `pricing` | v0 `SimplePricingGame`: continuous price choice with base/posterior/reveal conditions and a closed-form revenue oracle. | `python -m aeread_lab.cli --task pricing --agent offline:oracle` |
| `scam` | Adversarial belief-manipulation arena: scam-supplier style value inflation with credulous and skeptical controls. | `python -m aeread_lab.cli --task scam --agent offline:careful --attacker offline:credulous` |
| `supplier_scam` | Long-horizon supplier-scam stress: repeated restocking under cash/runway constraints, where inflated supplier claims and delayed-inventory lockups must be discounted. | `python -m aeread_lab.cli --task supplier_scam --agent offline:oracle` |

## OpenAI-only API path

The only live API adapter is `aeread_lab.models.OpenAIResponsesAgent`. It accepts
only these aliases:

- `gpt-5.5`
- `mini` (defaults to `gpt-5.4-mini`; override with `AEREAD_OPENAI_MODEL_MINI`)
- `nano` (defaults to `gpt-5.4-nano`; override with `AEREAD_OPENAI_MODEL_NANO`)

Example:

```bash
OPENAI_API_KEY=... python -m aeread_lab.cli --task regime --agent openai:nano
```

Run the full OpenAI-only model sweep with:

```bash
OPENAI_API_KEY=... python -m aeread_lab.cli --sweep --task all \
  --agents openai:gpt-5.5,openai:mini,openai:nano
```

There is no Anthropic/OpenRouter path in this build lab.

The adapter uses low reasoning effort, low text verbosity, `store=false`, and a
4096-token output budget by default. It raises on incomplete or textless responses
instead of silently scoring blank model outputs.

## Sweep runner and cache

The sweep runner compares agents on the primary mechanical metric for each task:
it also reports `parse`, the fraction of trials with a valid task-specific
`FINAL_*` answer. Treat low parse rate as an eval-format failure before
interpreting the economic metric.

- `regime`: lower mean absolute error to the regime-correct oracle is better.
- `alignment_tax`: lower configured-objective regret is better; overconcession
  and helpful-default match rates are reported separately.
- `principal_inference`: lower fraction error to the revealed-principal oracle
  is better; generic-gamma gap is reported separately.
- `portfolio`: lower configured-principal utility regret is better; max-return
  and low-risk miss rates are reported separately.
- `revealed_allocation`: lower utility regret and lower weight L1 error to the
  revealed-principal allocation are better.
- `ambiguity`: lower configured ambiguity regret is better; reference-prior,
  pure-maxmin, and optimistic miss rates are reported separately.
- `bargaining`: lower configured-principal grade error is better; generic gate
  surplus gap, alternating-offer miss rate, and hidden-reservation miss rate are
  reported separately.
- `belief_bargaining`: lower posterior expected-surplus gap is better; cue
  switch miss rate and multi-turn miss rate are reported separately.
- `market`: lower competitive/survival oracle price gap is better; collusion
  index, reserve-violation rate, survival cash gap, and liquidation miss rate
  are reported separately.
- `matching`: lower configured matching score regret is better; max-value and
  access-only miss rates are reported separately.
- `screening`: lower configured contract-menu regret is better; max-profit and
  constraint-blind miss rates are reported separately.
- `moral_hazard`: lower realized principal-profit regret is better; hidden-action
  blind and high-bonus miss rates are reported separately.
- `auction`: lower reserve-price error to the objective-specific mechanism
  oracle is better.
- `common_value`: lower expected-profit regret is better; winner's-curse miss
  and negative-profit rates are reported separately.
- `mechanism`: lower configured score regret is better; revenue-default,
  risk-blind, and IC-blind miss rates are reported separately.
- `strategic_drift`: lower long-horizon drift rate is better; stress-case drift
  and myopic-miss rates are reported separately for imperfect-information and
  N-player cases.
- `exploration`: lower expected-value gap is better; exploration miss rate is
  reported separately.
- `experiment_design`: lower expected-value gap is better; experiment miss and
  multi-step adaptation miss rates are reported separately.
- `retail`: lower order error to the survival/cash oracle is better; ruin
  probability, expected cash gap, myopic-order gap, multi-period cash gap, and
  multi-period miss rate are reported separately.
- `procurement`: higher oracle-choice accuracy is better.
- `pricing`: lower revenue gap to the closed-form optimum is better.
- `scam`: lower mean overpayment is better.
- `supplier_scam`: lower constrained final-cash regret is better; raw final-cash
  regret, reserve violation, scam-supplier rate, and timing-reserve violation
  are reported separately.

Offline comparison example:

```bash
python -m aeread_lab.cli --sweep --task all \
  --agents offline:oracle,offline:ev --no-cache
```

Live OpenAI responses are cached under `.aeread-cache/responses/` by default.
Use `--cache-dir <path>` to relocate the cache or `--no-cache` to force fresh
calls. Offline agents do not need the cache and never call the API.

Use `--limit N` for cheap smoke checks against the first `N` deterministic
cases/gambles before running a broad task. For example:

```bash
OPENAI_API_KEY=... python -m aeread_lab.cli --sweep --task regime \
  --agents openai:mini,openai:nano --limit 1
```

## Validation

Run offline validation without API spend:

```bash
python -m unittest discover -s tests
python -m aeread_lab.cli --task all --agent offline:oracle
python -m aeread_lab.cli --sweep --task regime \
  --agents offline:oracle,offline:ev --no-cache
```

## Expansion order

The next builds should keep the same discipline: add a deterministic generator,
a mechanical oracle, a no-API baseline, then a thin OpenAI run path.

1. Run full or stress-targeted live OpenAI probes on the cases where sampled
   smokes show parse stability but no separation.
2. Extend mechanism/market probes toward repeated-policy or opponent-policy
   simulation instead of another static scoring field.
3. Add adaptive vendor-reputation updates to `supplier_scam` instead of another
   static supplier option list.
4. Replace the stylized revealed-allocation traces with real 13F-style
   holdings-derived traces once a clean data source is selected.
5. Run full or stress-targeted live OpenAI probes where new stress cases parse
   cleanly but show only small separation.
