import spacy

nlp = spacy.load("en_core_web_sm")
text = "I left because it was late, and I took a taxi when it started raining."

doc = nlp(text)

print("Analysis: What tokens should belong to each clause?\n")
print("Desired output:")
print("1. I left           (tokens 0-1)")
print("2. because it was late (tokens 2-5)")
print("3. and I took a taxi (tokens 7-11 - includes 'and')")
print("4. when it started raining (tokens 12-15)")
print()

print("\nCurrent structure:")
print("'left' (1) is ROOT")
print("  - has child 'was' (4) with dep=advcl")
print("    - 'was' has child 'because' (2) with dep=mark")
print("  - has child 'took' (9) with dep=conj") 
print("    - 'took' has child 'started' (14) with dep=advcl")
print()

print("\nThe issue: When extracting 'left' clause, we're including tokens")
print("0-3 (I left because it), but 'because it was late' should be separate")
print()

print("\nSolution: For each clause, exclude subordinating markers and their clause roots")
print("When 'left' has child 'was' with dep=advcl:")
print("  - Find the mark dependency child of 'was' -> 'because' (2)")
print("  - Start that dependent clause from the mark token, not from after")
print("  - End main clause before the mark token")
