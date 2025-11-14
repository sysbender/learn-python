"""
Clause Detection and Sentence Classification Module

This module provides functionality for:
1. Detecting clauses in sentences using spaCy's dependency parsing
2. Classifying sentences by their structure (simple, compound, complex, compound-complex)

Supports both English and French languages.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import spacy
from spacy.tokens import Doc, Span, Token


class SentenceType(Enum):
    """Enumeration of sentence types based on clause structure."""
    SIMPLE = "simple"
    COMPOUND = "compound"
    COMPLEX = "complex"
    COMPOUND_COMPLEX = "compound-complex"
    OTHER = "other"


class ClauseType(Enum):
    """Enumeration of clause types."""
    INDEPENDENT = "independent"
    DEPENDENT = "dependent"


@dataclass
class Clause:
    """Represents a clause with its text, type, and span information."""
    text: str
    clause_type: ClauseType
    start: int
    end: int
    root_token: Optional[Token] = None

    def __repr__(self):
        return f"Clause(type={self.clause_type.value}, text='{self.text}')"


class ClauseDetector:
    """
    Detects clauses in sentences using spaCy's dependency parsing.
    
    Supports English and French. The detector identifies clause boundaries
    by finding verbal predicates and their associated arguments.
    """
    
    # Dependency relations that indicate subordination (dependent clauses)
    SUBORDINATE_DEPS = {
        'mark',      # marker (because, although, if, etc.)
        'advcl',     # adverbial clause modifier
        'acl',       # clausal modifier of noun (adjectival clause)
        'ccomp',     # clausal complement
        'xcomp',     # open clausal complement
        'relcl',     # relative clause modifier
    }
    
    # Coordinating conjunctions for compound structures
    COORDINATING_DEPS = {'conj', 'cc'}
    
    def __init__(self, language: str = "en"):
        """
        Initialize the clause detector.
        
        Args:
            language: Language code ('en' for English, 'fr' for French)
        """
        self.language = language
        self.nlp = self._load_model(language)
    
    def _load_model(self, language: str) -> spacy.Language:
        """Load appropriate spaCy model for the language."""
        models = {
            "en": "en_core_web_sm",
            "fr": "fr_core_news_sm"
        }
        
        model_name = models.get(language)
        if not model_name:
            raise ValueError(f"Unsupported language: {language}")
        
        try:
            return spacy.load(model_name)
        except OSError:
            raise OSError(
                f"Model '{model_name}' not found. "
                f"Install it with: python -m spacy download {model_name}"
            )
    
    def _find_clause_roots(self, doc: Doc) -> List[Token]:
        """
        Find tokens that serve as roots of clauses (typically verbs).
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            List of tokens that are clause roots
        """
        roots = []
        
        for token in doc:
            # Main verb (root of sentence)
            if token.dep_ == "ROOT" and token.pos_ in ("VERB", "AUX"):
                roots.append(token)
            
            # Subordinate clauses
            elif token.dep_ in self.SUBORDINATE_DEPS and token.pos_ in ("VERB", "AUX"):
                roots.append(token)
            
            # Coordinated verbs (compound sentences)
            elif token.dep_ == "conj" and token.pos_ in ("VERB", "AUX"):
                roots.append(token)
        
        return roots
    
    def _get_clause_span(self, root: Token, doc: Doc) -> Tuple[int, int]:
        """
        Get the start and end indices for a clause based on its root.
        
        Args:
            root: Root token of the clause
            doc: spaCy Doc object
            
        Returns:
            Tuple of (start_index, end_index)
        """
        # Get all descendants of the root
        descendants = list(root.subtree)
        
        if not descendants:
            return root.i, root.i + 1
        
        start = min(token.i for token in descendants)
        end = max(token.i for token in descendants) + 1
        
        return start, end
    
    def _is_dependent_clause(self, root: Token) -> bool:
        """
        Determine if a clause is dependent based on its root token.
        
        Args:
            root: Root token of the clause
            
        Returns:
            True if the clause is dependent, False if independent
        """
        # Check if the token has a subordinating marker
        if root.dep_ in self.SUBORDINATE_DEPS:
            return True
        
        # Check if any child is a subordinating conjunction
        for child in root.children:
            if child.dep_ == "mark":  # Subordinating conjunction marker
                return True
        
        # ROOT dependency indicates main/independent clause
        if root.dep_ == "ROOT":
            return False
        
        # Coordinated clauses (conj) with ROOT ancestor are independent
        if root.dep_ == "conj":
            # Check if it's coordinated with a ROOT
            head = root.head
            while head.dep_ != "ROOT" and head.head != head:
                head = head.head
            return head.dep_ != "ROOT"
        
        return False
    
    def _clean_clause_text(self, text: str) -> str:
        """
        Clean clause text by removing extra whitespace.
        
        Args:
            text: Raw clause text
            
        Returns:
            Cleaned clause text
        """
        return " ".join(text.split())
    
    def detect_clauses(self, text: str) -> List[Clause]:
        """
        Detect all clauses in the given text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of Clause objects
        """
        doc = self.nlp(text)
        clause_roots = self._find_clause_roots(doc)
        
        clauses = []
        seen_spans = set()
        
        for root in clause_roots:
            start, end = self._get_clause_span(root, doc)
            
            # Avoid duplicate clauses
            span_key = (start, end)
            if span_key in seen_spans:
                continue
            seen_spans.add(span_key)
            
            clause_text = self._clean_clause_text(doc[start:end].text)
            is_dependent = self._is_dependent_clause(root)
            
            clause = Clause(
                text=clause_text,
                clause_type=ClauseType.DEPENDENT if is_dependent else ClauseType.INDEPENDENT,
                start=start,
                end=end,
                root_token=root
            )
            clauses.append(clause)
        
        # Sort by position in text
        clauses.sort(key=lambda c: c.start)
        
        return clauses


class SentenceClassifier:
    """
    Classifies sentences based on their clause structure.
    
    Sentence types:
    - Simple: One independent clause
    - Compound: Two or more independent clauses
    - Complex: One independent clause and at least one dependent clause
    - Compound-Complex: Two or more independent clauses and at least one dependent clause
    """
    
    def __init__(self, clause_detector: ClauseDetector):
        """
        Initialize the sentence classifier.
        
        Args:
            clause_detector: ClauseDetector instance to use for clause detection
        """
        self.clause_detector = clause_detector
    
    def classify(self, text: str) -> Dict:
        """
        Classify a sentence based on its clause structure.
        
        Args:
            text: Input sentence to classify
            
        Returns:
            Dictionary containing:
                - sentence_type: SentenceType enum value
                - independent_count: Number of independent clauses
                - dependent_count: Number of dependent clauses
                - clauses: List of detected Clause objects
        """
        clauses = self.clause_detector.detect_clauses(text)
        
        independent_count = sum(
            1 for c in clauses if c.clause_type == ClauseType.INDEPENDENT
        )
        dependent_count = sum(
            1 for c in clauses if c.clause_type == ClauseType.DEPENDENT
        )
        
        # Determine sentence type
        if independent_count == 1 and dependent_count == 0:
            sentence_type = SentenceType.SIMPLE
        elif independent_count >= 2 and dependent_count == 0:
            sentence_type = SentenceType.COMPOUND
        elif independent_count == 1 and dependent_count >= 1:
            sentence_type = SentenceType.COMPLEX
        elif independent_count >= 2 and dependent_count >= 1:
            sentence_type = SentenceType.COMPOUND_COMPLEX
        else:
            sentence_type = SentenceType.OTHER
        
        return {
            "sentence_type": sentence_type,
            "independent_count": independent_count,
            "dependent_count": dependent_count,
            "clauses": clauses
        }
    
    def classify_batch(self, texts: List[str]) -> List[Dict]:
        """
        Classify multiple sentences.
        
        Args:
            texts: List of input sentences
            
        Returns:
            List of classification results
        """
        return [self.classify(text) for text in texts]


# Convenience functions for easy usage
def detect_clauses(text: str, language: str = "en") -> List[Clause]:
    """
    Convenience function to detect clauses in text.
    
    Args:
        text: Input text
        language: Language code ('en' or 'fr')
        
    Returns:
        List of Clause objects
    """
    detector = ClauseDetector(language=language)
    return detector.detect_clauses(text)


def classify_sentence(text: str, language: str = "en") -> Dict:
    """
    Convenience function to classify a sentence.
    
    Args:
        text: Input sentence
        language: Language code ('en' or 'fr')
        
    Returns:
        Classification results dictionary
    """
    detector = ClauseDetector(language=language)
    classifier = SentenceClassifier(detector)
    return classifier.classify(text)