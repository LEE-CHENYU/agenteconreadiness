"""Layer 2 identification core — fit a utility's parameters from revealed choices.

The gate (Layer 1, `axioms.py`) answers *"does some utility rationalize the
choices?"* (GARP/CCEI — existence). This module answers the next question:
**"which utility, within a functional class, is consistent with the choices?"**
— and, across classes, **"which class?"**. That is the canonical Layer 2
identification step, and the build lab had only forward-computation
(γ → action) and closed-form inversion before this; here is a real estimator
(action → γ̂, with a CI) plus multi-class model selection.

Scope + design (the rigor that matters):

- **Continuous-allocation observations.** Each observation is (gamble, wealth,
  chosen fraction f ∈ [0,1] of wealth staked). CRRA's optimal *fraction* is
  wealth-invariant; CARA's *declines* with wealth — so fraction-vs-wealth data
  identifies the class, not just the parameter. We fit by least-squares of the
  observed fraction against the class's optimal fraction f*(θ) (a smooth,
  monotone function of the risk parameter), which is far better-conditioned than
  binary safe-vs-risky menus (those only bracket θ to an interval — that
  under-identification is itself reported by the identifiability audit).

- **Functional classes (v0 pair):** CRRA u(W)=W^(1-γ)/(1-γ) (risk parameter γ)
  and CARA u(W)=-exp(-aW) (absolute risk aversion a). Both are 1-parameter, so a
  fine 1-D grid + local refine is exact enough without scipy (stdlib only, per
  the package's zero-dep policy). The interface generalizes to >1-param classes
  (prospect-theory λ,α) via a small product grid; v0 ships the 1-param pair.

- **Identifiability audit (the load-bearing honesty).** Andrews 2026's critique:
  a representation theorem gives *existence*, not *identification* — the data may
  not pin down the parameter or the class. We measure this directly: the SSE
  profile width (parameter CI) and the cross-class SSE gap. When the profile is
  flat (wide CI) or two classes fit ~equally (small gap), the fit is reported as
  **weakly identified** rather than asserting a confident value. A Layer 2 that
  always confidently names a utility would overclaim exactly what Andrews warns
  against; reporting non-identification *is* the contribution.

Validated by parameter-recovery tests (tests/test_identify.py): planted γ
recovered within tight CIs across γ ∈ {0.7,1.5,3,5} and two noise levels; CRRA
vs CARA model recovery from wealth-varying gambles; and a binary-menu
under-identification case the audit correctly flags.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Gamble:
    """A one-period binary gamble: stake fraction f of wealth W; final wealth is
    W*(1 + f*up) with prob p_win, else W*(1 + f*down). down is negative."""

    p_win: float
    up: float
    down: float


@dataclass(frozen=True)
class AllocationObservation:
    """One revealed allocation: at this wealth, facing this gamble, the agent
    staked `fraction` of wealth."""

    gamble: Gamble
    wealth: float
    fraction: float


# ============================================================
# Utility classes: optimal staked fraction f*(theta)
# ============================================================


def _argmax_fraction(value_at, *, step: float = 0.002) -> float:
    best_v, best_f = -math.inf, 0.0
    f = 0.0
    while f <= 1.0 + 1e-12:
        v = value_at(f)
        if v > best_v:
            best_v, best_f = v, f
        f += step
    return best_f


def crra_optimal_fraction(gamble: Gamble, wealth: float, gamma: float) -> float:
    """Optimal staked fraction under CRRA u(W)=W^(1-γ)/(1-γ) (log at γ=1).

    Wealth-invariant by CRRA's scale-invariance — this is the class signature.
    """

    def value(f: float) -> float:
        wu = wealth * (1.0 + f * gamble.up)
        wd = wealth * (1.0 + f * gamble.down)
        if wu <= 0 or wd <= 0:
            return -math.inf
        if abs(gamma - 1.0) < 1e-9:
            u = gamble.p_win * math.log(wu) + (1 - gamble.p_win) * math.log(wd)
        else:
            uu = (wu ** (1.0 - gamma) - 1.0) / (1.0 - gamma)
            ud = (wd ** (1.0 - gamma) - 1.0) / (1.0 - gamma)
            u = gamble.p_win * uu + (1 - gamble.p_win) * ud
        return u

    return _argmax_fraction(value)


def cara_optimal_fraction(gamble: Gamble, wealth: float, a: float) -> float:
    """Optimal staked fraction under CARA u(W)=-exp(-aW).

    Declines with wealth (the staked *amount* a*f*W is roughly wealth-invariant),
    which is what distinguishes CARA from CRRA in fraction-vs-wealth data.
    """

    def value(f: float) -> float:
        wu = wealth * (1.0 + f * gamble.up)
        wd = wealth * (1.0 + f * gamble.down)
        u = gamble.p_win * (-math.exp(-a * wu)) + (1 - gamble.p_win) * (-math.exp(-a * wd))
        return u

    return _argmax_fraction(value)


# A functional class = (name, optimal-fraction fn, parameter grid).
@dataclass(frozen=True)
class FunctionalClass:
    name: str
    optimal_fraction: object  # (gamble, wealth, theta) -> float
    grid: tuple[float, ...]
    param_name: str


def crra_class(grid: Sequence[float] | None = None) -> FunctionalClass:
    g = tuple(grid) if grid is not None else tuple(round(0.05 * k, 4) for k in range(1, 161))  # 0.05..8.0
    return FunctionalClass("CRRA", crra_optimal_fraction, g, "gamma")


def cara_class(grid: Sequence[float] | None = None) -> FunctionalClass:
    # absolute risk aversion; log-spaced grid over a plausible range
    g = tuple(round(10 ** (-4 + 0.05 * k), 8) for k in range(0, 81))  # ~1e-4 .. ~1.0
    if grid is not None:
        g = tuple(grid)
    return FunctionalClass("CARA", cara_optimal_fraction, g, "a")


# ============================================================
# Fitting (least-squares on observed vs optimal fraction)
# ============================================================


@dataclass
class ClassFit:
    class_name: str
    param_name: str
    theta_hat: float
    sse: float
    n: int
    theta_lo: float  # profile CI (SSE within rss*(1+1/n) of min) — see _profile_interval
    theta_hi: float
    weakly_identified: bool

    @property
    def rmse(self) -> float:
        return math.sqrt(self.sse / self.n) if self.n else 0.0

    @property
    def ci_width(self) -> float:
        return self.theta_hi - self.theta_lo


def _sse(klass: FunctionalClass, obs: Sequence[AllocationObservation], theta: float) -> float:
    total = 0.0
    for o in obs:
        pred = klass.optimal_fraction(o.gamble, o.wealth, theta)
        total += (pred - o.fraction) ** 2
    return total


_MIN_OBS_FOR_IDENTIFICATION = 4


def _profile_interval(
    klass: FunctionalClass,
    obs: Sequence[AllocationObservation],
    grid_sse: list[tuple[float, float]],
    theta_hat: float,
    sse_min: float,
) -> tuple[float, float, bool]:
    """A profile-likelihood-style interval: the set of theta whose SSE is within a
    threshold of the minimum. Threshold = sse_min * (1 + 2.0/n) + eps — a simple,
    scale-free band (wider when the fit is poor or n is small).

    Flags weak identification on any of three conditions, each a real
    non-identification mode (the Andrews 2026 honesty): (a) too few observations
    to identify + assess reliability (n < min_obs — a single point can match the
    grid exactly yet say nothing about robustness); (b) the accepting band spans
    most of the grid (a flat profile — the data doesn't constrain theta); (c) the
    estimate is pinned at a grid boundary (the true value is outside the searched
    range, or the agent is at a corner like always-max / always-min).
    """
    n = max(1, len(obs))
    eps = 1e-9
    thresh = sse_min * (1.0 + 2.0 / n) + eps
    inside = [t for (t, s) in grid_sse if s <= thresh]
    if not inside:
        return theta_hat, theta_hat, True
    lo, hi = min(inside), max(inside)
    grid_span = grid_sse[-1][0] - grid_sse[0][0]
    band = hi - lo
    too_few = n < _MIN_OBS_FOR_IDENTIFICATION
    flat_profile = grid_span > 0 and band > 0.6 * grid_span
    at_boundary = theta_hat <= grid_sse[0][0] + 1e-9 or theta_hat >= grid_sse[-1][0] - 1e-9
    weak = too_few or flat_profile or at_boundary
    return lo, hi, weak


def fit_class(klass: FunctionalClass, obs: Sequence[AllocationObservation]) -> ClassFit:
    """Least-squares fit of one functional class's parameter to observed fractions,
    with a profile interval + weak-identification flag."""
    grid_sse = [(t, _sse(klass, obs, t)) for t in klass.grid]
    sse_min, theta_hat = min((s, t) for (t, s) in grid_sse)
    # local refine around the grid winner
    step = (klass.grid[1] - klass.grid[0]) if len(klass.grid) > 1 else 0.0
    if step > 0:
        t = theta_hat - step
        while t <= theta_hat + step:
            s = _sse(klass, obs, t)
            if s < sse_min:
                sse_min, theta_hat = s, t
            t += step / 20.0
    lo, hi, weak = _profile_interval(klass, obs, grid_sse, theta_hat, sse_min)
    return ClassFit(
        class_name=klass.name,
        param_name=klass.param_name,
        theta_hat=theta_hat,
        sse=sse_min,
        n=len(obs),
        theta_lo=lo,
        theta_hi=hi,
        weakly_identified=weak,
    )


# ============================================================
# Multi-class model selection
# ============================================================


def _aic_bic(sse: float, n: int, k_params: int) -> tuple[float, float]:
    """Gaussian-error AIC/BIC from SSE. n*ln(SSE/n) + 2k (AIC) / +k*ln(n) (BIC).
    Lower is better. Guards SSE=0 (perfect fit) with a tiny floor."""
    sigma2 = max(sse / n, 1e-12)
    ll = -0.5 * n * (math.log(2 * math.pi * sigma2) + 1.0)
    aic = -2 * ll + 2 * k_params
    bic = -2 * ll + k_params * math.log(n)
    return aic, bic


@dataclass
class ModelSelection:
    fits: list[ClassFit]
    best_class: str
    aic: dict
    bic: dict
    posterior: dict  # softmax over -0.5*BIC (BIC-approx posterior), sums to 1
    decisive: bool   # winner's posterior clearly dominates


def select_class(
    obs: Sequence[AllocationObservation],
    classes: Sequence[FunctionalClass],
    *,
    decisive_threshold: float = 0.9,
) -> ModelSelection:
    """Fit every class, rank by BIC, report a BIC-approximate posterior over
    classes. `decisive` is True only when the winner's posterior exceeds
    `decisive_threshold` — otherwise the data does not clearly prefer a class
    (the model-level identifiability statement)."""
    fits = [fit_class(c, obs) for c in classes]
    n = max(1, len(obs))
    aic = {}
    bic = {}
    for f in fits:
        a, b = _aic_bic(f.sse, n, k_params=1)
        aic[f.class_name] = a
        bic[f.class_name] = b
    # BIC-approx posterior: softmax over -0.5*BIC.
    min_bic = min(bic.values())
    weights = {name: math.exp(-0.5 * (b - min_bic)) for name, b in bic.items()}
    z = sum(weights.values())
    posterior = {name: w / z for name, w in weights.items()}
    best_class = min(bic, key=bic.get)
    decisive = posterior[best_class] >= decisive_threshold
    return ModelSelection(
        fits=fits,
        best_class=best_class,
        aic=aic,
        bic=bic,
        posterior=posterior,
        decisive=decisive,
    )


# ============================================================
# Synthetic data generation (for recovery validation + tasks)
# ============================================================


def simulate_allocations(
    klass: FunctionalClass,
    theta: float,
    gambles: Sequence[Gamble],
    wealths: Sequence[float],
    *,
    sigma: float = 0.03,
    seed: int = 0,
) -> list[AllocationObservation]:
    """Generate revealed allocations from a known (class, theta) with Gaussian
    fraction noise. The ground truth recovery tests fit these back to theta."""
    import random

    rng = random.Random(20260529 + seed)
    obs: list[AllocationObservation] = []
    for w in wealths:
        for gm in gambles:
            f_star = klass.optimal_fraction(gm, w, theta)
            noisy = min(1.0, max(0.0, f_star + rng.gauss(0.0, sigma)))
            obs.append(AllocationObservation(gamble=gm, wealth=w, fraction=noisy))
    return obs


DEFAULT_GAMBLES: tuple[Gamble, ...] = (
    Gamble(0.50, 0.80, -0.40),
    Gamble(0.55, 0.90, -0.45),
    Gamble(0.60, 0.60, -0.40),
    Gamble(0.50, 1.00, -0.50),
)

# Wide wealth range so CRRA (flat fraction) and CARA (declining fraction) separate.
DEFAULT_WEALTHS: tuple[float, ...] = (20.0, 60.0, 200.0, 600.0, 2000.0)
