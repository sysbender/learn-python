import pytest
import spacy
from typing import Dict, List, Tuple
from nlp_utils import load_nlp_model, ClauseDetector, SentenceClassifier

# Fixtures to load and reuse spaCy models for testing
@pytest.fixture(scope="session")
def en_nlp():
    """Fixture for English spaCy model."""
    return load_nlp_model("en")

@pytest.fixture(scope="session")
def fr_nlp():
    """Fixture for French spaCy model."""
    return load_nlp_model("fr")

@pytest.fixture(scope="session")
def en_detector(en_nlp):
    """Fixture for English ClauseDetector."""
    return ClauseDetector(en_nlp)

@pytest.fixture(scope="session")
def fr_detector(fr_nlp):
    """Fixture for French ClauseDetector."""
    return ClauseDetector(fr_nlp)

@pytest.fixture(scope="session")
def en_classifier(en_detector):
    """Fixture for English SentenceClassifier."""
    return SentenceClassifier(en_detector)

@pytest.fixture(scope="session")
def fr_classifier(fr_detector):
    """Fixture for French SentenceClassifier."""
    return SentenceClassifier(fr_detector)


# --- ClauseDetector Tests (Verification of Clause Counts/Extraction) ---

def test_clause_detector_simple_en(en_detector):
    text = "The dog barks loudly."
    ics, dcs = en_detector.detect(en_detector.nlp(text))
    assert len(ics) == 1
    assert len(dcs) == 0
    assert ics[0] == "The dog barks loudly."

def test_clause_detector_compound_en(en_detector):
    text = "She sings, and he dances."
    ics, dcs = en_detector.detect(en_detector.nlp(text))
    assert len(ics) >= 2
    assert len(dcs) == 0
    # Check if both main ideas are extracted
    assert any("She sings" in c for c in ics)
    assert any("he dances" in c for c in ics)

def test_clause_detector_complex_en(en_detector):
    text = "I went home because it was raining."
    ics, dcs = en_detector.detect(en_detector.nlp(text))
    assert len(ics) == 1
    assert len(dcs) >= 1
    assert "I went home" in ics
    assert any("because it was raining" in c for c in dcs)

def test_clause_detector_compound_complex_en(en_detector):
    text = "Since the store closed, I went to the park, and I bought a coffee."
    ics, dcs = en_detector.detect(en_detector.nlp(text))
    assert len(ics) >= 2
    assert len(dcs) >= 1
    assert any("Since the store closed" in c for c in dcs)
    assert any("I went to the park" in c for c in ics)
    assert any("I bought a coffee" in c for c in ics)

def test_clause_detector_simple_fr(fr_detector):
    text = "Le soleil brille." # The sun is shining.
    ics, dcs = fr_detector.detect(fr_detector.nlp(text))
    assert len(ics) == 1
    assert len(dcs) == 0
    assert ics[0] == "Le soleil brille."

def test_clause_detector_compound_fr(fr_detector):
    text = "Elle mange et il boit." # She eats and he drinks.
    ics, dcs = fr_detector.detect(fr_detector.nlp(text))
    assert len(ics) >= 2
    assert len(dcs) == 0
    assert any("Elle mange" in c for c in ics)
    assert any("il boit" in c for c in ics)

def test_clause_detector_complex_fr(fr_detector):
    text = "J'ai lu le livre qu'elle m'a donné." # I read the book that she gave me.
    ics, dcs = fr_detector.detect(fr_detector.nlp(text))
    assert len(ics) == 1
    assert len(dcs) >= 1
    assert "J'ai lu le livre" in ics
    assert any("qu'elle m'a donné" in c for c in dcs)

def test_clause_detector_compound_complex_fr(fr_detector):
    text = "Bien qu'il soit fatigué, il a couru, et il a gagné la course." 
    # Although he is tired, he ran, and he won the race.
    ics, dcs = fr_detector.detect(fr_detector.nlp(text))
    assert len(ics) >= 2
    assert len(dcs) >= 1
    assert any("Bien qu'il soit fatigué" in c for c in dcs)
    assert any("il a couru" in c for c in ics)
    assert any("il a gagné la course" in c for c in ics)


# --- SentenceClassifier Tests (Verification of Classification) ---

# English Classification Tests
@pytest.mark.parametrize("text, expected_type", [
    ("The cat slept.", "Simple"),
    ("I ran, and she walked.", "Compound"),
    ("Because the coffee was hot, I waited.", "Complex"),
    ("She waited until I arrived, but I was late.", "Compound-Complex"),
    ("I love the city where I grew up.", "Complex"),
    ("He sings, she cooks, and they eat.", "Compound"),
])
def test_sentence_classifier_en(en_classifier, text, expected_type):
    analysis = en_classifier.classify(text)
    assert analysis['classification'] == expected_type

# French Classification Tests
@pytest.mark.parametrize("text, expected_type", [
    ("Nous travaillons bien.", "Simple"), # We work well.
    ("Il pleut, mais il fait beau.", "Compound"), # It's raining, but it's sunny.
    ("Elle partira quand il arrivera.", "Complex"), # She will leave when he arrives.
    ("Comme j'ai faim, je vais faire la cuisine, et nous mangerons bien.", "Compound-Complex"), 
    # As I am hungry, I will cook, and we will eat well.
    ("J'aime le livre que tu as écrit.", "Complex"), # I like the book that you wrote.
])
def test_sentence_classifier_fr(fr_classifier, text, expected_type):
    analysis = fr_classifier.classify(text)
    assert analysis['classification'] == expected_type

# Edge case test: Fragment
def test_sentence_classifier_fragment(en_classifier):
    # A fragment often results in 0 ICs
    analysis = en_classifier.classify("Running quickly to the store.")
    assert analysis['classification'] in ["Fragment/Other", "Simple"] # Simple is acceptable if the parser finds a hidden root

# Test for model loading error
def test_load_nlp_model_unsupported():
    with pytest.raises(ValueError):
        load_nlp_model("de") # German is not supported in MODEL_MAP