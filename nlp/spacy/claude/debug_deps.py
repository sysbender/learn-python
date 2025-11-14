import spacy

nlp = spacy.load("en_core_web_sm")
text = "I left because it was late, and I took a taxi when it started raining."

doc = nlp(text)

print("Tokens and their dependencies:")
print("-" * 80)
for token in doc:
    print(f"{token.i:2d} {token.text:15s} POS:{token.pos_:8s} DEP:{token.dep_:10s} HEAD:{token.head.i:2d}({token.head.text})")

print("\n\nDependency tree visualization:")
print("-" * 80)
for token in doc:
    if token.dep_ == "ROOT":
        print(f"ROOT: {token.i} - {token.text}")
        for child in token.subtree:
            if child != token:
                print(f"  └─ {child.i} - {child.text} ({child.dep_})")
