import spacy

nlp = spacy.load("en_core_web_sm")
text = "I left because it was late, and I took a taxi when it started raining."

doc = nlp(text)

print("Detailed analysis of each potential clause root:\n")

roots_to_check = []
for token in doc:
    is_verb = token.pos_ in ("VERB", "AUX") or (token.tag_ and token.tag_.startswith("V"))
    if token.dep_ == "ROOT" or (token.dep_ in {'mark', 'advcl', 'acl', 'ccomp', 'xcomp', 'relcl', 'conj'} and is_verb):
        roots_to_check.append(token)

for root in roots_to_check:
    print(f"\nRoot: {root.i} - '{root.text}' (dep={root.dep_}, pos={root.pos_})")
    
    # Get the subtree
    descendants = list(root.subtree)
    span_start = min(d.i for d in descendants)
    span_end = max(d.i for d in descendants) + 1
    
    print(f"  Subtree span: [{span_start}, {span_end}] = '{doc[span_start:span_end].text}'")
    print(f"  Subtree tokens:")
    for d in descendants:
        print(f"    {d.i}: {d.text} (dep={d.dep_})")
    
    # Find children with subordinating deps
    print(f"  Direct children with clause deps:")
    for child in root.children:
        if child.dep_ in {'mark', 'advcl', 'acl', 'ccomp', 'xcomp', 'relcl', 'conj'}:
            print(f"    {child.i}: {child.text} (dep={child.dep_})")
