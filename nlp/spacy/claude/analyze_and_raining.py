import spacy

nlp = spacy.load("en_core_web_sm")
text = "I left because it was late, and I took a taxi when it started raining."

doc = nlp(text)

print("Token analysis:")
for i, token in enumerate(doc):
    print(f"{i:2d}: {token.text:15s} pos={token.pos_:8s} dep={token.dep_:10s} head={token.head.i}")

print("\n\nAnalyzing 'and' (token 7):")
and_token = doc[7]
print(f"Token 7: '{and_token.text}' (pos={and_token.pos_}, dep={and_token.dep_}, head={and_token.head})")

print("\nAnalyzing 'raining' (token 15):")
raining = doc[15]
print(f"Token 15: '{raining.text}' (pos={raining.pos_}, dep={raining.dep_}, head={raining.head.i})")
print(f"Is 'raining' a clause root? It depends on if we're finding it as such...")
