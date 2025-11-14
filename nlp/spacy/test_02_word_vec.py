

import spacy
import numpy as np


nlp = spacy.load('en_core_web_lg')
#print(nlp.lang)
 
with open('data/wiki_us.txt', 'r') as f: 
    text = f.read()

doc = nlp(text)
sentences = (list(doc.sents))
s1 = sentences[0]
print(s1)

your_word ='country'
ms = nlp.vocab.vectors.most_similar(
    np.asarray([nlp.vocab.vectors[nlp.vocab.strings[your_word]]]), n=10)
words = [nlp.vocab.strings[w] for w in ms[0][0]]
distances = ms[2]
print(words)