from clause_detector import detect_clauses

# Test case 1: Your original example
text1 = "I left because it was late, and I took a taxi when it started raining."
clauses1 = detect_clauses(text1)
print("Test 1: Original example")
print(f"Text: {text1}")
print(f"Clauses ({len(clauses1)}):")
for i, c in enumerate(clauses1, 1):
    print(f"  {i}. {c.text}")
print()

# Test case 2: Simple sentence
text2 = "I went home."
clauses2 = detect_clauses(text2)
print("Test 2: Simple sentence")
print(f"Text: {text2}")
print(f"Clauses ({len(clauses2)}):")
for i, c in enumerate(clauses2, 1):
    print(f"  {i}. {c.text}")
print()

# Test case 3: Only dependent clause
text3 = "Although it was cold, we played outside."
clauses3 = detect_clauses(text3)
print("Test 3: Dependent clause first")
print(f"Text: {text3}")
print(f"Clauses ({len(clauses3)}):")
for i, c in enumerate(clauses3, 1):
    print(f"  {i}. {c.text}")
print()

# Test case 4: Multiple coordinated clauses
text4 = "I ran, she walked, and he drove."
clauses4 = detect_clauses(text4)
print("Test 4: Multiple coordinated clauses")
print(f"Text: {text4}")
print(f"Clauses ({len(clauses4)}):")
for i, c in enumerate(clauses4, 1):
    print(f"  {i}. {c.text}")
print()

# Test case 5: Nested subordinate clauses
text5 = "I know that she left because it was late."
clauses5 = detect_clauses(text5)
print("Test 5: Nested subordinate clauses")
print(f"Text: {text5}")
print(f"Clauses ({len(clauses5)}):")
for i, c in enumerate(clauses5, 1):
    print(f"  {i}. {c.text}")
