"""
Debug script to analyze French clause detection.
Run this to see the dependency parsing details for French sentences.
"""

import spacy
from clause_detector import ClauseDetector

def debug_sentence(text, language="fr"):
    """Debug a sentence by showing its dependency parse."""
    print(f"\n{'='*80}")
    print(f"Analyzing: {text}")
    print(f"Language: {language}")
    print(f"{'='*80}")
    
    # Load model and parse
    try:
        nlp = spacy.load("fr_core_news_sm" if language == "fr" else "en_core_web_sm")
    except OSError:
        print(f"Model not found for {language}")
        return
    
    doc = nlp(text)
    
    # Show token details
    print("\nToken Analysis:")
    print(f"{'Token':<15} {'POS':<10} {'Tag':<10} {'Dep':<15} {'Head':<15}")
    print("-" * 80)
    for token in doc:
        print(f"{token.text:<15} {token.pos_:<10} {token.tag_:<10} {token.dep_:<15} {token.head.text:<15}")
    
    # Try clause detection
    print("\nClause Detection:")
    detector = ClauseDetector(language=language)
    clauses = detector.detect_clauses(text)
    
    if clauses:
        print(f"Found {len(clauses)} clause(s):")
        for i, clause in enumerate(clauses, 1):
            print(f"  {i}. [{clause.clause_type.value}] {clause.text}")
            if clause.root_token:
                print(f"     Root: {clause.root_token.text} (pos={clause.root_token.pos_}, dep={clause.root_token.dep_})")
    else:
        print("No clauses detected!")
        print("\nLooking for ROOT tokens...")
        roots = [t for t in doc if t.dep_ == "ROOT"]
        if roots:
            for root in roots:
                print(f"  Found ROOT: {root.text} (pos={root.pos_}, tag={root.tag_})")
        else:
            print("  No ROOT tokens found!")


if __name__ == "__main__":
    # Test French sentences
    french_sentences = [
        "Le chat dort.",
        "Je suis allé au magasin et elle est rentrée.",
        "Bien qu'il pleuve, nous sortons.",
        "Le livre que j'ai lu était intéressant.",
        "Je pense qu'elle a raison."
    ]
    
    print("\n" + "="*80)
    print("FRENCH SENTENCE ANALYSIS")
    print("="*80)
    
    for sentence in french_sentences:
        debug_sentence(sentence, language="fr")
    
    # Compare with English
    print("\n\n" + "="*80)
    print("ENGLISH COMPARISON")
    print("="*80)
    
    english_sentences = [
        "The cat sleeps.",
        "I went to the store and she went home.",
        "Although it rains, we go outside."
    ]
    
    for sentence in english_sentences:
        debug_sentence(sentence, language="en")