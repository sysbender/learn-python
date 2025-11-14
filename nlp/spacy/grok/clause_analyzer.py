# clause_analyzer.py
from __future__ import annotations

from typing import List, Tuple, Dict, Any, Optional
import spacy
from spacy.tokens import Doc, Token, Span
from spacy.language import Language

# Language-specific models
SPACY_MODELS = {
    "en": "en_core_web_sm",
    "fr": "fr_core_news_sm",
}

# Clause boundary markers (ROOT verbs, conjunctions, etc.)
CLAUSE_ROOT_DEPS = {"ROOT"}
SUBORDINATING_CONJ_DEPS = {"mark", "fixed"}  # e.g., "that", "because", "si", "que"
COORDINATING_CONJ_DEPS = {"cc"}  # e.g., "and", "but", "et", "mais"
RELATIVE_PRONOUN_DEPS = {"relcl", "csubj", "ccomp", "xcomp", "advcl"}


class ClauseAnalyzer:
    """Detect clauses and classify sentence types using spaCy dependency parsing."""

    def __init__(self, lang: str = "en"):
        """
        Initialize with language-specific spaCy model.

        Args:
            lang: Language code ('en' or 'fr')
        """
        if lang not in SPACY_MODELS:
            raise ValueError(f"Unsupported language: {lang}. Choose from {list(SPACY_MODELS.keys())}")
        self.lang = lang
        self.nlp = spacy.load(SPACY_MODELS[lang])
        self._register_extensions()

    def _register_extensions(self) -> None:
        """Register custom token/doc extensions."""
        if not Doc.has_extension("clauses"):
            Doc.set_extension("clauses", default=[])
        if not Doc.has_extension("sentence_type"):
            Doc.set_extension("sentence_type", default=None)

    def detect_clauses(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect clauses in a sentence using dependency parsing.

        Args:
            text: Input sentence

        Returns:
            List of clause dicts: {'text': str, 'span': (start, end), 'type': 'ind'|'dep'}
        """
        doc = self.nlp(text.strip())
        if not doc:
            return []

        clauses = []
        visited = set()

        # Find all root verbs → potential independent clauses
        roots = [tok for tok in doc if tok.dep_ == "ROOT" and tok.pos_ in {"VERB", "AUX"}]

        for root in roots:
            clause_span = self._get_clause_span(doc, root, visited)
            if clause_span:
                clauses.append({
                    "text": clause_span.text,
                    "span": (clause_span.start, clause_span.end),
                    "type": "ind" if root.dep_ == "ROOT" else "dep",
                    "root": root.i
                })
                visited.update(range(clause_span.start, clause_span.end))

        # Find remaining dependent clauses (advcl, ccomp, relcl, etc.)
        for tok in doc:
            if tok.i in visited:
                continue
            if tok.dep_ in RELATIVE_PRONOUN_DEPS and tok.head.pos_ in {"VERB", "AUX"}:
                clause_span = self._get_clause_span(doc, tok, visited)
                if clause_span:
                    clauses.append({
                        "text": clause_span.text,
                        "span": (clause_span.start, clause_span.end),
                        "type": "dep",
                        "root": tok.i
                    })
                    visited.update(range(clause_span.start, clause_span.end))

        # Sort by start position
        clauses.sort(key=lambda x: x["span"][0])

        # Attach to doc
        doc._.clauses = clauses
        return clauses

    def _get_clause_span(self, doc: Doc, root: Token, visited: set) -> Optional[Span]:
        """
        Extract full clause span around a root verb using subtree + conjunction logic.
        """
        subtree_tokens = list(root.subtree)
        if not subtree_tokens:
            return None

        start = min(t.i for t in subtree_tokens)
        end = max(t.i for t in subtree_tokens) + 1

        # Expand left for subject/nsubj if not in subtree
        current = root
        while current.dep_ in {"csubj", "nsubj", "nsubj:pass"} and current.head.i >= 0:
            current = current.head
            if current.i < start and current.i not in visited:
                start = current.i

        # Expand for coordinating conjunctions (compound sentences)
        if root.dep_ == "ROOT":
            for child in root.children:
                if child.dep_ == "cc":
                    conj = next((c for c in child.children if c.dep_ == "conj"), None)
                    if conj and conj.pos_ in {"VERB", "AUX"}:
                        conj_span = self._get_clause_span(doc, conj, visited)
                        if conj_span:
                            end = max(end, conj_span.end)

        return doc[start:end] if start < end else None

    def classify_sentence_type(self, text: str) -> str:
        """
        Classify sentence type based on clause count and types.

        Rules:
        - 1 ind → simple
        - 2+ ind + 0 dep → compound
        - 1 ind + 1+ dep → complex
        - 2+ ind + 1+ dep → compound-complex
        - else → other
        """
        clauses = self.detect_clauses(text)
        ind_count = sum(1 for c in clauses if c["type"] == "ind")
        dep_count = sum(1 for c in clauses if c["type"] == "dep")

        if ind_count == 1 and dep_count == 0:
            return "simple"
        elif ind_count >= 2 and dep_count == 0:
            return "compound"
        elif ind_count == 1 and dep_count >= 1:
            return "complex"
        elif ind_count >= 2 and dep_count >= 1:
            return "compound-complex"
        else:
            return "other"

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Full analysis: clauses + sentence type.
        """
        doc = self.nlp(text.strip())
        clauses = self.detect_clauses(text)
        sentence_type = self.classify_sentence_type(text)
        doc._.sentence_type = sentence_type

        return {
            "text": text,
            "clauses": clauses,
            "sentence_type": sentence_type,
            "independent_count": sum(1 for c in clauses if c["type"] == "ind"),
            "dependent_count": sum(1 for c in clauses if c["type"] == "dep"),
        }