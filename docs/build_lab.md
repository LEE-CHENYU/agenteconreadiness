# AERead build lab

This copy contains a runnable research scaffold for the current AERead direction.
It is deliberately small and judge-free: task generators expose symbolic ground
truth, scoring is mechanical, and live API use is restricted to OpenAI model
aliases only.

## What is implemented

| Build | Why it matters | Command |
|---|---|---|
| `regime` | Four-regime utility battery: EV single-shot, Kelly compounding, CVaR under ruin, configured-principal CRRA. This is the re-centered regime-appropriateness axis. | `python -m aeread_lab.cli --task regime --agent offline:oracle` |
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

There is no Anthropic/OpenRouter path in this build lab.

## Validation

Run offline validation without API spend:

```bash
python -m unittest discover -s tests
python -m aeread_lab.cli --task all --agent offline:oracle
```

## Expansion order

The next builds should keep the same discipline: add a deterministic generator,
a mechanical oracle, a no-API baseline, then a thin OpenAI run path.

1. Broaden the `regime` battery to more gamble families and explicit barrier states.
2. Add model-version sweeps for alignment-shift diagnostics across `gpt-5.5`,
   `mini`, and `nano`.
3. Add a `TERMS`-style bargaining grade wrapper: gate oracle first, then
   configured-principal bargaining oracle.
4. Add `Market-Bench`/agentic-market simulation wrappers only after the above
   probes are stable with multi-seed confidence intervals.
