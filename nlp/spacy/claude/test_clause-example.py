from clause_detector import detect_clauses, classify_sentence

def test_Quick_Start():
    # Detect clauses in a sentence
    text = "Although it was raining, we went outside, and we had fun."
    clauses = detect_clauses(text, language="en")

    for clause in clauses:
        print(f"{clause.clause_type.value}: {clause.text}")


    print('================')
    # Classify a sentence
    result = classify_sentence(text, language="en")
    print(f"Sentence type: {result['sentence_type'].value}")
    print(f"Independent clauses: {result['independent_count']}")
    print(f"Dependent clauses: {result['dependent_count']}")


def test_english():
    text ="I left because it was late, and I took a taxi when it started raining."
    clauses = detect_clauses(text, language='en')
    for clause in clauses:
        print(clause)

        
from clause_detector import ClauseDetector, SentenceClassifier

def test_Using_Classes_Directly():
    # Create detector for English
    detector = ClauseDetector(language="en")
    classifier = SentenceClassifier(detector)

    # Detect clauses
    clauses = detector.detect_clauses("I think that she is right.")

    # Classify sentence
    result = classifier.classify("I think that she is right.")
    print(result['sentence_type'].value)  # "complex"

def test_french():
    from clause_detector import detect_clauses, classify_sentence

    # French clause detection
    text = "Bien qu'il pleuve, nous sortons."
    clauses = detect_clauses(text, language="fr")

    # French sentence classification
    result = classify_sentence(
        "Je lis et elle écrit.", 
        language="fr"
    )
    print(result['sentence_type'].value)  # "compound"


def test_batch_processing():
    from clause_detector import ClauseDetector, SentenceClassifier

    detector = ClauseDetector(language="en")
    classifier = SentenceClassifier(detector)

    sentences = [
        "The cat sleeps.",
        "I read, and she writes.",
        "When it rains, I stay inside."
    ]

    results = classifier.classify_batch(sentences)

    for sent, result in zip(sentences, results):
        print(f"{sent}")
        print(f"  Type: {result['sentence_type'].value}")
        print(f"  Independent: {result['independent_count']}, "
            f"Dependent: {result['dependent_count']}")