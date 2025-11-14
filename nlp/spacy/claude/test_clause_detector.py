"""
Unit tests for clause detection and sentence classification.

Run with: pytest test_clause_detector.py -v
"""

import pytest
from clause_detector import (
    ClauseDetector,
    SentenceClassifier,
    Clause,
    ClauseType,
    SentenceType,
    detect_clauses,
    classify_sentence
)


class TestClauseDetectorEnglish:
    """Tests for English clause detection."""
    
    @pytest.fixture
    def detector(self):
        """Create a ClauseDetector instance for English."""
        return ClauseDetector(language="en")
    
    @pytest.fixture
    def classifier(self, detector):
        """Create a SentenceClassifier instance."""
        return SentenceClassifier(detector)
    
    def test_simple_sentence(self, detector):
        """Test detection in a simple sentence."""
        text = "The cat sleeps."
        clauses = detector.detect_clauses(text)
        
        assert len(clauses) >= 1
        assert any(c.clause_type == ClauseType.INDEPENDENT for c in clauses)
    
    def test_compound_sentence(self, detector):
        """Test detection in a compound sentence."""
        text = "I went to the store, and she went home."
        clauses = detector.detect_clauses(text)
        
        independent_clauses = [c for c in clauses if c.clause_type == ClauseType.INDEPENDENT]
        assert len(independent_clauses) >= 2
    
    def test_complex_sentence(self, detector):
        """Test detection in a complex sentence."""
        text = "Although it was raining, we went outside."
        clauses = detector.detect_clauses(text)
        
        independent = [c for c in clauses if c.clause_type == ClauseType.INDEPENDENT]
        dependent = [c for c in clauses if c.clause_type == ClauseType.DEPENDENT]
        
        assert len(independent) >= 1
        assert len(dependent) >= 1
    
    def test_compound_complex_sentence(self, detector):
        """Test detection in a compound-complex sentence."""
        text = "When I arrived, she was cooking, and he was reading."
        clauses = detector.detect_clauses(text)
        
        independent = [c for c in clauses if c.clause_type == ClauseType.INDEPENDENT]
        dependent = [c for c in clauses if c.clause_type == ClauseType.DEPENDENT]
        
        assert len(independent) >= 2
        assert len(dependent) >= 1
    
    def test_clause_text_extraction(self, detector):
        """Test that clause text is properly extracted."""
        text = "I know that she is happy."
        clauses = detector.detect_clauses(text)
        
        assert len(clauses) >= 1
        for clause in clauses:
            assert clause.text.strip() != ""
            assert isinstance(clause.text, str)
    
    def test_clause_boundaries(self, detector):
        """Test that clause boundaries are properly set."""
        text = "The dog barks loudly."
        clauses = detector.detect_clauses(text)
        
        for clause in clauses:
            assert clause.start >= 0
            assert clause.end > clause.start
            assert clause.root_token is not None
    
    def test_relative_clause(self, detector):
        """Test detection of relative clauses."""
        text = "The book that I read was interesting."
        clauses = detector.detect_clauses(text)
        
        # Should detect main clause and relative clause
        assert len(clauses) >= 1
    
    def test_subordinate_conjunction(self, detector):
        """Test detection with various subordinate conjunctions."""
        test_cases = [
            "Because it was late, we left.",
            "If you come, I will be happy.",
            "While she was sleeping, the phone rang.",
            "Since you asked, I will tell you."
        ]
        
        for text in test_cases:
            clauses = detector.detect_clauses(text)
            dependent = [c for c in clauses if c.clause_type == ClauseType.DEPENDENT]
            assert len(dependent) >= 1, f"Failed to detect dependent clause in: {text}"
    
    def test_empty_text(self, detector):
        """Test handling of empty text."""
        clauses = detector.detect_clauses("")
        assert clauses == []
    
    def test_no_verb_sentence(self, detector):
        """Test handling of sentences without verbs."""
        text = "A beautiful day."
        clauses = detector.detect_clauses(text)
        # Should handle gracefully, even if no clauses detected
        assert isinstance(clauses, list)


class TestClauseDetectorFrench:
    """Tests for French clause detection."""
    
    @pytest.fixture
    def detector(self):
        """Create a ClauseDetector instance for French."""
        try:
            return ClauseDetector(language="fr")
        except OSError:
            pytest.skip("French model not installed")
    
    def test_simple_sentence_french(self, detector):
        """Test detection in a simple French sentence."""
        text = "Le chat dort."
        clauses = detector.detect_clauses(text)
        
        assert len(clauses) >= 1
        assert any(c.clause_type == ClauseType.INDEPENDENT for c in clauses)
    
    def test_compound_sentence_french(self, detector):
        """Test detection in a compound French sentence."""
        text = "Je suis allé au magasin et elle est rentrée."
        clauses = detector.detect_clauses(text)
        
        independent_clauses = [c for c in clauses if c.clause_type == ClauseType.INDEPENDENT]
        assert len(independent_clauses) >= 1
    
    def test_complex_sentence_french(self, detector):
        """Test detection in a complex French sentence."""
        text = "Bien qu'il pleuve, nous sortons."
        clauses = detector.detect_clauses(text)
        
        assert len(clauses) >= 1
    
    def test_relative_clause_french(self, detector):
        """Test detection of French relative clauses."""
        text = "Le livre que j'ai lu était intéressant."
        clauses = detector.detect_clauses(text)
        
        assert len(clauses) >= 1


class TestSentenceClassifier:
    """Tests for sentence classification."""
    
    @pytest.fixture
    def classifier(self):
        """Create a SentenceClassifier instance for English."""
        detector = ClauseDetector(language="en")
        return SentenceClassifier(detector)
    
    def test_classify_simple(self, classifier):
        """Test classification of simple sentence."""
        text = "The dog barks."
        result = classifier.classify(text)
        
        assert result["sentence_type"] == SentenceType.SIMPLE
        assert result["independent_count"] >= 1
        assert result["dependent_count"] == 0
    
    def test_classify_compound(self, classifier):
        """Test classification of compound sentence."""
        text = "I like tea, and she likes coffee."
        result = classifier.classify(text)
        
        assert result["sentence_type"] == SentenceType.COMPOUND
        assert result["independent_count"] >= 2
        assert result["dependent_count"] == 0
    
    def test_classify_complex(self, classifier):
        """Test classification of complex sentence."""
        text = "Because I was tired, I went to bed early."
        result = classifier.classify(text)
        
        assert result["sentence_type"] == SentenceType.COMPLEX
        assert result["independent_count"] >= 1
        assert result["dependent_count"] >= 1
    
    def test_classify_compound_complex(self, classifier):
        """Test classification of compound-complex sentence."""
        text = "Although I was tired, I finished my work, and I went home."
        result = classifier.classify(text)
        
        assert result["sentence_type"] == SentenceType.COMPOUND_COMPLEX
        assert result["independent_count"] >= 2
        assert result["dependent_count"] >= 1
    
    def test_classify_batch(self, classifier):
        """Test batch classification."""
        texts = [
            "The sun shines.",
            "I read, and she writes.",
            "When it rains, I stay inside."
        ]
        results = classifier.classify_batch(texts)
        
        assert len(results) == 3
        assert all("sentence_type" in r for r in results)
    
    def test_result_structure(self, classifier):
        """Test that classification result has correct structure."""
        text = "The cat sleeps."
        result = classifier.classify(text)
        
        assert "sentence_type" in result
        assert "independent_count" in result
        assert "dependent_count" in result
        assert "clauses" in result
        assert isinstance(result["clauses"], list)
        assert isinstance(result["sentence_type"], SentenceType)
        assert isinstance(result["independent_count"], int)
        assert isinstance(result["dependent_count"], int)


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_detect_clauses_function(self):
        """Test the detect_clauses convenience function."""
        text = "The cat sleeps."
        clauses = detect_clauses(text, language="en")
        
        assert isinstance(clauses, list)
        assert len(clauses) >= 1
        assert all(isinstance(c, Clause) for c in clauses)
    
    def test_classify_sentence_function(self):
        """Test the classify_sentence convenience function."""
        text = "The dog barks."
        result = classify_sentence(text, language="en")
        
        assert "sentence_type" in result
        assert isinstance(result["sentence_type"], SentenceType)
    
    def test_invalid_language(self):
        """Test handling of invalid language."""
        with pytest.raises(ValueError):
            detect_clauses("test", language="invalid")


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    @pytest.fixture
    def detector(self):
        """Create a ClauseDetector instance."""
        return ClauseDetector(language="en")
    
    def test_very_long_sentence(self, detector):
        """Test handling of very long sentences."""
        text = " and ".join(["I went to the store"] * 10)
        clauses = detector.detect_clauses(text)
        
        # Should handle without errors
        assert isinstance(clauses, list)
    
    def test_punctuation_heavy(self, detector):
        """Test handling of sentences with heavy punctuation."""
        text = "Well, honestly, I think - and this is important - that we should go!"
        clauses = detector.detect_clauses(text)
        
        assert isinstance(clauses, list)
    
    def test_sentence_with_quotes(self, detector):
        """Test handling of sentences with quotes."""
        text = 'She said, "I am happy."'
        clauses = detector.detect_clauses(text)
        
        assert isinstance(clauses, list)
    
    def test_multiple_sentences(self, detector):
        """Test handling of multiple sentences in one string."""
        text = "I like coffee. She likes tea."
        clauses = detector.detect_clauses(text)
        
        # Should detect clauses from both sentences
        assert isinstance(clauses, list)


class TestClauseObject:
    """Tests for the Clause dataclass."""
    
    def test_clause_creation(self):
        """Test creating a Clause object."""
        clause = Clause(
            text="The cat sleeps",
            clause_type=ClauseType.INDEPENDENT,
            start=0,
            end=3
        )
        
        assert clause.text == "The cat sleeps"
        assert clause.clause_type == ClauseType.INDEPENDENT
        assert clause.start == 0
        assert clause.end == 3
    
    def test_clause_repr(self):
        """Test string representation of Clause."""
        clause = Clause(
            text="test",
            clause_type=ClauseType.DEPENDENT,
            start=0,
            end=1
        )
        
        repr_str = repr(clause)
        assert "dependent" in repr_str
        assert "test" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])