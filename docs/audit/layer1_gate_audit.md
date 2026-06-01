# Layer 1 (gate) — rationality-saturation: test methodology & results, for audit

**Date:** 2026-05-31  **Branch:** `build-lab/openai-mvp`

This is a standalone audit of the **Layer 1 / gate** instrument (coherence /
rationality saturation: WARP / GARP / CCEI). It is written to be *checked*: every
number has (a) the file + function that produces it, (b) the test that pins it,
(c) a one-line command to reproduce it. Soft spots and not-yet-done items are
flagged explicitly in §6–§7 — the report's job is to help a skeptic find them.

Layer 2 (identification) has its own report:
[`layer2_identification_audit.md`](layer2_identification_audit.md). The cross-layer
map is in [`../ARCHITECTURE.md`](../ARCHITECTURE.md).

---

## 0. Reproduce everything (offline, no API key)

```bash
cd ~/agenteconreadiness_build_lab_20260529

# Gate instrument tests (golden-answer + harness):
python -m pytest tests/test_axioms.py tests/test_saturation.py -q          # 29 passed

# Gate battery, offline validity controls (oracle saturates, cycler/random fire):
python -m aeread_lab.cli --task saturation --agent offline:oracle
python -m aeread_lab.cli --task saturation --agent offline:cycler
python -m aeread_lab.cli --task saturation --agent offline:random
```

Live gate run (needs `OPENAI_API_KEY`; repo `.env` is gitignored):
```bash
set -a && . ./.env && set +a
python - <<'PY'
from aeread_lab.models import OpenAIResponsesAgent
from aeread_lab.tasks.saturation import run_saturation_battery
print(run_saturation_battery(OpenAIResponsesAgent(model="mini"))["mean_ccei"])
PY
```

**Verified 2026-05-31:** gate tests = **29 passed** (`test_axioms` 17 +
`test_saturation` 12). Full repo suite = **392 passed, 9 subtests**.

---

## 1. What the gate claims to measure

"Does *some* utility rationalize these choices?" — existence, in the
revealed-preference sense. The chain of reasoning:

- **Revealed preference:** if bundle A was chosen when B was affordable, the
  agent revealed A ⪰ B.
- **Afriat's theorem (1967):** a finite set of budget-allocation choices satisfies
  **GARP** *if and only if* a well-behaved (continuous, increasing, concave)
  utility rationalizes them. So GARP-pass is a computable proxy for "a coherent
  utility exists."
- **CCEI** (Critical Cost Efficiency Index / Afriat efficiency index, ∈[0,1]):
  the *degree* of consistency. 1.0 = perfectly rationalizable; `1 − CCEI` ≈ the
  fraction of budget "wasted" relative to a coherent optimizer. This is the metric
  Chen et al. 2023 report (frontier LLMs ≈ 0.998) and the gate's headline number.

The gate is a **floor**: frontier models are expected to saturate it (CCEI≈1.0).
Its value is that AERead can now *measure* this on its own models with real
algorithms + CIs, rather than only cite the literature — not that it discriminates
frontier models (that is the grade's job; see §6 caveat 1).

---

## 2. Method

| Component | Where | What it does |
|---|---|---|
| Axiom core | `aeread_lab/core/axioms.py` | WARP (pairwise reversal); GARP (transitive-closure cycle check — catches cycles of *any* length); CCEI (bisection on the efficiency level at which GARP holds); + transitivity / dominance / monotonicity for discrete-choice menus |
| Gate task | `aeread_lab/tasks/saturation.py` | budget-allocation menus (8 independent sets, 2- and 3-good, 8 menus each); agent allocates a budget across goods; bundles → `Observation`s → axiom scores |
| Statistics | `aeread_lab/stats.py` | bootstrap CI on mean CCEI; Wilson CI on GARP-pass rate; tolerance-sensitivity sweep |
| Offline controls | `aeread_lab/models.py` (`_saturation_allocation`) | `oracle` (Cobb-Douglas maximizer), `random`, `cycler` policies |

**Why budget allocation, not single-shot choice.** GARP/CCEI require *cross-choice*
coherence — the same agent choosing across many budget sets so that
revealed-preference cycles can or cannot form. Single-decision tasks (procurement,
pricing) structurally cannot exhibit a revealed-preference cycle, so they cannot
test the gate. This task is built specifically to be able to. Menus rotate
relative prices (seeded) so budget lines genuinely cross — collinear prices would
make GARP trivially satisfiable and deflate the test.

---

## 3. Golden-answer validation (the correctness proof)

A GARP checker that always returned `True` would pass a smoke test and silently
make every model look rational. These hand-derived cases — validated against an
independent reference implementation **before** the constants were committed —
prove the algorithms are correct. All in `tests/test_axioms.py`:

| Golden dataset | WARP viol. | GARP | CCEI | Why it matters |
|---|---|---|---|---|
| Strict 2-cycle (`p=[(1,2),(2,1)]`, `x=[(1,2),(2,1)]`) | 1 | fail | **0.80** | textbook reversal; WARP and GARP agree |
| Cobb-Douglas maximizer (α=0.5, 4 prices) | 0 | pass | **1.00** | a real utility's choices → must be consistent (the saturation target) |
| **Pure 3-cycle** (`p3`,`x3` rotation) | **0** | **fail** | **0.75** | **WARP sees nothing, GARP catches it** — proves GARP strictly subsumes WARP. The prior sprint toy was WARP-only and would have missed this. |

Supporting assertions (same file): CCEI monotone in violation severity (a mild
reversal scores higher than a severe one); empty input → CCEI 1.0 (trivially
consistent); and the discrete axioms (transitivity / dominance / monotonicity)
each detect a planted violation **and** pass a clean case.

---

## 4. Validity controls — dynamic range (the harness *fires*)

The instrument must distinguish coherent from incoherent, or "saturated" is
meaningless. Offline policies, asserted in `tests/test_saturation.py`, full
8-menu-set battery (numbers re-captured 2026-05-31):

| Policy | mean CCEI (95% CI) | min CCEI | GARP pass | WARP | verdict |
|---|---|---|---|---|---|
| `offline:oracle` (Cobb-Douglas) | 1.0000 (1.000, 1.000) | 1.0000 | 100% | 0 | saturated |
| `offline:random` (menu-keyed split) | ~0.97–1.00* | ~0.97 | 80–90%* | 1–3* | not saturated |
| `offline:cycler` (spend on dearest good) | 0.3676 (0.327, 0.418) | 0.3047 | 0% | 106 | not saturated |

\* `random` keys its split on `hash(...)`, and Python's string hash is
process-salted (`PYTHONHASHSEED`), so its exact CCEI/GARP-rate is
**non-deterministic across runs** (observed 0.97–1.00) — the only non-reproducible
row here. `oracle` and `cycler` ARE deterministic (cycler verified identical
across 3 runs; CCEI 0.3676). The `random` test asserts only the structural
property (`garp_pass_rate < 1` and `saturated == False`), never a point value.

CCEI spans **0.37 → 1.0**; GARP-pass spans 0% → 100%. The tests assert the
*structure* (oracle saturates; cycler/random do not; oracle > cycler), not brittle
point values. **A test that only ever returned
"saturated" is not a test; these controls prove this one isn't.**

---

## 5. Live result — real OpenAI models (2026-05-31)

8 menu sets × 8 menus = **64 live calls per model**, `reasoning_effort=low`,
**0 parse failures**. AERead's own measured gate saturation:

| Agent | mean CCEI (95% CI) | min CCEI | GARP pass | WARP | saturated |
|---|---|---|---|---|---|
| `offline:oracle` (control) | 1.000 (1.00, 1.00) | 1.000 | 100% | 0 | yes |
| **`openai:mini`** (gpt-5.4-mini) | **1.000 (1.00, 1.00)** | 1.000 | 100% (8/8) | 0 | **yes** |
| **`openai:nano`** (gpt-5.4-nano) | **0.9375 (0.856, 1.00)** | 0.7125 | 75% (6/8) | 2 | **no** |
| `offline:cycler` (control) | 0.368 (0.33, 0.42) | — | 0% | 106 | no |

**Reading:** `mini` clears the floor perfectly; `nano` does **not** — 2 of 8 menu
sets are hard GARP failures (min CCEI 0.71 ≈ 29% revealed budget waste on its
worst set). A capability gradient where the sub-frontier model fails coherence and
the frontier-tier model saturates — first-party corroboration of "rationality is a
saturated floor *for frontier models*."

### 5.1 Robustness checks built into every run

- **Tolerance sweep:** CCEI/GARP recomputed across ε ∈ {1e-12 … 1e-2};
  `tolerance_max_ccei_spread` ≤ 1e-4 and `tolerance_verdict_stable = True` on all
  runs above → the verdict is **not** a floating-point-epsilon artifact (a
  reviewer's first objection, pre-answered).
- **GARP-only-violation counter:** flags sets where GARP fired but WARP saw
  nothing (the instrument doing more than a pairwise check). 0 on these particular
  live runs, but the 3-good menus + the golden 3-cycle prove the capability is live.

---

## 6. Honest caveats on interpretation

1. **The gate is a *floor*, instrumented as a floor.** Saturation is *expected*
   for frontier models and is table stakes, not a headline. The value is the
   first-party measurement, not "the gate discriminates frontier models" — it
   mostly won't; that is the grade's role. The mini-vs-nano separation is a
   *capability-tier* gradient (sub-frontier vs frontier), not a frontier-vs-frontier
   one.
2. **GARP tests internal consistency only.** A coherent agent can be coherently
   self-destructive — GARP says nothing about whether the pursued objective is
   *good*. Regime-appropriateness / principal-fidelity is the grade, deliberately
   separate.
3. **CCEI shortfall is design-relative.** "29% budget waste" is relative to *these*
   menus; a different menu distribution would yield different absolute CCEI. The
   cross-model *comparison* is the meaningful object, not the absolute number.

---

## 7. What is NOT yet done (audit the gaps)

| Gap | Status | Consequence |
|---|---|---|
| Gate on gpt-5.5 + a Claude model | **not run** | the frontier-inclusive capability curve is shown only for mini-vs-nano |
| n = 8 menu sets | **modest** | nano's GARP-pass-rate CI is wide (0.41–0.93); the 2 hard failures + min CCEI 0.71 are real, but the *rate* needs 20–30 sets to tighten before any leaderboard claim |
| Higher `reasoning_effort` run | **not run** | unknown whether nano's incoherence survives more thinking (a stress dimension) |
| Stress wrapper (persona / distractor framing) | **not built** | the gate-as-cliff-under-load measurement (where the floor degrades) is described in the task docstring but not implemented |
| Transitivity / dominance / monotonicity in a live task | **core only** | the discrete axioms exist + are unit-tested, but no task feeds an LLM through them yet (saturation uses WARP/GARP/CCEI) |

---

## 8. File + test index (for line-level audit)

| File | Role | Tests |
|---|---|---|
| `aeread_lab/core/axioms.py` | WARP / GARP / CCEI / transitivity / dominance / monotonicity | `tests/test_axioms.py` (17) |
| `aeread_lab/tasks/saturation.py` | gate task + battery + tolerance sweep | `tests/test_saturation.py` (12) |
| `aeread_lab/models.py` `_saturation_allocation` | offline validity-control policies | (via saturation tests) |
| `aeread_lab/stats.py` | bootstrap + Wilson CIs | (via task tests) |

Committed on `build-lab/openai-mvp` (gate core + task: `74d644b`; `core/` reorg +
this report: this session).
