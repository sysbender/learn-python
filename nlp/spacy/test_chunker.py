import pytest
from chunker import SemanticChunker

@pytest.fixture
def chunker():
    return SemanticChunker(lang="fr")  # Use French by default for these tests

# -----------------------------
# English tests
# -----------------------------
def test_basic_chunking_english():
    chunker_en = SemanticChunker(lang="en")
    text = "Although the project faced several challenges, the team delivered the final product on time."
    result = chunker_en.chunk_sentence(text)
    assert "//" in result
    assert "challenges," in result.split("//")[0]
    chunks = [chunk.strip() for chunk in result.split("//")]
    for chunk in chunks:
        assert len(chunk.split()) >= 3

def test_short_sentence_english():
    chunker_en = SemanticChunker(lang="en")
    text = "Hello world."
    result = chunker_en.chunk_sentence(text)
    assert result == "Hello world."

# -----------------------------
# French tests
# -----------------------------
def test_basic_chunking_french():
    text = "Bien que le projet ait rencontré plusieurs défis, l'équipe a livré le produit final à temps."
    result = chunker.chunk_sentence(text)
    assert "//" in result
    assert "défis," in result.split("//")[0]
    chunks = [chunk.strip() for chunk in result.split("//")]
    for chunk in chunks:
        assert len(chunk.split()) >= 3

# Each French example as a separate test
def test_french_sentence_1():
    chunker = SemanticChunker(lang="fr")
    sentence = "Louise demande à son colocataire si elle peut avoir un temps devant la télévision un peu plus tard dans la journée."
    expected = "Louise demande à son colocataire // si elle peut avoir un temps devant la télévision // un peu plus tard dans la journée."
    result = chunker.chunk_sentence(sentence)
    assert result == expected

def test_french_sentence_2():
    chunker = SemanticChunker(lang="fr")
    sentence = "Je regardais souvent avec mes parents quand j'étais plus petite."
    expected = "Je regardais souvent avec mes parents // quand j'étais plus petite."
    result = chunker.chunk_sentence(sentence)
    assert result == expected

def test_french_sentence_3():
    chunker = SemanticChunker(lang="fr")
    sentence = "Il y a un gros match de rugby que je vais absolument regarder."
    expected = "Il y a un gros match de rugby // que je vais absolument regarder."
    result = chunker.chunk_sentence(sentence)
    assert result == expected

def test_french_sentence_4():
    chunker = SemanticChunker(lang="fr")
    sentence = "imprévisible avec plein de retournements de situation et il semble intéressé par l'ambiance de ce sport et a très envie de le découvrir."
    expected = "imprévisible avec plein de retournements de situation // et il semble intéressé par l'ambiance de ce sport // et a très envie de le découvrir."
    result = chunker.chunk_sentence(sentence)
    assert result == expected

def test_french_sentence_5():
    chunker = SemanticChunker(lang="fr")
    sentence = "ce qui montre qu'il ne connaît pas et ne comprend pas bien encore ce sport."
    expected = "ce qui montre qu'il ne connaît pas // et ne comprend pas bien encore ce sport."
    result = chunker.chunk_sentence(sentence)
    assert result == expected

def test_french_sentence_6():
    chunker = SemanticChunker(lang="fr")
    sentence = "Julien va leur conclure en disant Julien n'a évidemment aucun problème sur le fait que Louise puisse regarder à la télévision le match de rugby et lui propose même,"
    expected = "Julien va leur conclure en disant Julien n'a évidemment aucun problème // sur le fait que Louise puisse regarder à la télévision le match de rugby // et lui propose même,"
    result = chunker.chunk_sentence(sentence)
    assert result == expected

def test_french_sentence_7():
    chunker = SemanticChunker(lang="fr")
    sentence = "Il y a donc une forme de nostalgie chez elle et un côté agréable à pouvoir profiter d'un match à la télévision ou dans un stade."
    expected = "Il y a donc une forme de nostalgie chez elle // et un côté agréable à pouvoir profiter d'un match à la télévision // ou dans un stade."
    result = chunker.chunk_sentence(sentence)
    assert result == expected

def test_french_sentence_8():
    chunker = SemanticChunker(lang="fr")
    sentence = "C'est bel et bien la première fois qu'ils abordent le sujet de son amour pour le rugby."
    expected = "C'est bel et bien la première fois // qu'ils abordent le sujet de son amour pour le rugby."
    result = chunker.chunk_sentence(sentence)
    assert result == expected

def test_french_sentence_9():
    chunker = SemanticChunker(lang="fr")
    sentence = "et savoir s'il s'agit d'un nouvel aspect de ses goûts ou s'il y a quelque chose de plus ancien dont elle ne lui avait jamais parlé jusqu'à présent."
    expected = "et savoir s'il s'agit d'un nouvel aspect de ses goûts // ou s'il y a quelque chose de plus ancien // dont elle ne lui avait jamais parlé jusqu'à présent."
    result = chunker.chunk_sentence(sentence)
    assert result == expected
