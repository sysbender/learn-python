import spacy
from clause_detector import ClauseDetector

nlp = spacy.load("en_core_web_sm")
text = "I left because it was late, and I took a taxi when it started raining."

detector = ClauseDetector(language="en")
doc = detector.nlp(text)

root = doc[9]  # 'took'
all_roots = detector._find_clause_roots(doc)

print(f"Root: {root.i} - '{root.text}' (dep={root.dep_})")
print(f"All clause roots: {[r.i for r in all_roots]}")
print()

# Call the function to see what it does
start, end = detector._get_clause_start_end_excluding_children(root, doc, all_roots)
print(f"Result: start={start}, end={end}")
print(f"Span text: '{doc[start:end].text}'")
