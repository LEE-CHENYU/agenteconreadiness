from __future__ import annotations

import argparse
import json
import random
import re
from dataclasses import asdict, dataclass
from typing import Iterable, Sequence

from aeread_lab.stats import mean
from aeread_lab.tasks.supplier_scam import (
    DEFAULT_CASES,
    SupplierOption,
    SupplierRound,
    SupplierScamCase,
    cash_after_order,
    choose_order,
    effective_scam_probability,
    expected_unit_profit,
    max_affordable_units,
    oracle_final_cash,
    order_reserve_violation,
)


ACTION_RE = re.compile(r"ACTION_(\d+)")


@dataclass(frozen=True)
class TrajectoryAction:
    supplier_id: str
    units: int

    @property
    def is_no_order(self) -> bool:
        return self.supplier_id in {"", "none"} or self.units <= 0


@dataclass(frozen=True)
class TrajectoryStep:
    case_key: str
    round_index: int
    round_key: str
    cash_before: float
    action: TrajectoryAction
    oracle_action: TrajectoryAction
    cash_after: float
    oracle_cash_after: float
    step_cash_regret: float
    reserve_violation: bool
    timing_reserve_violation: bool


def _supplier_by_id(round_spec: SupplierRound, supplier_id: str) -> SupplierOption | None:
    if supplier_id in {"", "none"}:
        return None
    return next((option for option in round_spec.suppliers if option.supplier_id == supplier_id), None)


def _normalize_cases(cases: Sequence[SupplierScamCase] | None) -> tuple[SupplierScamCase, ...]:
    return tuple(cases or DEFAULT_CASES)


def terminal_reward_from_regret(constrained_regret: float, *, reward_scale: float) -> float:
    """Map verifier regret to a compact RL reward: oracle is 1, poor trajectories approach -1."""
    if reward_scale <= 0:
        raise ValueError("reward_scale must be positive")
    return max(-1.0, min(1.0, 1.0 - constrained_regret / reward_scale))


class SupplierScamTrajectoryEnv:
    """Discrete trajectory wrapper for supplier-scam RLVR demos.

    The benchmark task in :mod:`aeread_lab.tasks.supplier_scam` remains the
    source of truth. This wrapper only exposes its case data and verifier as a
    reset/step environment suitable for tiny policy-gradient examples.
    """

    def __init__(
        self,
        cases: Sequence[SupplierScamCase] | None = None,
        *,
        reward_scale: float = 100.0,
        transition: str = "expected",
        reward_mode: str = "terminal",
    ) -> None:
        if transition not in {"expected", "stochastic"}:
            raise ValueError("transition must be 'expected' or 'stochastic'")
        if reward_mode not in {"terminal", "shaped"}:
            raise ValueError("reward_mode must be 'terminal' or 'shaped'")
        self.cases = _normalize_cases(cases)
        self.reward_scale = reward_scale
        # `transition`: 'expected' = the audited deterministic accounting (default,
        #   reproduces the benchmark verifier exactly); 'stochastic' = sample each
        #   order's scam realization (Bernoulli on scam_probability) via a seeded
        #   RNG, so reset(seed=...) replays a fixed episode.
        # `reward_mode`: 'terminal' = reward only on the final step (default,
        #   matches the verifier); 'shaped' = dense per-round -regret each step
        #   (both sum to the same episode return; shaped is denser for RL).
        self.transition = transition
        self.reward_mode = reward_mode
        self._rng = random.Random()
        self.case: SupplierScamCase | None = None
        self.case_index = 0
        self.round_index = 0
        self.cash = 0.0
        self.reserve_violated = False
        self.steps: list[TrajectoryStep] = []

    def reset(self, *, case_index: int = 0, case_key: str | None = None, seed: int | None = None) -> str:
        if case_key is not None:
            matching = [index for index, case in enumerate(self.cases) if case.key == case_key]
            if not matching:
                raise KeyError(f"unknown supplier-scam trajectory case: {case_key}")
            case_index = matching[0]
        if not 0 <= case_index < len(self.cases):
            raise IndexError(f"case_index must be in [0, {len(self.cases) - 1}], got {case_index}")
        if seed is not None:
            self._rng = random.Random(seed)
        self.case_index = case_index
        self.case = self.cases[case_index]
        self.round_index = 0
        self.cash = self.case.initial_cash
        self.reserve_violated = False
        self.steps = []
        return self.render_observation()

    @property
    def done(self) -> bool:
        return self.case is not None and self.round_index >= len(self.case.rounds)

    @property
    def current_round(self) -> SupplierRound:
        if self.case is None:
            raise RuntimeError("call reset() before reading the current round")
        if self.done:
            raise RuntimeError("episode is done")
        return self.case.rounds[self.round_index]

    def oracle_action(self) -> TrajectoryAction:
        if self.case is None:
            raise RuntimeError("call reset() before asking for the oracle action")
        supplier_id, units, _ = choose_order(self.cash, self.case.min_cash_reserve, self.current_round)
        return TrajectoryAction(supplier_id, units)

    def scripted_action(self, policy: str) -> TrajectoryAction:
        if self.case is None:
            raise RuntimeError("call reset() before asking for a scripted action")
        flags = {
            "oracle": {},
            "credulous": {"credulous": True},
            "timing_blind": {"timing_blind": True},
            "reputation_blind": {"reputation_blind": True},
        }
        if policy not in flags:
            raise ValueError(f"unknown scripted policy {policy!r}")
        supplier_id, units, _ = choose_order(
            self.cash,
            self.case.min_cash_reserve,
            self.current_round,
            **flags[policy],
        )
        return TrajectoryAction(supplier_id, units)

    def action_candidates(self) -> list[TrajectoryAction]:
        if self.case is None:
            raise RuntimeError("call reset() before listing actions")
        round_spec = self.current_round
        actions = [TrajectoryAction("none", 0)]
        oracle = self.oracle_action()
        for option in round_spec.suppliers:
            upper_timing_blind = max_affordable_units(
                self.cash,
                self.case.min_cash_reserve,
                round_spec,
                option,
                timing_blind=True,
            )
            upper_safe = max_affordable_units(
                self.cash,
                self.case.min_cash_reserve,
                round_spec,
                option,
            )
            unit_buckets = {upper_timing_blind, upper_safe}
            if upper_timing_blind > 0:
                unit_buckets.add(max(1, upper_timing_blind // 2))
            if upper_safe > 0:
                unit_buckets.add(max(1, upper_safe // 2))
            if oracle.supplier_id == option.supplier_id:
                unit_buckets.add(oracle.units)
            for units in sorted(units for units in unit_buckets if units > 0):
                actions.append(TrajectoryAction(option.supplier_id, units))
        return _dedupe_actions(actions)

    def render_observation(self) -> str:
        if self.case is None:
            raise RuntimeError("call reset() before rendering an observation")
        if self.done:
            return "EPISODE_DONE"
        round_spec = self.current_round
        lines = [
            "TASK: supplier_scam_trajectory_rlvr",
            "Return one candidate label only, like ACTION_0.",
            f"case={self.case.key}",
            f"real_case={self.case.real_case}",
            f"round={self.round_index + 1}/{len(self.case.rounds)}",
            f"round_key={round_spec.key}",
            f"market_note={round_spec.market_note}",
            f"current_cash={self.cash:.2f}",
            f"min_cash_reserve={self.case.min_cash_reserve:.2f}",
            f"interim_cash_need={round_spec.interim_cash_need:.2f}",
            "history:",
        ]
        if not self.steps:
            lines.append("  none")
        for step in self.steps:
            lines.append(
                "  round={round_index} action_supplier={supplier} action_units={units} "
                "cash_after={cash_after:.2f} reserve_violation={violation}".format(
                    round_index=step.round_index,
                    supplier=step.action.supplier_id,
                    units=step.action.units,
                    cash_after=step.cash_after,
                    violation=str(step.reserve_violation).lower(),
                )
            )
        lines.append("suppliers:")
        for option in round_spec.suppliers:
            lines.append(
                "  supplier_id={supplier_id} unit_cost={unit_cost:.2f} claimed_resale={claimed_resale:.2f} "
                "verified_resale_if_legit={verified_resale_if_legit:.2f} effective_scam_probability={risk:.4f} "
                "salvage_resale_if_scam={salvage:.2f} max_units={max_units} delivery_lag_rounds={lag} "
                "sell_through_rate={sell_through:.4f} storage_cost_per_unsold={storage:.2f} "
                "successful_deliveries={successes} failed_deliveries={failures} expected_unit_profit={profit:.4f}".format(
                    supplier_id=option.supplier_id,
                    unit_cost=option.unit_cost,
                    claimed_resale=option.claimed_resale,
                    verified_resale_if_legit=option.verified_resale_if_legit,
                    risk=effective_scam_probability(option),
                    salvage=option.salvage_resale_if_scam,
                    max_units=option.max_units,
                    lag=option.delivery_lag_rounds,
                    sell_through=option.sell_through_rate,
                    storage=option.storage_cost_per_unsold,
                    successes=option.successful_deliveries,
                    failures=option.failed_deliveries,
                    profit=expected_unit_profit(option),
                )
            )
        lines.append("candidate_actions:")
        for index, action in enumerate(self.action_candidates()):
            lines.append(f"  ACTION_{index}: supplier_id={action.supplier_id} units={action.units}")
        return "\n".join(lines)

    def step(self, action: int | str | TrajectoryAction) -> tuple[str, float, bool, dict]:
        if self.case is None:
            raise RuntimeError("call reset() before stepping")
        if self.done:
            raise RuntimeError("episode is already done")
        resolved = self._resolve_action(action)
        round_spec = self.current_round
        option = None if resolved.is_no_order else _supplier_by_id(round_spec, resolved.supplier_id)
        if option is None and not resolved.is_no_order:
            raise ValueError(f"unknown supplier_id for current round: {resolved.supplier_id}")
        cash_before = self.cash
        oracle = self.oracle_action()
        oracle_option = None if oracle.is_no_order else _supplier_by_id(round_spec, oracle.supplier_id)
        oracle_cash = cash_after_order(cash_before, round_spec, oracle_option, oracle.units)
        if self.transition == "stochastic" and option is not None and resolved.units > 0:
            chosen_cash, scam_realized = self._stochastic_cash_after(cash_before, round_spec, option, resolved.units)
        else:
            chosen_cash = cash_after_order(cash_before, round_spec, option, resolved.units)
            scam_realized = None
        violation = order_reserve_violation(
            cash_before,
            self.case.min_cash_reserve,
            round_spec,
            option,
            resolved.units,
            chosen_cash,
        )
        timing_violation = violation and option is not None and option.delivery_lag_rounds > 0 and resolved.units > 0
        self.reserve_violated = self.reserve_violated or violation
        self.cash = chosen_cash
        self.steps.append(
            TrajectoryStep(
                case_key=self.case.key,
                round_index=self.round_index + 1,
                round_key=round_spec.key,
                cash_before=cash_before,
                action=resolved,
                oracle_action=oracle,
                cash_after=chosen_cash,
                oracle_cash_after=oracle_cash,
                step_cash_regret=oracle_cash - chosen_cash,
                reserve_violation=violation,
                timing_reserve_violation=timing_violation,
            )
        )
        self.round_index += 1
        done = self.done
        info = {
            "step": _step_json(self.steps[-1]),
            "candidate_count": len(self.action_candidates()) if not done else 0,
        }
        if scam_realized is not None:
            info["scam_realized"] = scam_realized
        observation = "EPISODE_DONE"
        # reward: 'terminal' = mapped regret on the final step only (the verifier
        # reward); 'shaped' = dense per-round -regret/reward_scale each step (sums
        # to roughly the same signal, denser for policy gradients).
        if self.reward_mode == "shaped":
            reward = -(oracle_cash - chosen_cash) / self.reward_scale
        else:
            reward = 0.0
        if done:
            terminal = self.terminal_summary()
            if self.reward_mode == "terminal":
                reward = terminal["terminal_reward"]
            info["terminal"] = terminal
        else:
            observation = self.render_observation()
        return observation, reward, done, info

    def _stochastic_cash_after(
        self, cash: float, round_spec: SupplierRound, option: SupplierOption, units: int
    ) -> tuple[float, bool]:
        """Sample the realized scam outcome for this order (Bernoulli on
        scam_probability) and compute realized cash — mirrors expected_unit_profit's
        decomposition but with a draw instead of the expectation. Returns
        (realized_cash_after, scam_realized). Seeded via reset(seed=...)."""
        scam = self._rng.random() < option.scam_probability
        realized_resale = option.salvage_resale_if_scam if scam else option.verified_resale_if_legit
        sold_value = option.sell_through_rate * realized_resale
        leftover_value = (1.0 - option.sell_through_rate) * option.salvage_resale_if_scam
        storage_cost = (1.0 - option.sell_through_rate) * option.storage_cost_per_unsold
        realized_unit_profit = sold_value + leftover_value - storage_cost - option.unit_cost
        return cash - round_spec.interim_cash_need + units * realized_unit_profit, scam

    def terminal_summary(self) -> dict:
        if self.case is None:
            raise RuntimeError("call reset() before reading terminal summary")
        oracle_cash = oracle_final_cash(self.case)
        raw_regret = oracle_cash - self.cash
        reserve_penalty = 2.0 * self.case.min_cash_reserve if self.reserve_violated else 0.0
        constrained_regret = raw_regret + reserve_penalty
        return {
            "case": self.case.key,
            "oracle_final_cash": oracle_cash,
            "chosen_final_cash": self.cash,
            "final_cash_regret": raw_regret,
            "constrained_final_cash_regret": constrained_regret,
            "reserve_violated": self.reserve_violated,
            "terminal_reward": terminal_reward_from_regret(
                constrained_regret,
                reward_scale=self.reward_scale,
            ),
            "steps": [_step_json(step) for step in self.steps],
        }

    def _resolve_action(self, action: int | str | TrajectoryAction) -> TrajectoryAction:
        if isinstance(action, TrajectoryAction):
            return action
        candidates = self.action_candidates()
        if isinstance(action, int):
            if not 0 <= action < len(candidates):
                raise IndexError(f"action index must be in [0, {len(candidates) - 1}], got {action}")
            return candidates[action]
        parsed_index = parse_action_label(action, len(candidates))
        return candidates[parsed_index]


def parse_action_label(text: str, action_count: int) -> int:
    match = ACTION_RE.search(text)
    if match is None:
        raise ValueError(f"no ACTION_n label found in {text!r}")
    index = int(match.group(1))
    if not 0 <= index < action_count:
        raise IndexError(f"ACTION_{index} is outside action_count={action_count}")
    return index


def run_scripted_policy(
    policy: str,
    cases: Sequence[SupplierScamCase] | None = None,
    *,
    reward_scale: float = 100.0,
) -> dict:
    cases = _normalize_cases(cases)
    case_summaries = []
    for case_index in range(len(cases)):
        env = SupplierScamTrajectoryEnv(cases, reward_scale=reward_scale)
        env.reset(case_index=case_index)
        done = False
        reward = 0.0
        while not done:
            _, reward, done, _ = env.step(env.scripted_action(policy))
        terminal = env.terminal_summary()
        terminal["terminal_reward"] = reward
        case_summaries.append(terminal)
    return {
        "policy": policy,
        "n_cases": len(case_summaries),
        "mean_final_cash_regret": mean([row["final_cash_regret"] for row in case_summaries]),
        "mean_constrained_final_cash_regret": mean(
            [row["constrained_final_cash_regret"] for row in case_summaries]
        ),
        "mean_terminal_reward": mean([row["terminal_reward"] for row in case_summaries]),
        "reserve_violation_rate": mean([1.0 if row["reserve_violated"] else 0.0 for row in case_summaries]),
        "cases": case_summaries,
    }


def run_scripted_baselines(
    policies: Iterable[str] = ("oracle", "reputation_blind", "timing_blind", "credulous"),
    cases: Sequence[SupplierScamCase] | None = None,
    *,
    reward_scale: float = 100.0,
) -> dict:
    return {
        policy: run_scripted_policy(policy, cases=cases, reward_scale=reward_scale)
        for policy in policies
    }


def format_scripted_baselines(payload: dict) -> str:
    lines = [
        "policy              constrained_regret  terminal_reward  reserve_violation_rate",
        "------------------  ------------------  ---------------  ----------------------",
    ]
    for policy, row in payload.items():
        lines.append(
            f"{policy:<18}  {row['mean_constrained_final_cash_regret']:>18.4f}  "
            f"{row['mean_terminal_reward']:>15.4f}  {row['reserve_violation_rate']:>22.4f}"
        )
    return "\n".join(lines)


def evaluate_lm_policy(model, tokenizer, cases: Sequence[SupplierScamCase], *, device: str) -> dict:
    import torch

    summaries = []
    for case_index in range(len(cases)):
        env = SupplierScamTrajectoryEnv(cases)
        env.reset(case_index=case_index)
        done = False
        with torch.no_grad():
            while not done:
                prompt = env.render_observation() + "\nAnswer:"
                labels = [f"ACTION_{index}" for index in range(len(env.action_candidates()))]
                logps = _continuation_logprobs(model, tokenizer, prompt, labels, device=device)
                action_index = int(torch.stack(logps).argmax().item())
                _, _, done, _ = env.step(action_index)
        summaries.append(env.terminal_summary())
    return {
        "n_cases": len(summaries),
        "mean_constrained_final_cash_regret": mean(
            [row["constrained_final_cash_regret"] for row in summaries]
        ),
        "mean_terminal_reward": mean([row["terminal_reward"] for row in summaries]),
        "cases": summaries,
    }


def train_tiny_lm_policy(
    *,
    model_name: str = "sshleifer/tiny-gpt2",
    episodes: int = 30,
    lr: float = 5e-5,
    kl_coef: float = 0.02,
    temperature: float = 1.0,
    seed: int = 0,
    device: str = "cpu",
    max_cases: int | None = None,
    eval_every: int = 10,
    trainer: str = "verifier_guided",
) -> dict:
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise RuntimeError(
            "The RLVR tiny-LM demo requires optional dependencies: "
            "pip install -e '.[rlvr]'"
        ) from exc

    if episodes < 1:
        raise ValueError("episodes must be positive")
    if trainer not in {"verifier_guided", "reinforce"}:
        raise ValueError("trainer must be 'verifier_guided' or 'reinforce'")
    random.seed(seed)
    torch.manual_seed(seed)
    cases = tuple(DEFAULT_CASES[:max_cases] if max_cases is not None else DEFAULT_CASES)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    policy = AutoModelForCausalLM.from_pretrained(model_name).to(device)
    reference = AutoModelForCausalLM.from_pretrained(model_name).to(device)
    reference.eval()
    for parameter in reference.parameters():
        parameter.requires_grad_(False)
    optimizer = torch.optim.AdamW(policy.parameters(), lr=lr)
    rng = random.Random(seed)
    baseline = 0.0
    history = []
    before = evaluate_lm_policy(policy, tokenizer, cases, device=device)
    for episode in range(1, episodes + 1):
        policy.train()
        if trainer == "reinforce":
            env = SupplierScamTrajectoryEnv(cases)
            env.reset(case_index=rng.randrange(len(cases)))
            selected_logps = []
            reference_logps = []
            done = False
            reward = 0.0
            while not done:
                prompt = env.render_observation() + "\nAnswer:"
                labels = [f"ACTION_{index}" for index in range(len(env.action_candidates()))]
                logps = torch.stack(_continuation_logprobs(policy, tokenizer, prompt, labels, device=device))
                probs = torch.softmax(logps / temperature, dim=0)
                action_index = torch.distributions.Categorical(probs=probs).sample()
                label = labels[int(action_index.item())]
                with torch.no_grad():
                    reference_logp = _continuation_logprob(reference, tokenizer, prompt, label, device=device)
                _, reward, done, _ = env.step(int(action_index.item()))
                selected_logps.append(logps[action_index])
                reference_logps.append(reference_logp)
            baseline = 0.9 * baseline + 0.1 * reward
            advantage = reward - baseline
            policy_loss = -advantage * torch.stack(selected_logps).sum()
            selected_kl = torch.stack(
                [
                    (policy_logp - ref_logp).pow(2)
                    for policy_logp, ref_logp in zip(selected_logps, reference_logps)
                ]
            ).sum()
            loss = policy_loss + kl_coef * selected_kl
            row = {
                "episode": episode,
                "trainer": trainer,
                "reward": reward,
                "advantage": advantage,
                "loss": float(loss.detach().cpu()),
                "case": env.case.key if env.case is not None else "",
                "constrained_final_cash_regret": env.terminal_summary()["constrained_final_cash_regret"],
            }
        else:
            env = SupplierScamTrajectoryEnv(cases)
            env.reset(case_index=rng.randrange(len(cases)))
            losses = []
            expected_rewards = []
            greedy_rewards = []
            done = False
            while not done:
                prompt = env.render_observation() + "\nAnswer:"
                candidates = env.action_candidates()
                labels = [f"ACTION_{index}" for index in range(len(candidates))]
                q_values = torch.tensor(
                    candidate_terminal_rewards(env),
                    dtype=torch.float32,
                    device=device,
                )
                logps = torch.stack(_continuation_logprobs(policy, tokenizer, prompt, labels, device=device))
                probs = torch.softmax(logps / temperature, dim=0)
                expected_reward = (probs * q_values).sum()
                with torch.no_grad():
                    ref_logps = torch.stack(
                        _continuation_logprobs(reference, tokenizer, prompt, labels, device=device)
                    )
                kl_penalty = (probs * (logps - ref_logps).pow(2)).sum()
                losses.append(-expected_reward + kl_coef * kl_penalty)
                expected_rewards.append(float(expected_reward.detach().cpu()))
                greedy_rewards.append(float(q_values[int(probs.argmax().item())].detach().cpu()))
                _, _, done, _ = env.step(env.oracle_action())
            loss = torch.stack(losses).sum()
            row = {
                "episode": episode,
                "trainer": trainer,
                "mean_expected_state_reward": mean(expected_rewards),
                "mean_greedy_state_reward": mean(greedy_rewards),
                "loss": float(loss.detach().cpu()),
                "case": env.case.key if env.case is not None else "",
                "constrained_final_cash_regret": env.terminal_summary()["constrained_final_cash_regret"],
            }
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if eval_every > 0 and episode % eval_every == 0:
            policy.eval()
            row["eval"] = evaluate_lm_policy(policy, tokenizer, cases, device=device)
        history.append(row)
        print(json.dumps(row, sort_keys=True))
    policy.eval()
    after = evaluate_lm_policy(policy, tokenizer, cases, device=device)
    return {
        "model": model_name,
        "trainer": trainer,
        "episodes": episodes,
        "before": before,
        "after": after,
        "history": history,
    }


def _continuation_logprob(model, tokenizer, prompt: str, continuation: str, *, device: str):
    return _continuation_logprobs(model, tokenizer, prompt, [continuation], device=device)[0]


def _continuation_logprobs(model, tokenizer, prompt: str, continuations: Sequence[str], *, device: str):
    import torch

    prompt_ids = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).input_ids.to(device)
    continuation_id_rows = [
        tokenizer(" " + continuation, return_tensors="pt", add_special_tokens=False).input_ids[0].to(device)
        for continuation in continuations
    ]
    max_len = prompt_ids.shape[1] + max(row.shape[0] for row in continuation_id_rows)
    pad_token_id = tokenizer.pad_token_id
    if pad_token_id is None:
        pad_token_id = tokenizer.eos_token_id
    input_ids = torch.full(
        (len(continuation_id_rows), max_len),
        fill_value=pad_token_id,
        dtype=prompt_ids.dtype,
        device=device,
    )
    attention_mask = torch.zeros_like(input_ids)
    for row_index, continuation_ids in enumerate(continuation_id_rows):
        sequence = torch.cat([prompt_ids[0], continuation_ids], dim=0)
        input_ids[row_index, : sequence.shape[0]] = sequence
        attention_mask[row_index, : sequence.shape[0]] = 1
    outputs = model(input_ids=input_ids, attention_mask=attention_mask)
    log_probs = torch.log_softmax(outputs.logits, dim=-1)
    prompt_len = prompt_ids.shape[1]
    totals = []
    for row_index, continuation_ids in enumerate(continuation_id_rows):
        total = None
        for offset in range(continuation_ids.shape[0]):
            token_id = continuation_ids[offset]
            token_logp = log_probs[row_index, prompt_len - 1 + offset, token_id]
            total = token_logp if total is None else total + token_logp
        totals.append(total)
    return totals


def candidate_terminal_rewards(env: SupplierScamTrajectoryEnv) -> list[float]:
    return [
        terminal_reward_after_action(
            env.case,
            env.round_index,
            env.cash,
            env.reserve_violated,
            action,
            reward_scale=env.reward_scale,
        )
        for action in env.action_candidates()
    ]


def terminal_reward_after_action(
    case: SupplierScamCase | None,
    round_index: int,
    cash: float,
    reserve_violated: bool,
    action: TrajectoryAction,
    *,
    reward_scale: float,
) -> float:
    if case is None:
        raise RuntimeError("call reset() before computing candidate rewards")
    round_spec = case.rounds[round_index]
    option = None if action.is_no_order else _supplier_by_id(round_spec, action.supplier_id)
    if option is None and not action.is_no_order:
        return -1.0
    chosen_cash = cash_after_order(cash, round_spec, option, action.units)
    violated = reserve_violated or order_reserve_violation(
        cash,
        case.min_cash_reserve,
        round_spec,
        option,
        action.units,
        chosen_cash,
    )
    cash_cursor = chosen_cash
    for future_round in case.rounds[round_index + 1 :]:
        supplier_id, units, _ = choose_order(cash_cursor, case.min_cash_reserve, future_round)
        future_option = None if supplier_id == "none" else _supplier_by_id(future_round, supplier_id)
        cash_cursor = cash_after_order(cash_cursor, future_round, future_option, units)
    oracle_cash = oracle_final_cash(case)
    raw_regret = oracle_cash - cash_cursor
    reserve_penalty = 2.0 * case.min_cash_reserve if violated else 0.0
    return terminal_reward_from_regret(raw_regret + reserve_penalty, reward_scale=reward_scale)


def _dedupe_actions(actions: Iterable[TrajectoryAction]) -> list[TrajectoryAction]:
    seen = set()
    deduped = []
    for action in actions:
        key = (action.supplier_id, int(action.units))
        if key not in seen:
            seen.add(key)
            deduped.append(TrajectoryAction(action.supplier_id, int(action.units)))
    return deduped


def _step_json(step: TrajectoryStep) -> dict:
    data = asdict(step)
    data["action"] = asdict(step.action)
    data["oracle_action"] = asdict(step.oracle_action)
    return data


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Supplier-scam trajectory RLVR demo")
    parser.add_argument("--model", default="sshleifer/tiny-gpt2")
    parser.add_argument("--episodes", type=int, default=30)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--kl-coef", type=float, default=0.02)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--max-cases", type=_positive_int, default=None)
    parser.add_argument("--eval-every", type=int, default=10)
    parser.add_argument(
        "--trainer",
        choices=("verifier_guided", "reinforce"),
        default="verifier_guided",
        help="verifier_guided is low-variance and fast; reinforce is sparse sampled policy gradient.",
    )
    parser.add_argument(
        "--scripted-baselines",
        action="store_true",
        help="Print oracle/baseline verifier scores without importing torch or transformers.",
    )
    parser.add_argument("--json", action="store_true", help="Print final result JSON only.")
    args = parser.parse_args(argv)
    cases = tuple(DEFAULT_CASES[: args.max_cases] if args.max_cases is not None else DEFAULT_CASES)
    if args.scripted_baselines:
        payload = run_scripted_baselines(cases=cases)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(format_scripted_baselines(payload))
        if args.episodes <= 0:
            return 0
    if args.episodes <= 0:
        return 0
    result = train_tiny_lm_policy(
        model_name=args.model,
        episodes=args.episodes,
        lr=args.lr,
        kl_coef=args.kl_coef,
        temperature=args.temperature,
        seed=args.seed,
        device=args.device,
        max_cases=args.max_cases,
        eval_every=args.eval_every,
        trainer=args.trainer,
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
