"""
===============================================================================
Module
===============================================================================

Filename:
Engine_Policy_Service.py

Purpose:
Implements the deterministic policy evaluation layer for the Meta Resilience
System. This service defines engine selection policies, confidence weighting,
resource-aware execution rules, and stability controls used to determine which
analytical engines should participate during each evaluation cycle.

The Engine Policy Service provides a controlled decision boundary between
system state signals and engine orchestration. It does not execute engines,
modify engine behavior, or perform analysis itself. Instead, it evaluates
available information and produces deterministic selection outcomes.

Responsibilities:
- Define configurable policy thresholds.
- Maintain persistent policy state.
- Provide deterministic engine selection rules.
- Apply safety override conditions.
- Support compute-aware engine selection.
- Provide confidence-weighted engine prioritization.
- Enforce hysteresis and dwell constraints.
- Prevent unnecessary primary engine switching.
- Provide deterministic policy evaluation helpers.

Non-Responsibilities:
- Execute selected engines.
- Modify engine outputs.
- Perform system remediation.
- Change governance rules dynamically.
- Override external safety controls.

Design Principles:
- Deterministic evaluation.
- Explicit policy boundaries.
- Stable state transitions.
- Controlled switching behavior.
- Predictable engine orchestration.
- Separation of policy from execution.

Public Data Models:
- PolicyState
- PolicyConfig

Public Functions:
- select_engines()
- should_switch_primary()
- pick_primary_candidate()

Internal Functions:
- _ensure_available()

Dependencies:
- Python Standard Library
    - dataclasses
    - datetime
    - typing

===============================================================================
"""
meta_engine/engine_policy.py  
  
Deterministic policy evaluator for the Meta Resilience System.  
  
Responsibilities:  
- Encapsulate thresholds, base trust weights, and tunables.  
- Provide deterministic engine selection rules.  
- Provide hysteresis / dwell helpers for primary switching decisions.  
  
Drop this file into meta_engine/ and import select_engines, PolicyState, and PolicyConfig.  
"""  
  
from __future__ import annotations  
from dataclasses import dataclass  
from datetime import datetime, timedelta  
from typing import Dict, List, Optional  
  
# -------------------------  
# Data models  
# -------------------------  
@dataclass  
class PolicyState:  
    """Persistent policy state used across evaluation cycles."""  
    last_primary: Optional[str] = None  
    last_switch_time: Optional[datetime] = None  
    dwell_count: int = 0  
  
@dataclass  
class PolicyConfig:  
    """Tunable thresholds and base weights for selection and fusion."""  
    H_HIGH: float = 1.0  
    H_LOW: float = 0.4  
    E_LOW: float = 0.01  
    V_CRIT: float = 2.0  
    DETERMINISM_SAFETY: float = 0.5  
    T_DWELL_SECONDS: int = 60  
    DELTA_CONFIDENCE_TO_SWITCH: float = 0.12  
  
    BASE_WEIGHTS: Dict[str, float] = None  
  
    def __post_init__(self):  
        if self.BASE_WEIGHTS is None:  
            self.BASE_WEIGHTS = {  
                "universal": 1.5,  
                "ure": 1.0,  
                "chassis": 1.0,  
                "sentinel": 0.8,  
                "temporal": 0.6,  
                "adversarial": 1.4,  
            }  
  
# -------------------------  
# Selection logic  
# -------------------------  
def select_engines(  
    signals: Dict[str, float],  
    state: PolicyState,  
    compute_budget: float,  
    config: Optional[PolicyConfig] = None,  
    available_engines: Optional[List[str]] = None,  
    adversarial_flag: bool = False,  
) -> List[str]:  
    """  
    Deterministically select which engines to run this cycle.  
  
    Parameters  
    - signals: dict with keys 'entropy', 'determinism_index', 'velocity', 'energy' (optional)  
    - state: PolicyState (last_primary, last_switch_time, dwell_count)  
    - compute_budget: float in 0..1 representing available compute  
    - config: PolicyConfig (optional)  
    - available_engines: list of registered engine names (optional)  
    - adversarial_flag: boolean indicating external adversarial detection  
  
    Returns: ordered list of engine names (primary first where applicable)  
    """  
    cfg = config or PolicyConfig()  
    entropy = float(signals.get("entropy", 0.0))  
    determinism = float(signals.get("determinism_index", 1.0))  
    velocity = abs(float(signals.get("velocity", 0.0)))  
    energy = float(signals.get("energy", 0.0))  
    last = state.last_primary  
  
    # Safety override: low determinism or explicit adversarial flag  
    if determinism < cfg.DETERMINISM_SAFETY or adversarial_flag:  
        return _ensure_available(["universal", "sentinel"], available_engines)  
  
    # High entropy escalation: run heavy + light for cross-validation  
    if entropy > cfg.H_HIGH:  
        return _ensure_available(["universal", "ure"], available_engines)  
  
    # Compute constrained: prefer lightweight engine only  
    if compute_budget < 0.2:  
        return _ensure_available(["ure"], available_engines)  
  
    # Velocity trigger: rapid drift requires nonlinear analysis  
    if velocity > cfg.V_CRIT:  
        return _ensure_available(["universal"], available_engines)  
  
    # Stable fast path: keep using URE if already primary and signals are calm  
    if entropy < cfg.H_LOW and energy < cfg.E_LOW and last == "ure":  
        return _ensure_available(["ure"], available_engines)  
  
    # Default: prefer chassis + ure if available, else fall back to any two engines  
    preferred = _ensure_available(["chassis", "ure"], available_engines)  
    if preferred:  
        return preferred  
  
    # Fallback: return up to two available engines  
    if available_engines:  
        return available_engines[:2]  
    return []  
  
def _ensure_available(desired: List[str], available: Optional[List[str]]) -> List[str]:  
    """  
    Helper: return the intersection of desired and available preserving order.  
    If available is None, return desired as-is.  
    """  
    if available is None:  
        return desired.copy()  
    out = [d for d in desired if d in available]  
    return out  
  
# -------------------------  
# Hysteresis / switching helper  
# -------------------------  
def should_switch_primary(  
    candidate: str,  
    candidate_confidence: float,  
    current_confidence: float,  
    state: PolicyState,  
    config: Optional[PolicyConfig] = None,  
) -> bool:  
    """  
    Decide whether to switch the primary engine to 'candidate' based on dwell time  
    and confidence delta.  
  
    Returns True if switch should occur.  
    """  
    cfg = config or PolicyConfig()  
    now = datetime.utcnow()  
  
    # Respect minimum dwell time  
    if state.last_switch_time:  
        elapsed = (now - state.last_switch_time).total_seconds()  
        if elapsed < cfg.T_DWELL_SECONDS:  
            return False  
  
    # No-op if candidate is already primary  
    if candidate == state.last_primary:  
        return False  
  
    # Require a meaningful confidence improvement to switch  
    if (candidate_confidence - current_confidence) >= cfg.DELTA_CONFIDENCE_TO_SWITCH:  
        return True  
  
    return False  
  
# -------------------------  
# Utility: compute trust-ordered primary candidate  
# -------------------------  
def pick_primary_candidate(outputs: List[Dict], config: Optional[PolicyConfig] = None) -> Optional[tuple]:  
    """  
    Given a list of engine outputs (dicts with keys: engine_name, confidence),  
    return (engine_name, weighted_score) for the top candidate, or None.  
    Weighted score = confidence * base_weight.  
    """  
    cfg = config or PolicyConfig()  
    best = None  
    best_score = 0.0  
    for out in outputs:  
        name = out.get("engine_name")  
        conf = float(out.get("confidence", 0.0))  
        weight = cfg.BASE_WEIGHTS.get(name, 1.0)  
        score = conf * weight  
        if score > best_score:  
            best_score = score  
            best = name  
    if best is None:  
        return None  
    return best, best_score  