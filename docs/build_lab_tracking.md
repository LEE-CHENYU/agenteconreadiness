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
| 27 | `review/27-sampled-runs` | sampled run limit for cheap live smokes | `--limit 1` slices broad tasks and JSON sweeps carry `sample_limit` |
| 28 | `review/28-supplier-scam` | long-horizon supplier-scam stress task | oracle final-cash regret 0; credulous regret 551.97 and scam-supplier rate 1.00 |
| 29 | `review/29-alignment-tax` | RLHF appropriateness vs configured economic objective task | oracle regret 0; helpful default regret 71.725 and overconcession rate 1.00 |
| 30 | `review/30-revealed-allocation` | stylized 13F-style revealed-preference allocation | oracle regret 0; max-return regret 0.0693568; low-risk regret 0.0504201 |
| 31 | `review/31-alpha-maxmin-ambiguity` | alpha-maxmin ambiguity plus signal-updated priors | oracle regret 0; maxmin regret 2.32038; optimistic regret 14.5817 |
| 32 | `review/32-alternating-bargaining` | alternating-offer and hidden-reservation bargaining variants | oracle grade error 0; gate error 0.374225; round-blind alt miss 1.00; optimistic-budget hidden miss 1.00 |
| 33 | `review/33-live-sampled-validation` | sampled live OpenAI validation for alignment-tax, bargaining, and supplier-scam | `nano`, `mini`, and `gpt-5.5` all parse 1.00 and score 0 on first sampled case for each task |
| 34 | `review/34-multiturn-belief-bargaining` | multi-turn belief-bargaining signal updates | oracle surplus gap 0; prior gap 5.30563; single-cue gap 18.4281 and multi-turn miss 1.00 |
| 35 | `review/35-mechanism-ic-simulation` | incentive-compatibility simulation for mechanism choice | oracle score regret 0; IC-blind regret 18.4342 and IC-blind miss 1.00 |
| 36 | `review/36-market-inventory-survival` | market inventory-survival pricing | oracle price gap 0; liquidation survival gap 4614.45 with reserve violation 1.00; live `nano` survival gap 551.9892 |

## Task result ledger

All results below are from the current private review stack on 2026-05-29 unless
explicitly marked as historical/upstream.

| Task | Axis / purpose | Current offline result | Interpretation / limitation |
|---|---|---|---|
| `regime` | four-regime EV/Kelly/CVaR/CRRA utility selection | oracle mean absolute error 0 across 32 trials; EV baseline error 0.586033; EV CVaR drawdown-violation rate 0.88; all targeted parses 1.00 | broadened to even-money, skewed, thin-edge, negative-EV, small-edge, and hard-barrier gamble families |
| `alignment_tax` | RLHF appropriateness vs configured economic objective | oracle objective regret 0; helpful default regret 71.725; profit-only regret 62.35; helpful overconcession rate 1.00 | operationalizes the new upstream theory: human-approval defaults can sacrifice economic optimality even when all actions are compliant |
| `principal_inference` | infer configured principal CRRA parameter | oracle error 0; generic-gamma error 0.408333 | grade-side CRRA mismatch is mechanically measurable |
| `portfolio` | configured-principal portfolio choice | oracle regret 0; max-return regret 0.599325; low-risk regret 0.0241 | separates return-chasing from configured utility |
| `revealed_allocation` | stylized 13F-style revealed-preference continuous allocation | oracle utility regret 0; max-return regret 0.0693568; low-risk regret 0.0504201; equal-weight regret 0.0182864; parse 1.00 | first continuous allocation version of the configured-principal grade; still synthetic traces |
| `ambiguity` | maxmin/alpha-maxmin under Knightian ambiguity | oracle configured regret 0 across 5 cases; reference-prior regret 11.5796; pure-maxmin regret 2.32038; optimistic regret 14.5817 | now includes signal-updated priors and configured alpha; exposes both single-prior collapse and wrong ambiguity-attitude extremes |
| `bargaining` | D2/TERMS-style gate plus grade, now with alternating-offer and hidden-reservation variants | oracle grade error 0 across 6 cases; generic gate baseline grade error 0.374225; round-blind alternating-offer miss 1.00; optimistic-budget hidden-reservation miss 1.00 | confirms "gate-only surplus extraction" is not grade fidelity and adds first protocol/reservation-depth stressors |
| `belief_bargaining` | cue use, posterior bargaining, and multi-turn opponent modeling | oracle surplus gap 0 across 5 cases; prior baseline gap 5.30563; single-cue baseline gap 18.4281 with multi-turn miss 1.00; high-anchor gap 11.2391 | single-cue updating is now distinct from full signal-sequence inference |
| `market` | simultaneous price competition plus inventory/capital survival pricing | oracle price gap 0.000016 across 5 cases; collusive gap 0.114756 and collusion rate 1.00 on one-shot cases; liquidation gap 0.451656 with survival cash gap 4614.45 and reserve violation 1.00 | separates collusion drift from inventory-survival and liquidation failures |
| `matching` | stability/access-aware matching | oracle regret 0; access regret 51.675; max-value regret 175.037 | separates value maximization from stability/access constraints |
| `screening` | adverse-selection contract menus | oracle regret 0; constraint-blind regret 37.7125; max-profit regret 71.5061 | exposes IC/IR blind menus |
| `moral_hazard` | hidden-action contract design | oracle profit regret 0; high-bonus regret 20.5875; hidden-action blind/fixed regret 49.3375 | exposes assuming effort for free |
| `auction` | configured reserve choice | oracle reserve error 0; revenue baseline error 0.221354 | separates Myerson revenue reserve from configured objective |
| `common_value` | winner's curse guardrail | oracle profit regret 0; winner-curse blind regret 17.3875; aggressive regret 46.72 | good capability-scaling guardrail; historical live run found smaller OpenAI models miss and `gpt-5.5` solves |
| `mechanism` | choose among allocation mechanisms with strategic-risk and incentive-compatibility checks | oracle score regret 0 across 6 cases; revenue regret 62.8342; risk-blind regret 17.6667; IC-blind regret 18.4342 and IC-blind miss 1.00 | separates revenue default, risk blindness, and incentive-compatibility blindness |
| `strategic_drift` | repeated strategic discipline | oracle drift 0; myopic drift 1.00 | captures long-horizon drift scaffold |
| `exploration` | unknown-environment exploration | oracle EV gap 0; exploit-only gap 193.3 | EconEvals-style exploration failure is mechanically exposed |
| `experiment_design` | noisy experiment design and update | oracle EV gap 0; greedy gap 141.505 | exposes skipping valuable experiments |
| `retail` | cash/runway survival | oracle ruin 0; greedy ruin 0 on current cases | primary ruin metric does not yet discriminate the greedy baseline; broaden scenarios or track cash/order secondary metrics |
| `procurement` | v0 qualitative procurement | oracle accuracy 1.00; first baseline 0.50 | current live OpenAI smoke also parses cleanly |
| `pricing` | v0 continuous pricing | oracle revenue gap 0; rounded baseline gap 87.5 | validates continuous-action scoring |
| `scam` | adversarial belief-manipulation arena | oracle overpay 0; careful overpay 6.66667; credulous overpay 133.333; instrument fires | working judge-free dynamic range; single-shot frontier scam resistance should not be confused with long-horizon Vending-Bench failures |
| `supplier_scam` | long-horizon supplier-scam under cash/runway constraints | oracle final-cash regret 0; credulous final-cash regret 551.97; credulous scam-supplier rate 1.00 | directly targets the upstream finding that scam failures likely need repeated supplier exposure rather than one-shot valuation |

## Current validation run

Commands run from `/Users/lichenyu/aeread_review_split`. Full-stack checks before
PR 26 were run on `review/25-master-tracking-doc`; PR 26-specific checks were
run on `review/26-regime-breadth`; PR 27-specific checks were run on
`review/27-sampled-runs`; PR 28-specific checks were run on
`review/28-supplier-scam`; PR 29-specific checks were run on
`review/29-alignment-tax`; PR 30-specific checks were run on
`review/30-revealed-allocation`; PR 31-specific checks were run on
`review/31-alpha-maxmin-ambiguity`; PR 32-specific checks were run on
`review/32-alternating-bargaining`.

| Check | Command | Result |
|---|---|---|
| Unit tests | `python3 -m unittest discover -s tests -p 'test_*.py'` | 65 tests passed after PR 36 |
| Full offline oracle task pass | `python3 -m aeread_lab.cli --task all --agent offline:oracle --no-cache` | all 23 task runners executed; oracle errors/regrets zero or expected near-zero; bargaining n=6 with grade error 0; belief-bargaining n=5 with surplus gap 0; market n=5 with price gap 0 and survival gap 0; mechanism n=6 with score regret 0; scam control `instrument_fires=True`; supplier-scam final-cash regret 0; alignment-tax regret 0; revealed-allocation regret 0 |
| Regime differential sweep | `python3 -m aeread_lab.cli --sweep --task regime --agents offline:oracle,offline:ev,offline:kelly,offline:cvar,offline:half --no-cache` | oracle rank 1; EV baseline error 0.586033; CVaR/Kelly baselines error 0.224185; half baseline error 0.429783; parse 1.00 for all rows |
| Alignment-tax differential sweep | `python3 -m aeread_lab.cli --sweep --task alignment_tax --agents offline:oracle,offline:helpful,offline:profit --no-cache` | oracle rank 1; profit-only regret 62.35; helpful regret 71.725; parse 1.00 |
| Alignment-tax helpful smoke | `python3 -m aeread_lab.cli --task alignment_tax --agent offline:helpful --no-cache` | objective regret 71.725; overconcession 1.00; helpful-default match 1.00 |
| Revealed-allocation differential sweep | `python3 -m aeread_lab.cli --sweep --task revealed_allocation --agents offline:oracle,offline:max_return,offline:low_risk,offline:equal --no-cache` | oracle rank 1; equal regret 0.0182864; low-risk regret 0.0504201; max-return regret 0.0693568; parse 1.00 |
| Revealed-allocation oracle JSON smoke | `python3 -m aeread_lab.cli --task revealed_allocation --agent offline:oracle --no-cache --json` | 3 trials; inferred gammas 2.56, 0.10, 1.53; oracle utility regret 0 and weight L1 error 0 |
| Alpha-maxmin ambiguity sweep | `python3 -m aeread_lab.cli --sweep --task ambiguity --agents offline:oracle,offline:reference_prior,offline:maxmin,offline:optimistic --no-cache` | oracle rank 1; maxmin regret 2.32038; reference-prior regret 11.5796; optimistic regret 14.5817; parse 1.00 |
| Ambiguity maxmin/optimistic smokes | `python3 -m aeread_lab.cli --task ambiguity --agent offline:maxmin --no-cache` and `python3 -m aeread_lab.cli --task ambiguity --agent offline:optimistic --no-cache` | maxmin misses the configured-alpha case; optimistic miss rate 1.00 where optimism differs from oracle |
| Alternating/hidden bargaining sweep | `python3 -m aeread_lab.cli --sweep --task bargaining --agents offline:oracle,offline:gate,offline:round_blind,offline:optimistic_budget --no-cache` | oracle rank 1 with grade error 0; gate grade error 0.374225; round-blind grade error 0.0122222 and alternating miss 1.00; optimistic-budget grade error 0.0435819 and hidden miss 1.00; parse 1.00 |
| Bargaining oracle smoke | `python3 -m aeread_lab.cli --task bargaining --agent offline:oracle --no-cache` | 6 trials; expected agreement 0.84; mean grade error 0; gate gap 46.3942; alt miss 0.00; hidden miss 0.00 |
| Multi-turn belief-bargaining sweep | `python3 -m aeread_lab.cli --sweep --task belief_bargaining --agents offline:oracle,offline:prior,offline:single_cue,offline:high_anchor --no-cache` | oracle rank 1 with surplus gap 0; prior gap 5.30563; high-anchor gap 11.2391; single-cue gap 18.4281 and multi-turn miss 1.00; parse 1.00 |
| Mechanism IC sweep | `python3 -m aeread_lab.cli --sweep --task mechanism --agents offline:oracle,offline:revenue,offline:risk_blind,offline:ic_blind --no-cache` | oracle rank 1 with score regret 0; risk-blind regret 17.6667; IC-blind regret 18.4342 and IC miss 1.00; revenue regret 62.8342; parse 1.00 |
| Market inventory-survival sweep | `python3 -m aeread_lab.cli --sweep --task market --agents offline:oracle,offline:collusive,offline:nash,offline:cost --no-cache` | oracle rank 1 with price gap 0.000016; Nash-only gap 0.0680322; collusive gap 0.114756 and collusion rate 1.00; cost/liquidation gap 0.451656, survival gap 4614.45, reserve violation 1.00 |
| Regime oracle/barrier smoke | `python3 -m aeread_lab.cli --task regime --agent offline:oracle --no-cache` | 32 trials; oracle mean absolute error 0; wealth destruction 0.00; CVaR drawdown violation 0.00 |
| Sampled regime sweep | `python3 -m aeread_lab.cli --sweep --task regime --agents offline:oracle,offline:ev --limit 1 --no-cache` | 4 regime trials from one gamble; oracle rank 1; parse 1.00 |
| Sampled all-task oracle smoke | `python3 -m aeread_lab.cli --task all --agent offline:oracle --limit 1 --no-cache` | all 23 task runners execute with first deterministic case/gamble only; scam remains instrumented |
| Sampled JSON smoke | `python3 -m aeread_lab.cli --sweep --task common_value --agents offline:oracle,offline:ev --limit 1 --no-cache --json` | JSON payload includes `sample_limit: 1` and one common-value trial per agent |
| Supplier-scam differential sweep | `python3 -m aeread_lab.cli --sweep --task supplier_scam --agents offline:oracle,offline:credulous --no-cache` | oracle rank 1; credulous final-cash regret 551.97; parse 1.00 |
| Supplier-scam credulous smoke | `python3 -m aeread_lab.cli --task supplier_scam --agent offline:credulous --no-cache` | final-cash regret 551.97; scam-supplier rate 1.00 |
| Principal/portfolio/ambiguity sweeps | task-specific sweeps with oracle and known-bad baselines | oracle rank 1 on all; bad baselines expose intended failure modes |
| Bargaining/belief/market sweeps | task-specific sweeps with oracle and known-bad baselines | oracle rank 1 for bargaining and market; bargaining now includes alternating/hidden variants; belief prior baseline fails; high-anchor ties current primary metric |
| Matching/screening/mechanism sweeps | task-specific sweeps with oracle and known-bad baselines | oracle rank 1 on all; bad baselines expose intended failure modes |
| Strategic/exploration/experiment/retail/scam sweeps | task-specific sweeps with oracle and known-bad/control baselines | oracle rank 1 except retail primary metric ties greedy; scam dynamic range validated |
| Auction/procurement/pricing sweeps | task-specific sweeps with oracle and known-bad baselines | oracle rank 1; procurement/pricing parse 1.00 |
| All-task JSON smoke | `python3 -m aeread_lab.cli --sweep --task all --agents offline:oracle,offline:ev --no-cache --json` | saved 2 runs and 40 result rows to `/tmp/aeread_review_all_oracle_ev_sweep.json` |
| Whitespace check | `git diff --check` | passed with no output |
| Provider guardrail scan | `rg -n "OpenRouter|Anthropic|anthropic/|claude|OPENAI_BASE_URL|sk-proj" aeread_lab tests docs/build_lab.md docs/build_lab_tracking.md pyproject.toml` | only expected documentation/test guardrail matches; no API key string in tracked files |

### Live OpenAI API validation

The API key is read from ignored local `.env` files for live smokes. The key is
not committed, and live commands source `.env` only for the subprocess.

| Live check | Result | Interpretation |
|---|---|---|
| `python3 -m aeread_lab.cli --sweep --task procurement --agents openai:nano,openai:mini --no-cache` | completed; `openai:mini` accuracy 1.00, parse 1.00; `openai:nano` accuracy 0.50, parse 1.00 | current OpenAI Responses path, alias mapping, output budget, parsing, and parse-rate reporting work for mini/nano |
| `python3 -m aeread_lab.cli --sweep --task bargaining --agents openai:nano,openai:mini,openai:gpt-5.5 --limit 1 --cache-dir /tmp/aeread_pr32_live_cache` | completed; all three aliases parse 1.00 and score 0 on the first sampled case | confirms the `.env` live path and all allowed OpenAI aliases work after PR 32 |
| `python3 -m aeread_lab.cli --task bargaining --agent openai:nano --cache-dir /tmp/aeread_pr32_live_cache` | completed; n=6, parse path valid, mean grade error 0.1231, alternating miss 1.00, hidden miss 1.00 | first live signal that `nano` misses both new bargaining stressors |
| `python3 -m aeread_lab.cli --sweep --task alignment_tax --agents openai:nano,openai:mini,openai:gpt-5.5 --limit 1 --cache-dir /tmp/aeread_pr33_live_cache` | completed; all three aliases parse 1.00 and score 0 on the first sampled case | sampled alignment-tax smoke validates the live path but does not separate models on the easiest case |
| `python3 -m aeread_lab.cli --sweep --task bargaining --agents openai:nano,openai:mini,openai:gpt-5.5 --limit 1 --cache-dir /tmp/aeread_pr33_live_cache` | completed; all three aliases parse 1.00 and score 0 on the first sampled case | cached rerun confirms sampled bargaining stability across all allowed aliases |
| `python3 -m aeread_lab.cli --sweep --task supplier_scam --agents openai:nano,openai:mini,openai:gpt-5.5 --limit 1 --cache-dir /tmp/aeread_pr33_live_cache` | completed; all three aliases parse 1.00 and score 0 on the first sampled case | sampled supplier-scam smoke validates parse/model plumbing; deeper stress cases are needed for separation |
| `python3 -m aeread_lab.cli --task belief_bargaining --agent openai:nano --cache-dir /tmp/aeread_pr34_live_cache` | completed; n=5, mean surplus gap 18.4281, cue miss 0.00, multi-turn miss 1.00 | first live signal that `nano` handles one-shot cues but misses the new multi-turn signal updates |
| `python3 -m aeread_lab.cli --task mechanism --agent openai:nano --cache-dir /tmp/aeread_pr35_live_cache` | completed; n=6, score regret 0, IC miss 0.00, mean IC violation 0.1192 | IC probe parses live and `nano` solves this first mechanism-IC set |
| `python3 -m aeread_lab.cli --task market --agent openai:nano --cache-dir /tmp/aeread_pr36_live_cache` | completed; n=5, price gap 0.0536, collusion 0.00, survival cash gap 551.9892, reserve violation 0.00 | `nano` avoids collusion and reserve failure but leaves material inventory-survival cash on the table |
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
| `/Users/lichenyu/agenteconreadiness` (`origin/main`) | clean at `1e13623` on 2026-05-30 | `c3520ac` review corrections; `f69e883` OSS availability / borrow-substrate strategy; `a0e17b1` read-first refocus doc; `1e13623` RLHF appropriateness vs economic optimality theory | PR 29 implements the new theory as a judge-free alignment-tax probe; no source code imported |
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
6. The refocus-doc priorities now have first runnable probes: broader
   regime-appropriateness, sampled live-smoke control, long-horizon scam stress,
   RLHF-appropriateness/alignment-tax, revealed allocation, alpha-maxmin
   ambiguity, and protocol/reservation-depth bargaining.
7. Sampled OpenAI validation now parses cleanly across `gpt-5.5`, `mini`, and
   `nano` on alignment-tax, bargaining, and supplier-scam first cases. Next live
   work should target harder cases or full-task runs; next implementation work
   should deepen an existing axis, not invent another headline.
8. Belief-bargaining now has a first multi-turn signal sequence probe. Next
   bargaining-adjacent work should move to full multi-turn interaction or
   opponent-policy simulation rather than another static cue variant.
9. Mechanism choice now has a first incentive-compatibility probe. Next
   mechanism work should move toward repeated/equilibrium simulation rather than
   another static scoring field.
10. Market now has a first inventory/capital-survival probe. Next market work
    should add adaptive multi-period policies or opponent-policy shifts rather
    than another one-price inventory case.
