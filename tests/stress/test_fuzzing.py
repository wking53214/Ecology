import pytest
from plant import SpeculativeLanguageFilter

@pytest.mark.parametrize("obfuscated_input", [
    "PerHapsse",
    "p-e-r-h-a-p-s-e",
    "maybe",
    "m a y b e",
    "perhaps",
    "it is possible"
])
def test_speculation_filter_robustness(obfuscated_input):
    filter = SpeculativeLanguageFilter()
    assert filter.is_clean(obfuscated_input) is False, f"Failed to detect: {obfuscated_input}"
