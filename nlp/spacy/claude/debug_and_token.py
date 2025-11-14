import spacy

nlp = spacy.load("en_core_web_sm")
text = "I left because it was late, and I took a taxi when it started raining."

doc = nlp(text)

print("Looking at token 9 ('took'):")
root = doc[9]
print(f"root.i = {root.i}")
print(f"root.dep_ = '{root.dep_}'")
print()

print("Descendants of 'took':")
descendants = list(root.subtree)
for d in descendants:
    print(f"  {d.i}: {d.text}")

print(f"\nmin(descendants) = {min(d.i for d in descendants)}")
print()

print("Tokens from 6 to 10:")
for i in range(6, 10):
    token = doc[i]
    print(f"  {i}: '{token.text}' pos={token.pos_:8s}, dep={token.dep_}")
