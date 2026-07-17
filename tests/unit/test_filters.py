from plant import PersonalPronounFilter, SpeculativeLanguageFilter

def test_pronoun_filter_detection():
    filter = PersonalPronounFilter()
    assert filter.is_clean("The system functions independently.") is True
    assert filter.is_clean("I believe the system functions.") is False
    assert filter.is_clean("We analyzed the data.") is False

def test_speculation_filter_detection():
    filter = SpeculativeLanguageFilter()
    assert filter.is_clean("The metrics confirm stability.") is True
    assert filter.is_clean("Perhaps the metrics confirm stability.") is False
