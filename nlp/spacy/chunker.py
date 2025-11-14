import spacy
from spacy.symbols import CCONJ, SCONJ, ADP

PAUSE_RULES = {
    "en": {
        "subord": {"although", "because", "which", "if", "when", "while"},
        "coord": {"and", "but", "or"}
    },
    "fr": {
        "subord": {"bien que", "parce que", "qui", "si", "lorsque", "pendant que"},
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
        self.PAUSE_POS = {CCONJ, SCONJ, ADP}
        self.SUBORD_CONJ = PAUSE_RULES[lang]["subord"]
        self.COORD_CONJ = PAUSE_RULES[lang]["coord"]

    def is_named_entity(self, token):
        return token.ent_type_ != ""
    
    def find_split_index(self, tokens):
        """
        Find a good split index:
        - Prefer commas first
        - Then subordinate conjunctions
        - Then coordinating conjunctions
        - Then prepositions if chunk is long
        Returns None if no suitable split is found.
        """
        n = len(tokens)
        
        # 1️ Split at comma if both sides >= 3 words
        for i, token in enumerate(tokens[1:], start=1):
            if token.text == "," and i >= self.CHUNK_MIN_WORDS and (n - i) >= self.CHUNK_MIN_WORDS:
                return i + 1  # include comma in left chunk

        # 2️ Subordinate conjunctions
        for i, token in enumerate(tokens[1:], start=1):
            if token.text.lower() in self.SUBORD_CONJ and i >= self.CHUNK_MIN_WORDS and (n - i) >= self.CHUNK_MIN_WORDS:
                return i

        # 3️ Coordinating conjunctions
        for i, token in enumerate(tokens[1:], start=1):
            if token.text.lower() in self.COORD_CONJ and i >= self.CHUNK_MIN_WORDS and (n - i) >= self.CHUNK_MIN_WORDS:
                return i

        # 4️ Prepositions if chunk is very long
        for i, token in enumerate(tokens[1:], start=1):
            if token.pos == ADP and n > self.CHUNK_MAX_WORDS and i >= self.CHUNK_MIN_WORDS and (n - i) >= self.CHUNK_MIN_WORDS:
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
    # English
    chunker_en = SemanticChunker(lang="en")
    text_en = "Although the project faced several challenges, the team delivered the final product on time."
    print(chunker_en.chunk_sentence(text_en))

    # French
    chunker_fr = SemanticChunker(lang="fr")
    text_fr = "Bien que le projet ait rencontré plusieurs défis, l'équipe a livré le produit final à temps."
    print(chunker_fr.chunk_sentence(text_fr))
