import spacy
from spacy.symbols import CCONJ, SCONJ, ADP, PROPN

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Parameters
CHUNK_MIN_WORDS = 3
CHUNK_MAX_WORDS = 9

# Define POS tags for potential pause points
PAUSE_POS = {CCONJ, SCONJ, ADP}  # coordinating conj, subordinate conj, prepositions

def is_named_entity(token):
    return token.ent_type_ != ""

def find_split_index(tokens):
    """
    Return the index of the first token suitable for a split, considering:
    - Pause POS
    - Not inside named entities
    - Avoid first token
    """
    for i, token in enumerate(tokens[1:], start=1):  # avoid splitting at first token
        if token.pos in PAUSE_POS and not any(is_named_entity(t) for t in tokens[:i+1]):
            return i
    return None  # no suitable split

def recursive_chunk(tokens):
    """
    Recursively split tokens into semantic chunks.
    """
    n = len(tokens)
    
    # Base case: chunk is small enough
    if n <= CHUNK_MAX_WORDS:
        return [" ".join([t.text for t in tokens])]
    
    # Find split point
    split_idx = find_split_index(tokens)
    
    # If no split point found, split roughly at midpoint
    if split_idx is None:
        split_idx = n // 2
        # Ensure both chunks >= CHUNK_MIN_WORDS
        if split_idx < CHUNK_MIN_WORDS:
            split_idx = CHUNK_MIN_WORDS
        elif n - split_idx < CHUNK_MIN_WORDS:
            split_idx = n - CHUNK_MIN_WORDS
    
    # Recursively process each sub-chunk
    left = recursive_chunk(tokens[:split_idx])
    right = recursive_chunk(tokens[split_idx:])
    
    return left + right

def chunk_sentence(sentence, break_marker="//"):
    """
    Split a sentence into natural semantic chunks with the chosen break marker.
    """
    doc = nlp(sentence)
    chunks = []
    
    for sent in doc.sents:  # process each sentence separately
        tokens = list(sent)
        sub_chunks = recursive_chunk(tokens)
        chunks.append(f" {break_marker} ".join(sub_chunks))
    
    return " ".join(chunks)

# Example usage
text = "Although the project faced several challenges, the team managed to deliver the final product on time and within budget."
chunked_text = chunk_sentence(text, break_marker="//")
print(chunked_text)
