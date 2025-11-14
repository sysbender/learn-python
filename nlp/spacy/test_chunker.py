import pytest
from chunker import SemanticChunker

@pytest.fixture
def chunker():
    # Initialize the chunker without any unsupported parameters
    return SemanticChunker()

def test_basic_chunking_english(chunker):
    text = "Although the project faced several challenges, the team delivered the final product on time."
    result = chunker.chunk_sentence(text)
    
    # Ensure there is at least one split
    assert "//" in result
    
    # Ensure comma stays in the first chunk
    assert "challenges," in result.split("//")[0]
    
    # Ensure no chunk is shorter than 3 words
    chunks = [chunk.strip() for chunk in result.split("//")]
    for chunk in chunks:
        assert len(chunk.split()) >= 3

def test_basic_chunking_french(chunker):
    text = "Bien que le projet ait rencontré plusieurs défis, l'équipe a livré le produit final à temps."
    result = chunker.chunk_sentence(text)
    
    # Ensure there is at least one split
    assert "//" in result
    
    # Ensure comma stays in the first chunk
    assert "défis," in result.split("//")[0]
    
    # Ensure no chunk is shorter than 3 words
    chunks = [chunk.strip() for chunk in result.split("//")]
    for chunk in chunks:
        assert len(chunk.split()) >= 3

def test_short_sentence(chunker):
    text = "Hello world."
    result = chunker.chunk_sentence(text)
    
    # Short sentence should not be split
    assert result == "Hello world."

def test_long_paragraph_multilingual(chunker):
    # English long paragraph
    text_en = (
        "Although the team encountered several unexpected issues during the project, "
        "they managed to deliver the software on time, and the client was satisfied with the outcome."
    )
    result_en = chunker.chunk_sentence(text_en)
    chunks_en = [chunk.strip() for chunk in result_en.split("//")]
    
    # French long paragraph
    text_fr = (
        "Bien que l'équipe ait rencontré plusieurs problèmes inattendus pendant le projet, "
        "elle a réussi à livrer le logiciel à temps, et le client était satisfait du résultat."
    )
    result_fr = chunker.chunk_sentence(text_fr)
    chunks_fr = [chunk.strip() for chunk in result_fr.split("//")]
    
    # Check splits exist
    assert "//" in result_en
    assert "//" in result_fr
    
    # Check no chunk is shorter than 3 words
    for chunk in chunks_en + chunks_fr:
        assert len(chunk.split()) >= 3


def test_french_sentences_exact_chunks(chunker):
    # Each sentence with its expected chunked result
    examples = [
        (
            "Louise demande à son colocataire si elle peut avoir un temps devant la télévision un peu plus tard dans la journée.",
            "Louise demande à son colocataire // si elle peut avoir un temps devant la télévision // un peu plus tard dans la journée."
        ),
        (
            "Je regardais souvent avec mes parents quand j'étais plus petite.",
            "Je regardais souvent avec mes parents // quand j'étais plus petite."
        ),
        (
            "Il y a un gros match de rugby que je vais absolument regarder.",
            "Il y a un gros match de rugby // que je vais absolument regarder."
        ),
        (
            "imprévisible avec plein de retournements de situation et il semble intéressé par l'ambiance de ce sport et a très envie de le découvrir.",
            "imprévisible avec plein de retournements de situation // et il semble intéressé par l'ambiance de ce sport // et a très envie de le découvrir."
        ),
        (
            "ce qui montre qu'il ne connaît pas et ne comprend pas bien encore ce sport.",
            "ce qui montre qu'il ne connaît pas // et ne comprend pas bien encore ce sport."
        ),
        (
            "Julien va leur conclure en disant Julien n'a évidemment aucun problème sur le fait que Louise puisse regarder à la télévision le match de rugby et lui propose même,",
            "Julien va leur conclure en disant Julien n'a évidemment aucun problème // sur le fait que Louise puisse regarder à la télévision le match de rugby // et lui propose même,"
        ),
        (
            "Il y a donc une forme de nostalgie chez elle et un côté agréable à pouvoir profiter d'un match à la télévision ou dans un stade.",
            "Il y a donc une forme de nostalgie chez elle // et un côté agréable à pouvoir profiter d'un match à la télévision // ou dans un stade."
        ),
        (
            "C'est bel et bien la première fois qu'ils abordent le sujet de son amour pour le rugby.",
            "C'est bel et bien la première fois // qu'ils abordent le sujet de son amour pour le rugby."
        ),
        (
            "et savoir s'il s'agit d'un nouvel aspect de ses goûts ou s'il y a quelque chose de plus ancien dont elle ne lui avait jamais parlé jusqu'à présent.",
            "et savoir s'il s'agit d'un nouvel aspect de ses goûts // ou s'il y a quelque chose de plus ancien // dont elle ne lui avait jamais parlé jusqu'à présent."
        )
    ]
    
    for sentence, expected in examples:
        result = chunker.chunk_sentence(sentence)
        assert result == expected, f"Sentence failed: {sentence}\nExpected: {expected}\nGot: {result}"