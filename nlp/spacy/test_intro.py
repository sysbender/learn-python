
import spacy

nlp = spacy.load('en_core_web_sm')
print(nlp.lang)
 

 # container  - doc < sent < token > span > spanGroups

with open('data/wiki_us.txt', 'r') as f:
    text = f.read()    
    for token in text[0:10]:
        print(token)

doc =  nlp(text)
for t in doc[:10]:
    print(t)

# SBD - sendtence boundary detection 
sentences = list(doc.sents)
for sent in sentences[:5]:
    print(sent)

# teken attributes

'''
text	The token’s exact text.	"London"
.head	The syntactic head (word it depends on).	"visited" is head of "London" in “I visited London.”
.left_edge	Leftmost token in the phrase the token is part of.	Start of the subtree.
.right_edge	Rightmost token in the phrase.	End of the subtree.
.ent_type_	Named entity type (e.g. GPE, PERSON).	"London".ent_type_ → 'GPE'
.iob_	Entity position: Begin, Inside, or Outside entity.	"B" for first token in entity.
.lemma_	Base/root form of the word.	"running" → "run"
.morph	Morphological features (grammatical details).	`NounType=Prop
.pos_	Part of speech (coarse tag).	"PROPN", "VERB", "NOUN"
.dep_	Dependency relation to head.	"nsubj", "dobj", "prep"
.lang_	Detected language of token.	"en"
'''

# GPE - geo politicol entity
t2=  sentences[0][2]
print(t2 , f"{t2.text=}" , f"{t2.head=}"  )
print(f"{t2.left_edge=}")
print(f"{t2.right_edge=}")
print(f"{t2.ent_type_=}")
print(f"{t2.ent_iob_}")
print(f"{t2.lemma_=}")
print(f"{t2.morph=}")

print(f"{t2.pos_=}")
print(f"{t2.dep_=}")
print(f"{t2.lang_=}")

# part of speech

text = "Mike enjoys playing football"
doc2 = nlp(text)
for token in doc2:
    print(token.text, token.pos_, token.dep_)

from spacy import displacy
displacy.render(doc2, style="dep")

for ent in doc.ents:
    print(ent.text, ent.label_)
    