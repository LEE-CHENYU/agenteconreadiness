# AERead build lab

This copy contains a runnable research scaffold for the current AERead direction.
It is deliberately small and judge-free: task generators expose symbolic ground
truth to the harness, model-visible prompts do not expose oracle answers,
scoring is mechanical, and live API use is restricted to OpenAI model aliases
only.

## What is implemented

| Build | Why it matters | Command |
|---|---|---|
| `regime` | Four-regime utility battery: EV single-shot, Kelly compounding, CVaR under ruin, configured-principal CRRA. This is the re-centered regime-appropriateness axis. | `python -m aeread_lab.cli --task regime --agent offline:oracle` |
| `principal_inference` | Grade-side revealed-preference task: infer a principal's CRRA risk parameter from prior choices before allocating in a new scenario. | `python -m aeread_lab.cli --task principal_inference --agent offline:oracle` |
| `portfolio` | Multi-asset configured-principal allocation: choose portfolios using CRRA-style variance, tail risk, concentration, and mandate-fit terms. | `python -m aeread_lab.cli --task portfolio --agent offline:oracle` |
| `ambiguity` | Knightian uncertainty task: choose maxmin-robust actions across plausible priors instead of collapsing to one reference prior. | `python -m aeread_lab.cli --task ambiguity --agent offline:oracle` |
| `bargaining` | D2/TERMS-style gate+grade wrapper: generic seller surplus extraction vs configured-principal surplus sharing. | `python -m aeread_lab.cli --task bargaining --agent offline:oracle` |
| `belief_bargaining` | TERMS-style cue use and belief calibration: update buyer WTP beliefs from noisy cues before pricing. | `python -m aeread_lab.cli --task belief_bargaining --agent offline:oracle` |
| `market` | Market-Bench-style simultaneous price competition: competitive Nash pricing vs collusive/high-price drift. | `python -m aeread_lab.cli --task market --agent offline:oracle` |
| `matching` | Matching-market design: choose stable/access-aware matching rules instead of value-only assignments with blocking-pair risk. | `python -m aeread_lab.cli --task matching --agent offline:oracle` |
| `screening` | Adverse-selection contract screening: choose incentive-compatible/participation-safe menus instead of profit-only menus. | `python -m aeread_lab.cli --task screening --agent offline:oracle` |
| `moral_hazard` | Hidden-action contract design: choose incentive contracts that actually induce effort instead of assuming first-best effort for free. | `python -m aeread_lab.cli --task moral_hazard --agent offline:oracle` |
| `auction` | Mechanism-design reserve task: Myerson revenue reserve vs welfare/access reserves under configured objectives. | `python -m aeread_lab.cli --task auction --agent offline:oracle` |
| `common_value` | Winner's-curse auction guardrail: condition on winning as adverse information instead of bidding from a private signal as if it were private value. Live smoke: smaller OpenAI models miss; `gpt-5.5` solves. | `python -m aeread_lab.cli --task common_value --agent offline:oracle` |
| `mechanism` | Mechanism-choice task: choose among auction/allocation rules using configured principal weights and strategic-risk penalties. | `python -m aeread_lab.cli --task mechanism --agent offline:oracle` |
| `strategic_drift` | γ-Bench-style repeated strategic discipline: preserve long-horizon relationship value instead of drifting to myopic grabs. | `python -m aeread_lab.cli --task strategic_drift --agent offline:oracle` |
| `exploration` | EconEvals-style unknown-environment learning: decide when information value justifies a pilot before deployment. | `python -m aeread_lab.cli --task exploration --agent offline:oracle` |
| `experiment_design` | Imperfect-signal experiment design: choose whether and how to run a noisy experiment before deployment, then update by Bayes rule. | `python -m aeread_lab.cli --task experiment_design --agent offline:oracle` |
| `retail` | Vending-Bench-style inventory/runway management: maximize cash while respecting hard survival constraints. | `python -m aeread_lab.cli --task retail --agent offline:oracle` |
| `procurement` | v0 `ProductProcurementGame`: discrete-action qualitative procurement with a utility-vector oracle. | `python -m aeread_lab.cli --task procurement --agent offline:oracle` |
| `pricing` | v0 `SimplePricingGame`: continuous price choice with base/posterior/reveal conditions and a closed-form revenue oracle. | `python -m aeread_lab.cli --task pricing --agent offline:oracle` |
| `scam` | Adversarial belief-manipulation arena: scam-supplier style value inflation with credulous and skeptical controls. | `python -m aeread_lab.cli --task scam --agent offline:careful --attacker offline:credulous` |

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
1200-token output budget by default. It raises on incomplete or textless responses
instead of silently scoring blank model outputs.

## Sweep runner and cache

The sweep runner compares agents on the primary mechanical metric for each task:
it also reports `parse`, the fraction of trials with a valid task-specific
`FINAL_*` answer. Treat low parse rate as an eval-format failure before
interpreting the economic metric.

- `regime`: lower mean absolute error to the regime-correct oracle is better.
- `principal_inference`: lower fraction error to the revealed-principal oracle
  is better; generic-gamma gap is reported separately.
- `portfolio`: lower configured-principal utility regret is better; max-return
  and low-risk miss rates are reported separately.
- `ambiguity`: lower robust maxmin regret is better; reference-prior miss rate
  is reported separately.
- `bargaining`: lower configured-principal grade error is better; generic gate
  surplus gap is reported separately.
- `belief_bargaining`: lower posterior expected-surplus gap is better; cue
  switch miss rate is reported separately.
- `market`: lower competitive-equilibrium price gap is better; collusion index
  and collusion rate are reported separately.
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
- `mechanism`: lower configured score regret is better; revenue-default and
  risk-blind miss rates are reported separately.
- `strategic_drift`: lower long-horizon drift rate is better.
- `exploration`: lower expected-value gap is better; exploration miss rate is
  reported separately.
- `experiment_design`: lower expected-value gap is better; experiment miss
  rate is reported separately.
- `retail`: lower ruin probability is better; expected cash gap and order error
  are reported separately.
- `procurement`: higher oracle-choice accuracy is better.
- `pricing`: lower revenue gap to the closed-form optimum is better.
- `scam`: lower mean overpayment is better.

Offline comparison example:

```bash
python -m aeread_lab.cli --sweep --task all \
  --agents offline:oracle,offline:ev --no-cache
```

Live OpenAI responses are cached under `.aeread-cache/responses/` by default.
Use `--cache-dir <path>` to relocate the cache or `--no-cache` to force fresh
calls. Offline agents do not need the cache and never call the API.

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

1. Broaden the `regime` battery to more gamble families and explicit barrier states.
2. Run cached model-version sweeps for alignment-shift diagnostics across
   `gpt-5.5`, `mini`, and `nano`.
3. Broaden `portfolio` from candidate portfolios to real 13F-style
   revealed-preference traces and continuous allocation.
4. Broaden `ambiguity` into maxmin/alpha-maxmin and multiple-prior updates.
5. Broaden the `bargaining` wrapper from take-it-or-leave-it offers to
   alternating-offer and hidden-reservation variants.
6. Broaden `belief_bargaining` into multi-turn opponent modeling.
7. Broaden `mechanism` from scored static choices to equilibrium simulation
   and incentive-compatibility probes.
8. Expand `market` from symmetric price competition to inventory, capital
   appreciation, and multi-period survival.
9. Broaden `retail` into multi-period inventory and supplier-scam variants.
10. Broaden `strategic_drift` into imperfect-information and N-player games.
11. Broaden `experiment_design` into multi-step adaptive tests.
