# tests/test_clause_analyzer.py
import pytest
from clause_analyzer import ClauseAnalyzer


@pytest.fixture
def analyzer_en():
    return ClauseAnalyzer("en")


@pytest.fixture
def analyzer_fr():
    return ClauseAnalyzer("fr")


# === English Tests ===

def test_simple_sentence_en(analyzer_en):
    result = analyzer_en.analyze("The cat sleeps.")
    assert result["sentence_type"] == "simple"
    assert result["independent_count"] == 1
    assert result["dependent_count"] == 0
    assert any("cat sleeps" in c["text"] for c in result["clauses"])


def test_compound_sentence_en(analyzer_en):
    result = analyzer_en.analyze("The cat sleeps, and the dog barks.")
    assert result["sentence_type"] == "compound"
    assert result["independent_count"] == 2
    assert result["dependent_count"] == 0


def test_complex_sentence_en(analyzer_en):
    result = analyzer_en.analyze("The cat sleeps because it is tired.")
    assert result["sentence_type"] == "complex"
    assert result["independent_count"] == 1
    assert result["dependent_count"] == 1


def test_compound_complex_en(analyzer_en):
    result = analyzer_en.analyze("The cat sleeps when it rains, but the dog barks if it thunders.")
    assert result["sentence_type"] == "compound-complex"
    assert result["independent_count"] == 2
    assert result["dependent_count"] >= 1


# === French Tests ===

def test_simple_sentence_fr(analyzer_fr):
    result = analyzer_fr.analyze("Le chat dort.")
    assert result["sentence_type"] == "simple"
    assert result["independent_count"] == 1


def test_compound_sentence_fr(analyzer_fr):
    result = analyzer_fr.analyze("Le chat dort et le chien aboie.")
    assert result["sentence_type"] == "compound"
    assert result["independent_count"] == 2


def test_complex_sentence_fr(analyzer_fr):
    result = analyzer_fr.analyze("Le chat dort parce qu'il est fatigué.")
    assert result["sentence_type"] == "complex"
    assert result["independent_count"] == 1
    assert result["dependent_count"] == 1


def test_compound_complex_fr(analyzer_fr):
    result = analyzer_fr.analyze("Le chat dort quand il pleut, mais le chien aboie s'il tonne.")
    assert result["sentence_type"] == "compound-complex"
    assert result["independent_count"] == 2
    assert result["dependent_count"] >= 1


# === Edge Cases ===

def test_empty_string(analyzer_en):
    result = analyzer_en.analyze("")
    assert result["clauses"] == []
    assert result["sentence_type"] == "other"


def test_no_verb(analyzer_en):
    result = analyzer_en.analyze("Beautiful morning.")
    assert result["sentence_type"] == "other"