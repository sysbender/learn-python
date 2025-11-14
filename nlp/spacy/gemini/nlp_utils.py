import spacy
from spacy.tokens import Doc
from typing import Dict, List, Tuple

# --- Configuration and Model Loading ---

MODEL_MAP: Dict[str, str] = {
    "en": "en_core_web_sm",
    "fr": "fr_core_news_sm"
}

# In-memory cache for loaded models
_loaded_models: Dict[str, spacy.Language] = {}

def load_nlp_model(lang_code: str) -> spacy.Language:
    """Loads a spaCy model for the specified language, using caching."""
    if lang_code not in MODEL_MAP:
        raise ValueError(f"Unsupported language code: {lang_code}. Supported: {list(MODEL_MAP.keys())}")

    model_name = MODEL_MAP[lang_code]
    if model_name not in _loaded_models:
        try:
            nlp = spacy.load(model_name)
            _loaded_models[model_name] = nlp
            print(f"Successfully loaded spaCy model: {model_name}")
        except OSError:
            print(f"Downloading model {model_name}...")
            # Note: In a real environment, you might need to run:
            # spacy.cli.download(model_name)
            # This implementation assumes the models are already installed or available.
            raise EnvironmentError(f"spaCy model '{model_name}' not found. Please run 'python -m spacy download {model_name}'")

    return _loaded_models[model_name]


# --- Clause Detection Implementation ---

class ClauseDetector:
    """
    Detects and extracts clauses (independent and dependent) from a spaCy Doc.
    This implementation uses heuristics based on dependency parsing.
    """
    def __init__(self, nlp: spacy.Language):
        self.nlp = nlp
        # Common dependency labels for identifying clause structure
        self.COORD_CONJ = 'cc' # Coordinating conjunction (e.g., and, but, or)
        self.SUBORD_MARKER = 'mark' # Subordinating conjunction (e.g., when, because, if)
        self.RELATIVE_CLAUSE = 'relcl' # Relative clause modifier
        self.ADVERBIAL_CLAUSE = 'advcl' # Adverbial clause modifier
        self.CONJUNCT = 'conj' # Conjunction (linking coordinate elements)

    def _get_clause_span(self, head_token: spacy.tokens.Token) -> spacy.tokens.Span:
        """
        Recursively determines the full span of a clause rooted at the head_token.
        This is a common dependency parsing utility function.
        """
        start = head_token.i
        end = head_token.i + 1

        # Look for the leftmost child (often a subordinating marker or subject)
        # and the rightmost child (often objects or modifiers)
        tokens_in_clause = set([head_token])

        # Traverse all descendants
        for child in head_token.subtree:
            tokens_in_clause.add(child)

        # Include the subordinating marker/conjunction if it introduces the clause
        for token in head_token.ancestors:
            # Check if this ancestor is a marker/cc that immediately precedes the head
            if token.dep_ in [self.SUBORD_MARKER, self.COORD_CONJ, 'prep', 'pobj'] and token.i < head_token.i:
                 # Check if the marker is directly related to the head (or its subject)
                if token.head == head_token or token.head in head_token.children:
                    tokens_in_clause.add(token)


        if not tokens_in_clause:
            return head_token.doc[start:end]

        min_i = min(t.i for t in tokens_in_clause)
        max_i = max(t.i for t in tokens_in_clause) + 1

        # Ensure the span doesn't go beyond the sentence boundaries
        sent_start = head_token.sent.start
        sent_end = head_token.sent.end
        
        return head_token.doc[max(sent_start, min_i): min(sent_end, max_i)]

    def detect(self, doc: Doc) -> Tuple[List[str], List[str]]:
        """
        Analyzes a Doc and returns a tuple of (independent_clauses, dependent_clauses).
        """
        independent_clauses: List[spacy.tokens.Span] = []
        dependent_clauses: List[spacy.tokens.Span] = []
        
        # We only process the first sentence for simplicity, as classification is sentence-level
        sentence = next(doc.sents, None)
        if not sentence:
            return [], []

        # We will track which tokens are already covered by a clause span
        covered_tokens = set()

        # Step 1: Find all main verbs/clause roots within the sentence
        clause_heads: List[spacy.tokens.Token] = []
        
        # The true root of the sentence is always an Independent Clause head
        if sentence.root.pos_ == 'VERB' or sentence.root.pos_ == 'AUX':
            clause_heads.append(sentence.root)
            
        # Look for other verbs that could be clause heads
        for token in sentence:
            if token.pos_ == 'VERB' or token.pos_ == 'AUX':
                # Check for verbs connected by conjunctions (IC) or markers (DC)
                if token.dep_ == self.CONJUNCT and token.head.pos_ in ['VERB', 'AUX']:
                    clause_heads.append(token) # Potential IC (Compound)
                elif token.dep_ in [self.RELATIVE_CLAUSE, self.ADVERBIAL_CLAUSE]:
                    clause_heads.append(token) # Potential DC (Complex)

        # Step 2: Classify and extract spans
        processed_clause_texts: set = set()

        for head in clause_heads:
            span = self._get_clause_span(head)
            span_text = span.text.strip()
            
            if not span_text or span_text in processed_clause_texts:
                continue

            # Check if the clause is Dependent or Independent
            is_dependent = False
            
            # Check for DC markers in the current clause span or immediately preceding it
            for token in span:
                if token.dep_ == self.SUBORD_MARKER or token.dep_ == self.RELATIVE_CLAUSE:
                    is_dependent = True
                    break
            
            # If the head is a DC dependency, it's a DC (e.g., advcl, relcl)
            if head.dep_ in [self.RELATIVE_CLAUSE, self.ADVERBIAL_CLAUSE] or \
               any(child.dep_ == self.SUBORD_MARKER for child in head.children):
                is_dependent = True

            # The root of the sentence is always an IC unless introduced by a mark (e.g., 'That she left is true')
            if head == sentence.root and not is_dependent:
                independent_clauses.append(span)
            elif head.dep_ == self.CONJUNCT and head.head.dep_ not in [self.RELATIVE_CLAUSE, self.ADVERBIAL_CLAUSE]:
                independent_clauses.append(span) # Coordinated ICs
            elif is_dependent:
                dependent_clauses.append(span)

            processed_clause_texts.add(span_text)


        # Final cleaning and deduplication based on text (since span extraction is heuristic)
        ic_texts = list(sorted(list(set([span.text.strip() for span in independent_clauses]))))
        dc_texts = list(sorted(list(set([span.text.strip() for span in dependent_clauses]))))
        
        return ic_texts, dc_texts


# --- Sentence Type Classifier Implementation ---

class SentenceClassifier:
    """
    Classifies a sentence based on the number of independent and dependent clauses.
    Requires a ClauseDetector instance.
    """
    def __init__(self, detector: ClauseDetector):
        self.detector = detector

    def classify(self, text: str) -> Dict[str, str | int | List[str]]:
        """
        Classifies the input text (sentence) and returns the analysis.
        """
        doc = self.detector.nlp(text)
        
        # Only process the first sentence for classification
        sentence = next(doc.sents, None)
        if not sentence:
            return {
                "text": text,
                "classification": "Incomplete Sentence/Other",
                "independent_clauses": 0,
                "dependent_clauses": 0,
                "ic_texts": [],
                "dc_texts": []
            }

        ic_texts, dc_texts = self.detector.detect(doc)
        
        ic_count = len(ic_texts)
        dc_count = len(dc_texts)
        
        classification = "Other"

        if ic_count >= 2 and dc_count >= 1:
            classification = "Compound-Complex"
        elif ic_count >= 2 and dc_count == 0:
            classification = "Compound"
        elif ic_count == 1 and dc_count >= 1:
            classification = "Complex"
        elif ic_count == 1 and dc_count == 0:
            classification = "Simple"
        else:
            # Covers cases like fragments (0 IC, 1 DC) or malformed sentences
            classification = "Fragment/Other"

        return {
            "text": sentence.text.strip(),
            "classification": classification,
            "independent_clauses": ic_count,
            "dependent_clauses": dc_count,
            "ic_texts": ic_texts,
            "dc_texts": dc_texts
        }

if __name__ == '__main__':
    # Example usage for English
    print("--- English Example ---")
    en_nlp = load_nlp_model("en")
    en_detector = ClauseDetector(en_nlp)
    en_classifier = SentenceClassifier(en_detector)

    # Compound-Complex example
    en_text = "When the bell rang, the students stood up, and the teacher smiled because the day was over."
    en_analysis = en_classifier.classify(en_text)
    print(f"Text: {en_analysis['text']}")
    print(f"Classification: {en_analysis['classification']}")
    print(f"ICs ({en_analysis['independent_clauses']}): {en_analysis['ic_texts']}")
    print(f"DCs ({en_analysis['dependent_clauses']}): {en_analysis['dc_texts']}")
    
    print("\n--- French Example ---")
    # Example usage for French
    fr_nlp = load_nlp_model("fr")
    fr_detector = ClauseDetector(fr_nlp)
    fr_classifier = SentenceClassifier(fr_detector)

    # Complex example
    fr_text = "Le chat, qui était très curieux, a sauté sur la table."
    fr_analysis = fr_classifier.classify(fr_text)
    print(f"Text: {fr_analysis['text']}")
    print(f"Classification: {fr_analysis['classification']}")
    print(f"ICs ({fr_analysis['independent_clauses']}): {fr_analysis['ic_texts']}")
    print(f"DCs ({fr_analysis['dependent_clauses']}): {fr_analysis['dc_texts']}")