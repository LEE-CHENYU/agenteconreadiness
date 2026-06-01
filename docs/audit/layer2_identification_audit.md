# Layer 2 (identification) — utility recovery: test methodology & results, for audit

**Date:** 2026-05-31  **Branch:** `build-lab/openai-mvp`

Standalone audit of the **Layer 2 / identification** instrument: given that *a*
utility exists (Layer 1 gate passed), recover *which one* — fit the risk parameter,
select the functional class, and **say honestly when the data can't tell**. Same
audit discipline as the gate report: every number → file + test + repro command.

Layer 1 (gate) has its own report: [`layer1_gate_audit.md`](layer1_gate_audit.md).
Cross-layer map: [`../ARCHITECTURE.md`](../ARCHITECTURE.md).

> **Status:** estimator validated on **synthetic data with known planted utilities**
> (§4 — proves correctness); a **multi-seed live-model run** (§5.2, 2026-05-31)
> recovers the *implied* risk parameter from gpt-5.4 nano + mini's own allocation
> choices with a bootstrap CI over 5 seeds each. Both reveal near-log-utility
> (γ≈1); the coherence gap (nano CI ~4× wider than mini) is CI-confirmed. Still
> 2 models, single elicitation framing — a real measurement, not yet a
> leaderboard claim.

---

## 0. Reproduce (offline, no API key)

```bash
cd ~/agenteconreadiness_build_lab_20260529
python -m pytest tests/test_identify.py -q          # 15 passed
python -m aeread_lab.cli --task identification       # synthetic recovery battery
```

**Verified 2026-05-31:** `test_identify` = **15 passed**.

---

## 1. What it claims to measure

Layer 1 answers "does *a* utility exist?" (GARP — existence). Layer 2 answers the
next question: **"which one?"** — recover the risk parameter within a functional
class (CRRA γ; CARA a) and select the class across candidates. The headline
honesty is an **identifiability audit**: a flag for when the data *cannot* pin down
the parameter or the class. This is the direct response to **Andrews 2026**'s
critique — a representation theorem gives *existence*, not *identification*. A
Layer 2 that always confidently named a utility would overclaim exactly what
Andrews warns against; reporting non-identification *is* the contribution.

---

## 2. Method

| Component | Where | What it does |
|---|---|---|
| Fitting core | `aeread_lab/core/identify.py` | least-squares of observed staked fraction vs each class's optimal-fraction map f*(θ); 1-D grid + local refine (stdlib, no scipy) |
| Classes | same | CRRA u=W^(1−γ)/(1−γ); CARA u=−e^(−aW). Separated by wealth: CRRA's optimal *fraction* is wealth-invariant, CARA's declines with wealth |
| Model selection | same | fit every class, BIC-approx posterior over classes; `decisive` iff winner posterior > 0.9 |
| Identifiability audit | `_profile_interval` | flags weak ID on: flat SSE profile (band > 60% of grid), boundary estimate, n < 4 obs, or non-decisive class posterior |
| Battery | `aeread_lab/tasks/identification.py` | synthetic recovery over planted scenarios × seeds; bootstrap CI on recovery error |

**Why continuous allocation (not binary menus).** Binary safe-vs-risky menus were
tested first and *under-identify* γ (a flip only brackets γ to an interval;
estimates pile at the grid boundary). The continuous staked-fraction design —
where f*(γ) is smooth and monotone — recovers γ tightly. That earlier failure is
not hidden; it is exactly what the identifiability audit reports for thin designs
(§5).

---

## 3. Class-separability sanity (what model selection relies on)

Verified in `tests/test_identify.py`:

| | wealth 20 | 200 | 2000 |
|---|---|---|---|
| CRRA γ=3 optimal fraction | 0.20 | 0.20 | 0.20 (flat) |
| CARA a=0.01 optimal fraction | 0.998 | 0.288 | 0.028 (declines) |

Fraction-vs-wealth slope identifies the *family* — which is why selection needs a
wide wealth range, and why a single-wealth design is non-identified (§5).

---

## 4. Parameter recovery — the correctness proof (#1)

Synthetic choices from a known utility + Gaussian fraction noise, fit back. Battery
(`--task identification`, 5 scenarios × 8 seeds, σ=0.03):

| Planted | mean abs error (95% CI) | class recovery | decisive |
|---|---|---|---|
| CRRA γ=0.7 | 0.008 (0.004, 0.014) | 100% | 100% |
| CRRA γ=1.5 | 0.018 (0.011, 0.024) | 100% | 100% |
| CRRA γ=3.0 | 0.068 (0.048, 0.086) | 100% | 100% |
| CRRA γ=5.0 | 0.141 (0.093, 0.181) | 100% | 100% |
| CARA a=0.01 | 0.000 (0.000, 0.000) | 100% | 100% |
| **aggregate** | **0.047 (0.028, 0.066)** | **100%** | **100%** |

`instrument_validated = True` (mean abs err < 0.5 AND class recovery ≥ 0.9).
**Honest note:** recovery error grows with γ (0.008 → 0.141) — high risk-aversion
flattens the optimal fraction, carrying less information; the CIs report this
rather than hiding it. Tests assert `delta ≤ 0.4–0.5` (margin over observed) and
multi-seed spread < 0.8.

---

## 5. Identifiability audit — the honesty proof (#3)

The audit must flag non-identification, not silently emit a confident wrong number.
Pinned cases (`tests/test_identify.py`):

| Case | Expected | Asserted |
|---|---|---|
| Rich wealth range (5 levels) | decisive | `sel.decisive == True` |
| **Single wealth level** | **not decisive** (CRRA/CARA mimic each other) | `sel.decisive == False` |
| 1 observation | weakly identified | `fit.weakly_identified == True` |
| Always-max-bet (boundary) | weakly identified | `fit.weakly_identified == True` |

The single-wealth case is load-bearing: it shows the instrument refuses to name a
functional class when the design can't distinguish them.

## 5.1 Model selection — class recovery (#2)

Generate from CRRA → selector picks CRRA (posterior CRRA > CARA); generate from
CARA → picks CARA. Posterior is a proper distribution (sums to 1). Asserted both
directions in `tests/test_identify.py`.

## 5.2 Live result — implied risk parameter of real models (2026-05-31)

The instrument elicits a staked-fraction allocation from the model across each
(gamble × wealth) cell, then fits the *implied* utility from the model's own
choices. This recovers "what risk parameter is the model behaving as?" — distinct
from the source repo's persona-fit (which asks "can the model imitate a *given*
fitted human?").

**Multi-seed** (`run_live_identification_multiseed`, 5 independent elicitation
passes per model — bare agent, no cache → genuine resampling of the reasoning
models; 20 cells × 5 seeds = 100 live calls/model, 0 parse failures). The CI is a
**bootstrap over the 5 per-seed γ̂**, so it captures the real run-to-run sampling
variance (not just within-run fit residual):

| Model | mean implied CRRA γ̂ | bootstrap CI95 (over seeds) | per-seed γ̂ | spread | mean RMSE | selection |
|---|---|---|---|---|---|---|
| `openai:nano` (gpt-5.4-nano) | **0.997** | **[0.958, 1.049]** | 1.01, 0.97, 0.97, 0.94, 1.10 | 0.16 | 0.158 | CRRA decisive (1.00), 5/5 |
| `openai:mini` (gpt-5.4-mini) | **1.007** | **[1.000, 1.022]** | 1.00, 1.00, 1.04, 1.00, 1.00 | 0.037 | 0.018 | CRRA decisive (1.00), 5/5 |

**Reading:** both models reveal **near-log-utility risk preferences (γ ≈ 1)** —
roughly Kelly-like, materially risk-averse relative to the risk-neutral (γ=0)
default, not extreme. CRRA decisively beats CARA on every seed for both. The
**coherence gap is now CI-confirmed, not anecdotal**: `mini`'s γ̂ is tight
(CI width 0.022, per-seed spread 0.037, RMSE 0.018) while `nano`'s is ~4× wider
(CI width 0.091, spread 0.16, RMSE 0.158) — i.e. nano's allocations across wealth
levels are less consistently explained by a single γ, the same direction as the
gate finding (nano fails GARP on 2/8 sets; mini saturates). This **supersedes the
earlier single-pass two-run range** (nano 0.96↔1.03) — that spread is now properly
expressed as a bootstrap CI rather than a caveat.

**Still not done (honest):** γ̂ is specific to this "stake a fraction" elicitation
framing (framing-invariance untested — §6); 2 models only; and this is the model's
*own* implied γ, not the grade-side persona-config match (§6).

**Other caveats:** (1) n=20 cells, 2 models — a first measurement. (2) γ̂ is
specific to this "stake a fraction" elicitation framing; framing-invariance is
untested (§6). (3) This is the model's *own* implied γ; the grade-side question
(does a persona-*configured* model's fitted γ match its configured target?) is
still unrun (§6).

---

## 6. What is NOT yet done (audit the gaps)

| Gap | Status | Consequence |
|---|---|---|
| **Live implied-γ recovery** | **done + multi-seed (§5.2)** — nano + mini, 5 seeds, bootstrap CI | both γ≈1, coherence gap CI-confirmed (nano CI ~4× wider). Remaining: more models (gpt-5.5, Claude) |
| **Grade-side: persona-configured γ match** | **not run** | the higher-value question — configure a model to a target risk attitude, fit its γ̂, check it matches — is still unrun (needs the source-repo C1 framework) |
| Framing-invariance of γ̂ | **not tested** | γ̂ is measured under one elicitation prompt; whether it is stable across framings is unknown (a stress dimension) |
| Functional classes | **CRRA + CARA only** | prospect-theory (λ, α) and hyperbolic discounting (δ, k) are in the methodology's class list but not built; the interface supports adding them via a small product grid |
| n = 8 seeds / scenario | **modest** | adequate for a methodology-validation claim; not a ranked-leaderboard claim |
| Bayesian posterior over θ (within class) | **point + profile interval only** | the methodology mentions a full posterior; current output is θ̂ + a profile-likelihood-style interval, not MCMC |

---

## 7. Honest caveats

1. **Synthetic-data correctness, not a model claim.** The battery proves the
   estimator recovers a planted utility; it says nothing yet about any real
   model's risk preferences.
2. **Least-squares-on-fraction, not full MLE.** The fit minimizes squared error of
   observed vs optimal fraction (a method-of-moments-flavored estimator), not a
   likelihood over a stochastic choice model. Adequate and well-conditioned for
   the continuous-allocation design; a full MLE/Bayesian version is a natural
   upgrade and would give principled CIs.
3. **BIC-approx posterior.** Model-selection "posterior" is softmax over −0.5·BIC,
   not a true marginal-likelihood posterior — a standard, defensible approximation,
   but named as such.

---

## 8. File + test index

| File | Role | Tests |
|---|---|---|
| `aeread_lab/core/identify.py` | utility fitting + model selection + ID audit | `tests/test_identify.py` (15) |
| `aeread_lab/tasks/identification.py` | synthetic recovery battery | (via identify tests + CLI) |

Committed on `build-lab/openai-mvp` (instrument: `9a18fda`; `core/` reorg + this
report: this session).
