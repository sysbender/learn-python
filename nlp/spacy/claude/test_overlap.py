from clause_detector import detect_clauses

text = "I left because it was late, and I took a taxi when it started raining."

clauses = detect_clauses(text)

print(f"Total clauses: {len(clauses)}\n")
for i, clause in enumerate(clauses):
    print(f"Clause {i+1}:")
    print(f"  Text: {clause.text}")
    print(f"  Type: {clause.clause_type.value}")
    print(f"  Span: [{clause.start}, {clause.end}]")
    print()
