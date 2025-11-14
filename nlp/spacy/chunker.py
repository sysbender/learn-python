import spacy
from spacy.symbols import CCONJ, SCONJ, ADP, VERB

PAUSE_RULES = {
    "en": {
        "subord": {"although", "because", "which", "if", "when", "while"},
        "coord": {"and", "but", "or"}
    },
    "fr": {
        # Added missing subordinates: 'que', 'quand'
        "subord": {"bien que", "parce que", "qui", "si", "lorsque", "pendant que", "que", "quand"},
        "coord": {"et", "mais", "ou"}
    }
}

SPACY_MODELS = {
    "en": "en_core_web_sm",
    "fr": "fr_core_news_sm"
}

class SemanticChunker:
    def __init__(self, lang="en", chunk_min_words=3, chunk_max_words=9, break_marker="//"):
        if lang not in SPACY_MODELS:
            raise ValueError(f"Language {lang} not supported.")
        self.lang = lang
        self.nlp = spacy.load(SPACY_MODELS[lang])
        self.CHUNK_MIN_WORDS = chunk_min_words
        self.CHUNK_MAX_WORDS = chunk_max_words
        self.break_marker = break_marker
        self.SUBORD_CONJ = PAUSE_RULES[lang]["subord"]
        self.COORD_CONJ = PAUSE_RULES[lang]["coord"]

    def is_named_entity(self, token):
        return token.ent_type_ != ""

    def get_protected_spans(self, tokens):
        """Return a list of (start, end) indexes that should NOT be split."""
        protected = []

        doc = tokens[0].doc
        for ent in doc.ents:
            protected.append((ent.start, ent.end))

        for token in tokens:
            if token.pos == ADP:
                span = (min([t.i for t in token.subtree]), max([t.i for t in token.subtree]) + 1)
                protected.append(span)

        for token in tokens:
            if token.pos == VERB:
                dobj_children = [child for child in token.children if child.dep_ in ("obj", "iobj")]
                if dobj_children:
                    start = token.i
                    end = max([child.i for child in dobj_children] + [token.i]) + 1
                    protected.append((start, end))

        return protected

    def token_in_protected(self, idx, protected_spans):
        """Check if token idx is inside any protected span"""
        for start, end in protected_spans:
            if start <= idx < end:
                return True
        return False

    def find_split_index(self, tokens):
        n = len(tokens)
        protected_spans = self.get_protected_spans(tokens)

        # Helper to check if split would leave chunks too small
        def valid_split(i):
            return i >= self.CHUNK_MIN_WORDS and (n - i) >= self.CHUNK_MIN_WORDS

        # 1️ Comma split
        for i, token in enumerate(tokens[1:], start=1):
            if token.text == "," and valid_split(i) and not self.token_in_protected(i, protected_spans):
                return i + 1  # include comma in left chunk

        # 2️ Subordinate conjunctions
        for i, token in enumerate(tokens[1:], start=1):
            if token.text.lower() in self.SUBORD_CONJ and valid_split(i) and not self.token_in_protected(i, protected_spans):
                return i

        # 3️ Coordinating conjunctions
        for i, token in enumerate(tokens[1:], start=1):
            if token.text.lower() in self.COORD_CONJ and valid_split(i) and not self.token_in_protected(i, protected_spans):
                return i

        # 4️ Prepositions if sentence is long
        for i, token in enumerate(tokens[1:], start=1):
            if token.pos == ADP and n > self.CHUNK_MAX_WORDS and valid_split(i) and not self.token_in_protected(i, protected_spans):
                return i

        return None

    def recursive_chunk(self, tokens):
        n = len(tokens)
        if n <= self.CHUNK_MAX_WORDS:
            return ["".join([t.text_with_ws for t in tokens]).strip()]

        split_idx = self.find_split_index(tokens)
        if split_idx is None:
            return ["".join([t.text_with_ws for t in tokens]).strip()]

        left = self.recursive_chunk(tokens[:split_idx])
        right = self.recursive_chunk(tokens[split_idx:])
        return left + right

    def chunk_sentence(self, text):
        doc = self.nlp(text)
        chunks = []
        for sent in doc.sents:
            tokens = list(sent)
            sub_chunks = self.recursive_chunk(tokens)
            chunks.append(f" {self.break_marker} ".join(sub_chunks))
        return " ".join(chunks)


if __name__ == "__main__":
    # English test
    chunker_en = SemanticChunker(lang="en")
    text_en = "Although the project faced several challenges, the team delivered the final product on time."
    print(chunker_en.chunk_sentence(text_en))

    # French test
    chunker_fr = SemanticChunker(lang="fr")
    text_fr = "Je regardais souvent avec mes parents quand j'étais plus petite."
    print(chunker_fr.chunk_sentence(text_fr))
