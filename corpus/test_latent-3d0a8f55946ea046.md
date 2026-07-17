"""
test_latent.py
--------------

Core determinism + behavior tests for Iceberg's LatentPayload model.

These tests guarantee:
- Stable defaults
- Deterministic updates
- JSON-safe snapshots
- Structural-hash stability
- Monotonic emotional drift rules
- Replay-friendly latent evolution

This is the lighter-weight companion to test_latent_regression.py.
"""

# ---------------------------------------------------------
# TEST 1 — Defaults are stable
# ---------------------------------------------------------
def test_defaults_stable():
    lp1 = LatentPayload()
    lp2 = LatentPayload()

# ---------------------------------------------------------
# TEST 2 — JSON-safe snapshot
# ---------------------------------------------------------
def test_json_safe_snapshot():
    lp = LatentPayload()
    snap = lp.to_dict()

# ---------------------------------------------------------
# TEST 3 — Structural hash stable for identical snapshot
# ---------------------------------------------------------
def test_structural_hash_stable():
    lp = LatentPayload()
    snap = lp.to_dict()

# ---------------------------------------------------------
# Dummy caller dynamic for updates
# ---------------------------------------------------------
class DummyCallerDynamic:
    def __init__(self, frustration: float = 0.0):
        self.frustration = frustration

# ---------------------------------------------------------
# TEST 4 — Single-step update deterministic
# ---------------------------------------------------------
def test_single_step_deterministic():
    lp1 = LatentPayload()
    lp2 = LatentPayload()

cd1 = DummyCallerDynamic(frustration=0.1)
    cd2 = DummyCallerDynamic(frustration=0.1)

lp1.update_after_step(cd1)
    lp2.update_after_step(cd2)

assert lp1.to_dict() == lp2.to_dict(), "Single-step latent update drift detected"

# ---------------------------------------------------------
# TEST 5 — Multi-step update deterministic
# ---------------------------------------------------------
def test_multistep_deterministic():
    lp1 = LatentPayload()
    lp2 = LatentPayload()

for _ in range(5):
        lp1.update_after_step(cd1)
        lp2.update_after_step(cd2)

assert lp1.to_dict() == lp2.to_dict(), "Multi-step latent update drift detected"

# ---------------------------------------------------------
# TEST 6 — Monotonic emotional drift
# ---------------------------------------------------------
def test_monotonic_emotional_drift():
    lp = LatentPayload()
    cd = DummyCallerDynamic(frustration=0.2)

# Trust should not increase
    assert after["trust_scalar"] <= before["trust_scalar"], "trust_scalar should not increase"

# Volatility should not decrease
    assert after["volatility"] >= before["volatility"], "volatility should not decrease"

# Memory flag should not decrease
    assert after["memory_flag"] >= before["memory_flag"], "memory_flag should not decrease"

# ---------------------------------------------------------
# TEST 7 — Structural hash changes after update
# ---------------------------------------------------------
def test_hash_changes_after_update():
    lp = LatentPayload()
    cd = DummyCallerDynamic(frustration=0.2)

# ---------------------------------------------------------
# TEST 8 — Multi-step snapshot remains JSON-safe
# ---------------------------------------------------------
def test_multistep_json_safe():
    lp = LatentPayload()
    cd = DummyCallerDynamic(frustration=0.2)

try:
        json.dumps(lp.to_dict())
    except Exception as e:
        pytest.fail(f"LatentPayload after multi-step updates is not JSON-safe: {e}")
