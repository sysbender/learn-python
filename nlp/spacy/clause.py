import spacy
from spacy.tokens import Span

nlp = spacy.load("en_core_web_trf")

CLAUSE_DEPS = {"advcl", "ccomp", "xcomp", "relcl", "acl", "parataxis"}
COORDINATING_DEPS = {"conj"}
SUBORDINATORS = {"SCONJ"}

def get_clause_span(token):
    """Return the full span of a clause headed by token."""
    subtree = list(token.subtree)
    return (subtree[0].i, subtree[-1].i)


def detect_clauses(doc):
    clause_spans = []

    for token in doc:
        # ROOT clause (main clause)
        if token.dep_ == "ROOT" and token.pos_ == "VERB":
            clause_spans.append(get_clause_span(token))

        # Dependent clauses
        if token.dep_ in CLAUSE_DEPS:
            clause_spans.append(get_clause_span(token))

        # Coordinated clauses: "and I took..."
        if token.dep_ == "conj" and token.pos_ == "VERB":
            clause_spans.append(get_clause_span(token))

    # Merge and clean spans
    merged = []
    for start, end in sorted(clause_spans):
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)

    clauses = [doc[s:e+1] for s, e in merged]
    return clauses


# Test
text = "I left because it was late, and I took a taxi when it started raining."
doc = nlp(text)
clauses = detect_clauses(doc)

for i, c in enumerate(clauses, 1):
    print(f"Clause {i}: {c.text}")
