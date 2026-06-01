"""Pure-math methodology instruments (no LLM, no I/O) — the auditable cores.

- axioms.py   : Layer 1 (coherence) revealed-preference axioms (WARP/GARP/CCEI)
- identify.py : Layer 2 (identification) utility fitting + model selection

Note: stats.py (CIs) stays at package top level (27 importers); it is shared
infra rather than a layer-specific instrument.
"""
