I'll create a comprehensive Python solution using spaCy for clause detection and sentence classification with support for English and French.Now let me create comprehensive pytest unit tests:Now let me create a README with usage examples and setup instructions:Perfect! I've created a comprehensive solution for clause detection and sentence classification. Here's what I've built:

## 📦 **What's Included:**

### 1. **Main Module** (`clause_detector.py`)
- **ClauseDetector**: Uses spaCy's dependency parsing to identify clause boundaries
  - Finds verbal predicates (clause roots)
  - Determines clause spans using subtree traversal
  - Classifies clauses as independent or dependent
  
- **SentenceClassifier**: Analyzes clause structure to classify sentences
  - Counts independent vs. dependent clauses
  - Classifies as: simple, compound, complex, compound-complex, or other

- **Key Features**:
  - ✅ Bilingual support (English & French)
  - ✅ Clean, reusable API with dataclasses
  - ✅ Both class-based and convenience functions
  - ✅ Proper error handling

### 2. **Comprehensive Test Suite** (`test_clause_detector.py`)
- 40+ unit tests covering:
  - English clause detection
  - French clause detection
  - All sentence types
  - Edge cases (empty text, long sentences, punctuation)
  - Batch processing
  - Error handling

### 3. **Documentation** (README)
- Installation instructions
- Usage examples
- API reference
- Best practices

## 🎯 **How It Works:**

The detector uses spaCy's dependency parsing to:
1. Find clause roots (typically verbs with specific dependency relations like ROOT, conj, advcl)
2. Extract full clause spans using token subtrees
3. Classify clauses based on dependency patterns (subordinating markers, conjunctions)
4. Count and categorize to determine sentence type

## 🚀 **Quick Example:**

```python
from clause_detector import classify_sentence

result = classify_sentence(
    "Although it was raining, we went outside, and we had fun.",
    language="en"
)

print(result['sentence_type'].value)  # "compound-complex"
print(result['independent_count'])     # 2
print(result['dependent_count'])       # 1
```

The solution follows Python best practices with type hints, dataclasses, enums, comprehensive docstrings, and is fully testable with pytest!