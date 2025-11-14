import spacy

nlp = spacy.load("en_core_web_sm")
text = "I left because it was late, and I took a taxi when it started raining."

doc = nlp(text)

print("Analyzing 'took' (token 9):\n")
root = doc[9]
print(f"Root: {root.i} - '{root.text}' (dep={root.dep_})")
print(f"\nDirect children of 'took':")
for child in root.children:
    print(f"  {child.i}: '{child.text}' (dep={child.dep_}, pos={child.pos_})")

print(f"\nChildren of 'when' (token 12, should be advmod of 'started'):")
when_token = doc[12]
print(f"Token 12: '{when_token.text}' (dep={when_token.dep_}, head={when_token.head.i})")

print(f"\nChildren of 'started' (token 14):")
started = doc[14]
print(f"Token 14: '{started.text}' (dep={started.dep_}, head={started.head.i})")
for child in started.children:
    print(f"  {child.i}: '{child.text}' (dep={child.dep_})")

print(f"\nSo 'when' is NOT a direct child of 'took', it's a child of 'started'")
print(f"When extracting 'took' clause and encountering its child 'started',")
print(f"we need to find 'started's markers, which includes finding tokens")
print(f"that precede 'started' and are not part of 'took's direct children")
