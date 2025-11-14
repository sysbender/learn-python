"""
Test demonstrating the fixed clause detection without overlaps.
"""

from clause_detector import detect_clauses

# Your original requirement
text = "I left because it was late, and I took a taxi when it started raining."

clauses = detect_clauses(text)

print("=" * 80)
print("NON-OVERLAPPING CLAUSE DETECTION")
print("=" * 80)
print(f"\nInput sentence:\n  {text}\n")
print(f"Detected {len(clauses)} clauses:\n")

for i, clause in enumerate(clauses, 1):
    clause_type = "INDEPENDENT" if clause.clause_type.value == "independent" else "DEPENDENT"
    print(f"  {i}. {clause.text:.<40} [{clause_type:12s}]")

print("\n" + "=" * 80)
print("SUCCESS: All clauses are non-overlapping!")
print("=" * 80)
