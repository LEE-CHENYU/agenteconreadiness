# build-lab architecture — the 3-layer pipeline, mapped to code

AERead's methodology is a **3-layer revealed-preference pipeline**
(existence → identification → predictive validity), read as a **gate → grade**
hierarchy. This file maps each layer to the code that implements it, so an
auditor can go from "the Layer 1 instrument" straight to the files + tests without
hunting. Conceptual framing lives in the canonical
[`methodology.md`](https://github.com/LEE-CHENYU/agenteconreadiness/blob/main/docs/methodology.md)
(agenteconreadiness repo); this is the implementation index.

## The layer → code map

| Layer | Question | Core (pure math) | Task (runnable) | Tests | Audit report |
|---|---|---|---|---|---|
| **1 — gate** (existence / coherence) | Does *some* utility rationalize the choices? | [`aeread_lab/core/axioms.py`](../aeread_lab/core/axioms.py) — WARP / GARP / CCEI | [`aeread_lab/tasks/saturation.py`](../aeread_lab/tasks/saturation.py) | `tests/test_axioms.py` (17), `tests/test_saturation.py` (12) | [`audit/layer1_gate_audit.md`](audit/layer1_gate_audit.md) |
| **2 — identification** | *Which* utility, within a class? + which class? | [`aeread_lab/core/identify.py`](../aeread_lab/core/identify.py) — fit + model selection + ID audit | [`aeread_lab/tasks/identification.py`](../aeread_lab/tasks/identification.py) | `tests/test_identify.py` (15) | [`audit/layer2_identification_audit.md`](audit/layer2_identification_audit.md) |
| **3 — grade** (predictive validity / fidelity) | Does the identified utility match the *configured/revealed principal* + predict held-out? | (not built — uses revealed-preference fit) | `tasks/regime.py`, `tasks/bargaining.py`, `tasks/principal_holding_*`, … | `tests/test_regime.py`, `tests/test_tasks.py` | — |

Cross-layer headline results (all three layers' live + synthetic numbers, each
traceable to file:function + test + repro command) are pulled into one place in
[`audit/results_summary.md`](audit/results_summary.md). The full per-test list —
every one of the 400 tests in plain English, with the validation logic for what
each layer proves — is in [`audit/test_inventory.md`](audit/test_inventory.md).

Cross-cutting: **stress** (the gate-as-cliff-under-load) is a wrapper dimension,
not a layer — `tasks/stress_degradation_*` / `stability.py`. The **5-axis failure
taxonomy** (information / consistency / calibration / computational / meta-cognitive)
diagnoses *where* in the pipeline a failure sits (see the canonical methodology.md in agenteconreadiness).

## Package layout

```
aeread_lab/
  core/          # pure-math methodology instruments (no LLM, no I/O) — the auditable heart
    axioms.py    #   Layer 1: WARP / GARP / CCEI
    identify.py  #   Layer 2: utility fitting / model selection / identifiability
  tasks/         # 30+ runnable economic-game / probe modules (one per TASK name)
    saturation.py        #   Layer 1 task
    identification.py    #   Layer 2 task
    regime.py, bargaining.py, pricing.py, ...   # grade-side + other probes
  stats.py       # CIs (bootstrap / Wilson) — shared infra (27 importers; stays at top level)
  parsing.py     # FINAL_* answer parsers
  models.py      # Agent protocol; OpenAIResponsesAgent; OfflineAgent (+ per-task handlers)
  runner.py      # task dispatch (run_task / run_tasks / run_sweep)
  cli.py         # `python -m aeread_lab.cli --task <name> --agent <spec>`
  cache.py, reporting.py, stability.py
docs/                        # build_lab carries ONLY what it is canonical for:
  ARCHITECTURE.md            #   this file
  build_lab.md               #   task index + per-task metrics + live results
  build_lab_tracking.md      #   run-by-run ledger
  audit/                     #   per-layer audit reports (layer1 / layer2 / layer3)
  # methodology / proposal / layer3_candidates / prior_art / reading_list /
  # papers/ are NOT here — canonical in agenteconreadiness (link out, don't fork)
```

> **Doc canonicality (2026-05-31).** build_lab is the canonical source for **code +
> build/run docs (this file, `build_lab.md`, `build_lab_tracking.md`) + the audit
> reports (`audit/`)** only. The methodology / proposal / candidate-pool / prior-art
> / bibliography docs are canonical in **agenteconreadiness** and are **not copied
> here** — earlier verbatim forks had silently drifted ~40 lines behind, so they
> were removed; link out instead. **After the audit, build_lab's unique content
> (audit/ + code) syncs *forward* into agenteconreadiness for the
> collaborator-facing view** — one direction, no two-way drift.

## Known structural debt (deliberately deferred)

- **`models.py` is a ~6.5k-line god-file** (OfflineAgent + ~80 task handlers +
  ~60 `_extract_*` helpers). The intended split is `agents/{offline,openai,
  extractors}.py`. Deferred: it touches the dispatch chain and the whole test
  surface — wrong risk to take immediately before a milestone. Tracked here so it
  is not forgotten.
- Layer 3 has no dedicated *core* module yet (the grade is currently expressed
  through individual tasks); a `core/fidelity.py` would be the analog of
  `axioms.py` / `identify.py` once the predict-then-validate instrument is built.
