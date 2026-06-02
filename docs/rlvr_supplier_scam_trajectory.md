# Supplier-Scam Trajectory RLVR Demo

This is a separate post-training demo wrapper around the existing
`supplier_scam` benchmark primitives. It does not change the benchmark task,
the task registry, or `python -m aeread_lab.cli --task supplier_scam`.

The wrapper lives in:

- `aeread_lab/rlvr/supplier_scam_trajectory.py`

It reuses the existing supplier-scam case data and verifier logic:

- supplier choices and unit quantities
- cash transitions
- reserve and timing violations
- oracle final cash
- constrained final-cash regret

## Why This Is RLVR-Friendly

The original benchmark asks an agent for a free-form supplier and unit count.
The RLVR wrapper converts the same scenario into a small discrete trajectory
environment:

1. `reset()` starts one supplier-scam case.
2. Each `step()` chooses a discrete candidate action such as `ACTION_2`.
3. The verifier updates cash and reserve state.
4. The terminal reward is computed from constrained final-cash regret.

The default terminal reward is:

```text
reward = clamp(1 - constrained_final_cash_regret / 100, -1, 1)
```

The oracle trajectory receives `1.0`. Bad trajectories approach `-1.0`.

## Smoke Check Without ML Dependencies

Run the scripted verifier baselines:

```bash
python -m aeread_lab.rlvr.supplier_scam_trajectory --scripted-baselines --episodes 0
```

Expected ordering:

- `oracle`: zero constrained regret
- `reputation_blind`: small positive regret
- `timing_blind`: larger regret
- `credulous`: largest regret

## Tiny-LM RLVR Demo

Install optional dependencies:

```bash
pip install -e '.[rlvr]'
```

Then run a short CPU demo:

```bash
python -m aeread_lab.rlvr.supplier_scam_trajectory \
  --model sshleifer/tiny-gpt2 \
  --episodes 20 \
  --eval-every 5 \
  --device cpu \
  --max-cases 1 \
  --lr 0.001 \
  --kl-coef 0.0 \
  --trainer verifier_guided
```

This is intentionally educational, not a production RLHF/PPO/GRPO trainer. The
default `verifier_guided` trainer evaluates the verifier return for each
candidate action at the current state, then updates the tiny causal LM toward
higher expected verifier reward. The lower-variance verifier-guided path is the
recommended CPU smoke test.

The sparse sampled version is still available:

```bash
python -m aeread_lab.rlvr.supplier_scam_trajectory \
  --model sshleifer/tiny-gpt2 \
  --episodes 30 \
  --eval-every 10 \
  --device cpu \
  --max-cases 1 \
  --trainer reinforce
```

In local CPU testing, sparse REINFORCE did not reliably improve greedy
evaluation in 30 episodes. The verifier-guided run did improve the one-case
greedy trajectory from constrained regret `536.62` to `402.10` in 20 episodes,
but did not reach the full oracle trajectory in that short run. Treat this as a
transparent mechanics demo of verifier-reward post-training, not as evidence
that a tiny GPT-2 policy can solve the supplier-scam environment.

## Why `supplier_scam` (which task is the MDP)

This task was chosen by checking the whole harness against the RL fit criterion —
*an internal oracle that evaluates a multi-step action sequence with a deterministic
terminal reward.* Most of the ~31 tasks call `agent.complete()` once per case and
score a one-shot answer — for RL those are **contextual bandits** (one state → one
action → reward), not trajectories. Only three tasks are genuinely **stepped**
(state threads on the agent's own action across rounds):

| Task | Horizon | State threads on agent action? | Terminal reward | RL fit |
|---|---|---|---|---|
| **`supplier_scam`** | 11 rounds | yes — `cash = chosen_cash` each round | `oracle_final_cash − final_cash` (constrained regret) | **best — a clean MDP** |
| `belief_bargaining` (interaction) | 2 steps | yes — rejection updates state | expected-surplus gap | strong, short horizon |
| `strategic_drift` | 55 rounds | partial (opponent dynamics) | drift vs oracle | strong, long horizon |

`supplier_scam` is the cleanest: deterministic transition (`cash_after_order`),
deterministic terminal reward (`oracle_final_cash`), a real ruin barrier
(`order_reserve_violation` vs `min_cash_reserve`), and a hidden-state inference
problem (scam suppliers inflate claimed resale). It was already an MDP — just not
exposed as `reset()`/`step()`.

## Folded-in env extras (opt-in; defaults unchanged)

Two options were folded into `SupplierScamTrajectoryEnv` (2026-06-01), consolidating
a parallel `envs/` wrapper that had been built separately. Both default OFF so the
existing RLVR-demo behavior is unchanged:

- `transition="stochastic"` — samples each order's scam realization (Bernoulli on
  `scam_probability`) with a seeded RNG; `reset(seed=...)` replays a fixed episode.
  Default `"expected"` reproduces the audited deterministic accounting exactly.
- `reward_mode="shaped"` — dense per-round `−regret/reward_scale` each `step()`
  (denser for policy gradients). Default `"terminal"` matches the verifier reward.

Equivalence is preserved: an oracle policy under `reward_mode="shaped"` /
`transition="expected"` reaches `oracle_final_cash` with ~0 episode return on every
case (tested) — i.e. the env stays the *same* environment the `supplier_scam` audit
validated. Tests: `tests/tasks/test_supplier_scam_trajectory.py` (8).

## Scope caveat

This is a **training** surface, not part of the audit/eval. It is the first place
the benchmark becomes a *training* environment rather than an evaluator — which
(per the methodology's Q14 / RLHF-coverage thread) is a deliberate positioning
step: an env you train against stops being a clean held-out eval. The audited
`tasks/` corpus remains the eval; `rlvr/` is a separate, explicitly-labeled
training surface (not in `TASK_ORDER`), so training on it never contaminates the
benchmark.

## Separation From `supplier_scam`

The existing benchmark implementation remains in
`aeread_lab/tasks/supplier_scam.py`.

The RLVR wrapper is not included in `TASK_ORDER` and is not exposed as a normal
AERead benchmark task. That keeps the benchmark surface stable while still
letting us use the same environment mechanics for post-training experiments.
