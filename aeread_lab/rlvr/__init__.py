"""RLVR training-demo utilities built beside, not inside, benchmark tasks."""

__all__ = [
    "SupplierScamTrajectoryEnv",
    "TrajectoryAction",
    "run_scripted_baselines",
    "run_scripted_policy",
]


def __getattr__(name: str):
    if name not in __all__:
        raise AttributeError(name)
    from aeread_lab.rlvr import supplier_scam_trajectory

    return getattr(supplier_scam_trajectory, name)
