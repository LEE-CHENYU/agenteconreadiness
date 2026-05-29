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
| `bargaining` | D2/TERMS-style gate+grade wrapper: generic seller surplus extraction vs configured-principal surplus sharing. | `python -m aeread_lab.cli --task bargaining --agent offline:oracle` |
| `market` | Market-Bench-style simultaneous price competition: competitive Nash pricing vs collusive/high-price drift. | `python -m aeread_lab.cli --task market --agent offline:oracle` |
| `auction` | Mechanism-design reserve task: Myerson revenue reserve vs welfare/access reserves under configured objectives. | `python -m aeread_lab.cli --task auction --agent offline:oracle` |
| `procurement` | v0 `ProductProcurementGame`: discrete-action qualitative procurement with a utility-vector oracle. | `python -m aeread_lab.cli --task procurement --agent offline:oracle` |
| `pricing` | v0 `SimplePricingGame`: continuous price choice with base/posterior/reveal conditions and a closed-form revenue oracle. | `python -m aeread_lab.cli --task pricing --agent offline:oracle` |
| `scam` | Adversarial belief-manipulation arena: scam-supplier style value inflation with credulous and skeptical controls. | `python -m aeread_lab.cli --task scam --agent offline:careful --attacker offline:credulous` |

## OpenAI-only API path

The only live API adapter is `aeread_lab.models.OpenAIResponsesAgent`. It accepts
only these aliases:

- `gpt-5.5`
- `mini` (defaults to `gpt-5.5-mini`; override with `AEREAD_OPENAI_MODEL_MINI`)
- `nano` (defaults to `gpt-5.5-nano`; override with `AEREAD_OPENAI_MODEL_NANO`)

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

## Sweep runner and cache

The sweep runner compares agents on the primary mechanical metric for each task:

- `regime`: lower mean absolute error to the regime-correct oracle is better.
- `bargaining`: lower configured-principal grade error is better; generic gate
  surplus gap is reported separately.
- `market`: lower competitive-equilibrium price gap is better; collusion index
  and collusion rate are reported separately.
- `auction`: lower reserve-price error to the objective-specific mechanism
  oracle is better.
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
3. Broaden the `bargaining` wrapper from take-it-or-leave-it offers to
   alternating-offer and hidden-reservation variants.
4. Expand `auction` to multi-objective mechanism selection, not just reserve
   price.
5. Expand `market` from symmetric price competition to inventory, capital
   appreciation, and multi-period survival.
