import unittest

from aeread_lab.rlvr.supplier_scam_trajectory import (
    SupplierScamTrajectoryEnv,
    candidate_terminal_rewards,
    run_scripted_baselines,
    run_scripted_policy,
)
from aeread_lab.tasks.supplier_scam import DEFAULT_CASES


class SupplierScamTrajectoryTests(unittest.TestCase):

    def test_oracle_scripted_policy_gets_zero_constrained_regret(self):
        summary = run_scripted_policy("oracle")
        self.assertEqual(summary["n_cases"], len(DEFAULT_CASES))
        self.assertLess(abs(summary["mean_constrained_final_cash_regret"]), 1e-9)
        self.assertEqual(summary["mean_terminal_reward"], 1.0)
        self.assertEqual(summary["reserve_violation_rate"], 0.0)

    def test_scripted_baselines_preserve_supplier_scam_gap(self):
        baselines = run_scripted_baselines()
        self.assertLess(abs(baselines["oracle"]["mean_constrained_final_cash_regret"]), 1e-9)
        self.assertGreater(baselines["reputation_blind"]["mean_constrained_final_cash_regret"], 1.0)
        self.assertGreater(baselines["timing_blind"]["mean_constrained_final_cash_regret"], 50.0)
        self.assertGreater(baselines["credulous"]["mean_constrained_final_cash_regret"], 100.0)

    def test_env_exposes_candidate_actions_and_terminal_verifier_info(self):
        env = SupplierScamTrajectoryEnv(cases=[DEFAULT_CASES[0]])
        observation = env.reset()
        self.assertIn("TASK: supplier_scam_trajectory_rlvr", observation)
        self.assertIn("ACTION_0", observation)
        done = False
        info = {}
        reward = 0.0
        while not done:
            observation, reward, done, info = env.step(env.scripted_action("oracle"))
        self.assertEqual(observation, "EPISODE_DONE")
        self.assertEqual(reward, 1.0)
        self.assertIn("terminal", info)
        self.assertLess(abs(info["terminal"]["constrained_final_cash_regret"]), 1e-9)
        self.assertEqual(len(info["terminal"]["steps"]), len(DEFAULT_CASES[0].rounds))

    def test_candidate_terminal_rewards_rank_oracle_action(self):
        env = SupplierScamTrajectoryEnv(cases=[DEFAULT_CASES[0]])
        env.reset()
        candidates = env.action_candidates()
        rewards = candidate_terminal_rewards(env)
        oracle = env.oracle_action()
        oracle_index = candidates.index(oracle)
        self.assertEqual(rewards[oracle_index], max(rewards))
        self.assertEqual(rewards[oracle_index], 1.0)


class FoldedEnvExtrasTests(unittest.TestCase):
    """Extras folded in from the standalone envs/ wrapper (2026-06-01):
    stochastic transitions + shaped reward, kept opt-in so defaults are unchanged."""

    def test_defaults_unchanged_expected_terminal(self):
        env = SupplierScamTrajectoryEnv(cases=[DEFAULT_CASES[0]])
        self.assertEqual(env.transition, "expected")
        self.assertEqual(env.reward_mode, "terminal")

    def test_shaped_mode_oracle_zero_regret_each_case(self):
        # oracle policy under shaped reward → ~0 episode return on every case
        # (proves the shaped path stays equivalent to the audited oracle).
        for case in DEFAULT_CASES:
            env = SupplierScamTrajectoryEnv(cases=[case], reward_mode="shaped")
            env.reset()
            total = 0.0
            done = False
            while not done:
                _, r, done, _ = env.step(env.oracle_action())
            # accumulate via step rewards
            env2 = SupplierScamTrajectoryEnv(cases=[case], reward_mode="shaped")
            env2.reset()
            done = False
            while not done:
                _, r, done, _ = env2.step(env2.oracle_action())
                total += r
            self.assertAlmostEqual(total, 0.0, places=6, msg=case.key)

    def test_stochastic_seed_reproducible(self):
        def rollout(seed):
            env = SupplierScamTrajectoryEnv(cases=[DEFAULT_CASES[0]], transition="stochastic")
            env.reset(seed=seed)
            rewards = []
            done = False
            while not done:
                cands = env.action_candidates()
                _, r, done, _ = env.step(cands[-1])  # riskiest/largest order
                rewards.append(round(r, 6))
            return rewards

        self.assertEqual(rollout(11), rollout(11))  # same seed → identical draws

    def test_stochastic_surfaces_scam_realized(self):
        env = SupplierScamTrajectoryEnv(cases=[DEFAULT_CASES[0]], transition="stochastic")
        env.reset(seed=3)
        cands = env.action_candidates()
        # pick a real order (not ACTION_0/none) so a scam draw is made
        order = next(a for a in cands if not a.is_no_order)
        _, _, _, info = env.step(order)
        self.assertIn("scam_realized", info)
        self.assertIsInstance(info["scam_realized"], bool)


if __name__ == "__main__":
    unittest.main()
