# AERead OpenAI Build Lab - Master Tracking Ledger

Last updated: 2026-05-30

This is the review ledger for the private OpenAI-only build-lab stack. It tracks
what each atomic PR adds, what each task currently measures, which commands were
run, the observed results, and which claims are still only provisional.

Private review repo:
`https://github.com/LEE-CHENYU/aeread-openai-build-lab-review`

Working copies:

| Path | Role | Current expectation |
|---|---|---|
| `/Users/lichenyu/aeread_review_split` | private stacked PR repo | atomic review branches only |
| `/Users/lichenyu/agenteconreadiness_build_lab_20260529` | integrated build lab | cherry-picked stack for end-to-end checks |
| `/Users/lichenyu/agenteconreadiness` | original methodology repo | source-of-truth docs; do not mutate for build-lab PRs |
| `/Users/lichenyu/persona_simulator` | original sprint/rationale repo | source-of-truth sprint toys; do not mutate for build-lab PRs |

## Current validation stance

The current stack is useful as a private review scaffold, not as a leaderboard.
The validated path is:

1. Add a deterministic generator.
2. Add a mechanical oracle.
3. Add a no-API offline baseline that exposes the intended failure mode.
4. Add a thin OpenAI Responses API path.
5. Treat parse rate as a first-class result; do not interpret economic metrics
   when parse rate is below 1.00.

The strongest current evidence is not "new games are better"; it is that the
regime-appropriateness and deployment-pressure lens can be made runnable,
judge-free, and API-testable while staying OpenAI-only.

## Private PR stack

| PR | Branch | Adds | Current result |
|---:|---|---|---|
| 1 | `review/01-openai-runtime` | OpenAI-only runtime scaffold and offline oracle path | validated by unit tests and offline oracle run |
| 2 | `review/02-cached-sweep` | cached sweep runner | validated by sweep output and cache-disabled runs |
| 3 | `review/03-bargaining-gate-grade` | bargaining gate/grade task | oracle 0 grade error; gate baseline exposes grade error |
| 4 | `review/04-market-competition` | market price competition task | oracle near-zero equilibrium gap; collusive/high/cost baselines fail |
| 5 | `review/05-prompt-hygiene` | removes oracle leakage from prompts | covered by prompt hygiene unit test |
| 6 | `review/06-auction-mechanism` | configured reserve mechanism task | oracle 0 reserve error; revenue default fails configured objectives |
| 7 | `review/07-strategic-drift` | repeated strategic drift task | oracle drift 0; myopic drift 1.00 |
| 8 | `review/08-exploration` | unknown-environment exploration task | oracle gap 0; exploit-only baseline gap 193.3 |
| 9 | `review/09-retail-survival` | retail/runway survival task | oracle ruin 0; current greedy baseline does not separate on primary ruin |
| 10 | `review/10-belief-bargaining` | belief/cue bargaining task | oracle gap 0; prior baseline gap 8.84271 |
| 11 | `review/11-principal-inference` | CRRA principal inference task | oracle fraction error 0; generic-gamma error 0.408333 |
| 12 | `review/12-ambiguity-maxmin` | maxmin ambiguity task | oracle regret 0; reference-prior regret 17.9167 |
| 13 | `review/13-mechanism-choice` | mechanism-choice task | oracle score regret 0; revenue/risk-blind baselines fail |
| 14 | `review/14-experiment-design` | noisy experiment design task | oracle gap 0; greedy baseline gap 141.505 |
| 15 | `review/15-portfolio-choice` | configured portfolio choice task | oracle regret 0; max-return regret 0.599325 |
| 16 | `review/16-matching-market` | matching market task | oracle regret 0; max-value/access baselines fail |
| 17 | `review/17-contract-screening` | adverse-selection contract screening task | oracle regret 0; max-profit/constraint-blind baselines fail |
| 18 | `review/18-moral-hazard` | hidden-action moral hazard task | oracle regret 0; hidden-action blind regret 49.3375 |
| 19 | `review/19-openai-mini-nano-aliases` | OpenAI alias correction | `mini -> gpt-5.4-mini`; `nano -> gpt-5.4-nano` |
| 20 | `review/20-common-value-auction` | common-value auction/winner's-curse guardrail | oracle regret 0; winner-curse blind regret 17.3875 |
| 21 | `review/21-openai-response-budget` | safer OpenAI Responses settings | low reasoning, low verbosity, `store=false`, incomplete-response errors |
| 22 | `review/22-response-content-extraction` | robust OpenAI response text extraction | text chunks collected; incomplete/textless responses fail loudly |
| 23 | `review/23-openai-nano-budget` | nano-safe output budget | default output budget raised to 1200 |
| 24 | `review/24-parse-rate-reporting` | parse-rate reporting in sweeps | live/offline sweeps display parse rate |
| 25 | `review/25-master-tracking-doc` | this master tracking ledger | validation results recorded here |
| 26 | `review/26-regime-breadth` | broader regime battery and barrier-violation reporting | oracle rank 1 on 32 trials; EV baseline error 0.586033 and CVaR violation 0.88 |

## Task result ledger

All results below are from the current private review stack on 2026-05-29 unless
explicitly marked as historical/upstream.

| Task | Axis / purpose | Current offline result | Interpretation / limitation |
|---|---|---|---|
| `regime` | four-regime EV/Kelly/CVaR/CRRA utility selection | oracle mean absolute error 0 across 32 trials; EV baseline error 0.586033; EV CVaR drawdown-violation rate 0.88; all targeted parses 1.00 | broadened to even-money, skewed, thin-edge, negative-EV, small-edge, and hard-barrier gamble families |
| `principal_inference` | infer configured principal CRRA parameter | oracle error 0; generic-gamma error 0.408333 | grade-side CRRA mismatch is mechanically measurable |
| `portfolio` | configured-principal portfolio choice | oracle regret 0; max-return regret 0.599325; low-risk regret 0.0241 | separates return-chasing from configured utility |
| `ambiguity` | maxmin under Knightian ambiguity | oracle robust regret 0; reference-prior regret 17.9167 | exposes collapse to one prior |
| `bargaining` | D2/TERMS-style gate plus grade | oracle grade error 0; generic gate baseline grade error 0.4375 | confirms "gate-only surplus extraction" is not grade fidelity |
| `belief_bargaining` | cue use and posterior bargaining | oracle surplus gap 0; prior baseline gap 8.84271 | high-anchor baseline ties primary metric in current cases; keep prior baseline as main failure mode |
| `market` | simultaneous price competition | oracle equilibrium gap 0.000179; collusive gap 1.0001; cost/high worse | gate under competition is measurable; parse is n/a for this aggregate result |
| `matching` | stability/access-aware matching | oracle regret 0; access regret 51.675; max-value regret 175.037 | separates value maximization from stability/access constraints |
| `screening` | adverse-selection contract menus | oracle regret 0; constraint-blind regret 37.7125; max-profit regret 71.5061 | exposes IC/IR blind menus |
| `moral_hazard` | hidden-action contract design | oracle profit regret 0; high-bonus regret 20.5875; hidden-action blind/fixed regret 49.3375 | exposes assuming effort for free |
| `auction` | configured reserve choice | oracle reserve error 0; revenue baseline error 0.221354 | separates Myerson revenue reserve from configured objective |
| `common_value` | winner's curse guardrail | oracle profit regret 0; winner-curse blind regret 17.3875; aggressive regret 46.72 | good capability-scaling guardrail; historical live run found smaller OpenAI models miss and `gpt-5.5` solves |
| `mechanism` | choose among allocation mechanisms | oracle score regret 0; risk-blind regret 26.5; revenue regret 66.6 | separates revenue default from risk-aware mechanism choice |
| `strategic_drift` | repeated strategic discipline | oracle drift 0; myopic drift 1.00 | captures long-horizon drift scaffold |
| `exploration` | unknown-environment exploration | oracle EV gap 0; exploit-only gap 193.3 | EconEvals-style exploration failure is mechanically exposed |
| `experiment_design` | noisy experiment design and update | oracle EV gap 0; greedy gap 141.505 | exposes skipping valuable experiments |
| `retail` | cash/runway survival | oracle ruin 0; greedy ruin 0 on current cases | primary ruin metric does not yet discriminate the greedy baseline; broaden scenarios or track cash/order secondary metrics |
| `procurement` | v0 qualitative procurement | oracle accuracy 1.00; first baseline 0.50 | current live OpenAI smoke also parses cleanly |
| `pricing` | v0 continuous pricing | oracle revenue gap 0; rounded baseline gap 87.5 | validates continuous-action scoring |
| `scam` | adversarial belief-manipulation arena | oracle overpay 0; careful overpay 6.66667; credulous overpay 133.333; instrument fires | working judge-free dynamic range; single-shot frontier scam resistance should not be confused with long-horizon Vending-Bench failures |

## Current validation run

Commands run from `/Users/lichenyu/aeread_review_split`. Full-stack checks before
PR 26 were run on `review/25-master-tracking-doc`; PR 26-specific checks were
run on `review/26-regime-breadth`.

| Check | Command | Result |
|---|---|---|
| Unit tests | `python3 -m unittest discover -s tests -p 'test_*.py'` | 53 tests passed in 0.279s after PR 26 |
| Full offline oracle task pass | `python3 -m aeread_lab.cli --task all --agent offline:oracle --no-cache` | all 20 task runners executed; oracle errors/regrets zero or expected near-zero; scam control `instrument_fires=True` |
| Regime differential sweep | `python3 -m aeread_lab.cli --sweep --task regime --agents offline:oracle,offline:ev,offline:kelly,offline:cvar,offline:half --no-cache` | oracle rank 1; EV baseline error 0.586033; CVaR/Kelly baselines error 0.224185; half baseline error 0.429783; parse 1.00 for all rows |
| Regime oracle/barrier smoke | `python3 -m aeread_lab.cli --task regime --agent offline:oracle --no-cache` | 32 trials; oracle mean absolute error 0; wealth destruction 0.00; CVaR drawdown violation 0.00 |
| Principal/portfolio/ambiguity sweeps | task-specific sweeps with oracle and known-bad baselines | oracle rank 1 on all; bad baselines expose intended failure modes |
| Bargaining/belief/market sweeps | task-specific sweeps with oracle and known-bad baselines | oracle rank 1 for bargaining and market; belief prior baseline fails; high-anchor ties current primary metric |
| Matching/screening/mechanism sweeps | task-specific sweeps with oracle and known-bad baselines | oracle rank 1 on all; bad baselines expose intended failure modes |
| Strategic/exploration/experiment/retail/scam sweeps | task-specific sweeps with oracle and known-bad/control baselines | oracle rank 1 except retail primary metric ties greedy; scam dynamic range validated |
| Auction/procurement/pricing sweeps | task-specific sweeps with oracle and known-bad baselines | oracle rank 1; procurement/pricing parse 1.00 |
| All-task JSON smoke | `python3 -m aeread_lab.cli --sweep --task all --agents offline:oracle,offline:ev --no-cache --json` | saved 2 runs and 40 result rows to `/tmp/aeread_review_all_oracle_ev_sweep.json` |
| Whitespace check | `git diff --check` | passed with no output |
| Provider guardrail scan | `rg -n "OpenRouter|Anthropic|anthropic/|claude|OPENAI_BASE_URL" aeread_lab tests docs/build_lab.md pyproject.toml` | only expected documentation/test guardrail matches: `docs/build_lab.md` says no Anthropic/OpenRouter path; test rejects a Claude alias |

### Live OpenAI API validation

The API key was supplied interactively through `read -s OPENAI_API_KEY`, used for
the live smoke, then unset. It is not stored in the repo.

| Live check | Result | Interpretation |
|---|---|---|
| `python3 -m aeread_lab.cli --sweep --task procurement --agents openai:nano,openai:mini --no-cache` | completed; `openai:mini` accuracy 1.00, parse 1.00; `openai:nano` accuracy 0.50, parse 1.00 | current OpenAI Responses path, alias mapping, output budget, parsing, and parse-rate reporting work for mini/nano |
| `python3 -m aeread_lab.cli --sweep --task common_value --agents openai:nano,openai:mini,openai:gpt-5.5 --no-cache` | attempted, interrupted after more than 3 minutes with no completed output | not counted as a result; use smaller current live smokes or cached/historical `gpt-5.5` evidence until latency is controlled |

Historical live API findings from earlier in this private stack:

| Finding | Result | What changed because of it |
|---|---|---|
| `gpt-5.5-mini` and `gpt-5.5-nano` did not exist | live model list showed `gpt-5.4-mini` and `gpt-5.4-nano` | PR 19 fixed aliases |
| `gpt-5.5` produced blank scored outputs at 400 tokens | raw response was `status=incomplete`, reason `max_output_tokens` | PR 21 made incomplete/textless responses hard failures |
| response chunks could be missed | output text sometimes lived in nested content chunks | PR 22 added robust extraction |
| `nano` could still exhaust 800 tokens | direct probe worked at 1200 | PR 23 raised default output budget |
| common-value live smoke separated model scale | `nano` regret 21.6325, `mini` regret 7.5125, `gpt-5.5` regret 0 | interpret as a capability-scaling guardrail, not a frontier discriminator |

## Original repo commit check

Checked on 2026-05-29 before writing this ledger and rechecked on
2026-05-30 before PR 26.

| Repo | Status | New/relevant commits checked | Consequence for private build lab |
|---|---|---|---|
| `/Users/lichenyu/agenteconreadiness` (`origin/main`) | clean at `a0e17b1`; no newer fetched commits on 2026-05-30 | `c3520ac` review corrections; `f69e883` OSS availability / borrow-substrate strategy; `a0e17b1` read-first refocus doc | no code to import; ledger aligns with refocus: rationality is floor, headline axes are regime-appropriateness, alignment-shift, steerability |
| `/Users/lichenyu/persona_simulator` (`origin/master`) | dirty: modified `sprint/adversarial_scam_arena_toy/exploits.json`; untracked `.playwright-mcp/` logs; no newer fetched commits on 2026-05-30 | `47acd7a` GPT-5.x support/model override; `8404d2a` OpenAI scam-arena run; `c1fbbd0` borrow-substrate doc; `121e2e0` cross-model scam result + timeout/label fixes | record upstream evidence only; do not import OpenRouter/chat-completions client into this Responses-only lab |

Upstream sprint finding to preserve: OpenAI scam-arena run with `gpt-5.5`
attacker and `gpt-5.5`/`gpt-5.4-mini` defenders found both frontier OpenAI
defenders resistant in the single-shot scam setting. That revises the adversarial
interpretation: the scam arena is a valid instrument, but the Vending-Bench
"falls for scam suppliers" failure likely needs long-horizon stress, not a clean
one-shot value estimate.

Uncommitted original-repo artifacts are intentionally left untouched. The private
build lab should not depend on `.playwright-mcp/` logs or the local
`exploits.json` mutation.

## Approach decisions locked by validation

1. Do not add new tasks blindly. Each new task needs an oracle, a failure
   baseline, and either an immediate offline validation or a cheap OpenAI smoke.
2. Do not interpret economic metrics without parse rate. Parse failures are eval
   failures first.
3. Treat `common_value` as a smaller-model capability guardrail unless repeated
   frontier failures appear.
4. Treat single-shot scam resistance as a robust null, not evidence that
   long-horizon scam susceptibility is solved.
5. Keep the private lab OpenAI Responses API only. Original sprint code can
   inform design but should not pull in OpenRouter, Anthropic aliases, or
   chat-completions-specific behavior.
6. The next build should be selected by the refocus doc: broaden
   regime-appropriateness (more gamble families, CVaR barrier, configured CRRA)
   or make the adversarial arena long-horizon. Do not pivot to another headline
   axis before those are validated.
