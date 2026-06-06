# Contamination resistance (by design)

**Summary.** This channel is structurally harder to contaminate than a QA / pass-rate benchmark, because it
scores **behavior against a solver, not recall of an answer** — there is no answer key to leak. Knowing RPS's
equilibrium is uniform doesn't help a model *execute* randomness; knowing a preference should be transitive
doesn't stop it being money-pumped. The design goal is to push that native advantage to "by construction":
make the scored instances **regenerable**, so there is nothing static to have been trained on.

## Residual vectors (what still leaks)
1. **Static-prompt memorization** — the exact case text + a canned, coherent-looking response.
2. **Published-solution recall** — for *solved* games (Kuhn poker GTO, prisoner's dilemma) the optimal strategy
   is public, so a model can recite it without computing. The real weak spot.
3. **Benchmark leakage** — once instances are public, the next model generation trains on them (the
   MMLU / SWE-bench fate).

## Defenses by construction
- **Procedural / parametric generation (the decisive move).** Every case is a template with randomized
  parameters (payoffs, probabilities, labels, framings) **sampled fresh at eval time**, with the oracle
  recomputed per instance. `wrps` already does this ("parameterized family … varied-shape non-uniform
  equilibria so it can't be memorized as one fixed mixture"). Requirement: the **solution must change with the
  parameters**, so a memorized instance doesn't transfer and the only path to a good score is to solve the
  family. A regenerable test set has nothing static to have seen.
- **Hidden held-out parameter region (OOD).** Release public examples in region A for understanding; **score on
  a private held-out region B**. Even if the template leaks, scoring tests generalization, not recall.
- **Surface / label randomization.** Randomize action names, option order, numerics, wording — the game is
  invariant, the surface is fresh. (Its dual is a *probe*: if a relabel tanks the score, it was reciting.)
- **Interactive cases self-defend.** Adaptive-RPS / self-play generate the trajectory **online** — the
  opponent's moves depend on the model's, so the exact interaction never existed in training. You can't
  memorize a path you generate live.
- **Retire published-solution games as *scored* items** — or use **non-standard parametrizations** (odd deck
  sizes, non-1/18 ante:bet ratios) whose equilibria aren't published, so recall buys nothing. Keep canonical
  [Kuhn poker](kuhn-poker.html) as an illustration; score the variants.
- **Don't publish scored instances; canary + rotate.** Publish the methodology and the generator's
  *distribution*; keep the scored seed private; embed canary strings in released material; regenerate the
  scored set each round (free, since it's procedural).

## Why this is the design, not a patch
By-design generation makes **contamination-resistance and trait-measurement the same thing**: memorizing an
instance is impossible, so the only way to score is to actually have the coherence skill on a fresh instance.
It doesn't even matter if a lab trains on the *distribution* — that's not contamination, it's **acquiring the
trait being measured**, and held-out instances still verify it. Contamination is only fatal when
*memorization ≠ trait*; procedural generation removes the memorization path. This is also the payoff of the
[answer-free, adversarial, execute-don't-recall](research-design.html) scoping: there is no static answer and
the instance is minted live.

## Detect the residue you can't prevent
Report **public-region score vs held-out-region score** — a large positive delta *is* the contamination
signal — paired with perturbation sensitivity. You can't prove zero contamination, but you can make the gap
visible and small by construction.

**Cost (honest).** Full procedural generation needs a **parameterized solver**, not just a parameterized
prompt — the oracle must solve each instance. `wrps` shows it's tractable for matrix games;
[extensive-form and menu cases](games-by-solvability.html) need the generator + solver built deliberately.

**See also.** [Games by solvability](games-by-solvability.html) · [Contributing cases](contributing-cases.html) ·
[Research design](research-design.html).
