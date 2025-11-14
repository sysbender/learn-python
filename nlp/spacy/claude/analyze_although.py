import spacy

nlp = spacy.load("en_core_web_sm")
text = "Although it was cold, we played outside."

doc = nlp(text)

print("Tokens and dependencies:")
for token in doc:
    print(f"{token.i:2d}: {token.text:15s} pos={token.pos_:8s} dep={token.dep_:10s} head={token.head.i}")
