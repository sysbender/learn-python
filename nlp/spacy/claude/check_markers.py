import spacy

nlp = spacy.load("en_core_web_sm")

# Test different sentences
test_sentences = [
    "I left because it was late.",
    "I took a taxi when it rained.",
    "I went there although it was late.",
    "He ran fast so he won.",
]

for sent in test_sentences:
    doc = nlp(sent)
    print(f"\nSentence: {sent}")
    for token in doc:
        if token.pos_ in ("SCONJ", "CCONJ") or token.dep_ in ("mark", "cc", "advmod"):
            print(f"  {token.i}: '{token.text}' (pos={token.pos_}, dep={token.dep_})")
