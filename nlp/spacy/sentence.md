

Here is a clear, compact summary of **English sentence grammar**, organized so you can study or refer to it quickly:

---

# **Summary of English Sentence Grammar**

## **1. Basic Sentence Structure**

A complete English sentence must have:

* **Subject (S)** – who or what the sentence is about
* **Verb (V)** – the action or state
* **Object (O)** – who or what receives the action (optional)

### Common patterns:

* **S + V** → *Birds fly.*
* **S + V + O** → *She reads books.*
* **S + V + Complement** → *They are happy.*
* **S + V + Indirect Object + Direct Object** → *He gave me a gift.*
* **S + V + Object + Complement** → *They elected him president.*

---

## **2. Types of Sentences (by function)**

* **Declarative**: makes a statement
  *I like music.*
* **Interrogative**: asks a question
  *Do you like music?*
* **Imperative**: gives a command
  *Close the door.*
* **Exclamatory**: expresses strong emotion
  *What a beautiful day!*

---

## **3. Sentence Components**

### **A. Subjects**

* Can be **nouns**, **pronouns**, **gerunds**, **infinitives**, or **clauses**
  *Swimming is fun.*
  *What he said surprised me.*

### **B. Verbs**

* **Action verbs**: *run, eat, think*
* **Linking verbs**: *be, seem, become*
* **Auxiliary verbs**: *be, have, do, will, can…*

### **C. Objects & Complements**

* **Direct object**: receives the action
* **Indirect object**: benefits from the action
* **Subject complement**: renames or describes the subject
* **Object complement**: describes/renames the object

---

## **4. Clauses**

### **Independent clause**

* Can stand alone as a sentence
  *I left.*

### **Dependent (subordinate) clause**

* Cannot stand alone; starts with subordinators:
  **because, although, when, if, that, who, which…**
  *Because I was tired…*

### **Types of dependent clauses**

* **Noun clause**: *I know that he is right.*
* **Adjective (relative) clause**: *The man who called is my friend.*
* **Adverb clause**: *I left because it was late.*

---

## **5. Phrases**

Groups of words without a full subject-verb pair:

* **Noun phrase** → *the tall man*
* **Verb phrase** → *was eating*
* **Prepositional phrase** → *in the room*
* **Gerund phrase** → *Swimming in the lake*
* **Infinitive phrase** → *to learn English*

---

## **6. Sentence Types (by structure)**

1. **Simple sentence**
   *She reads every day.*
2. **Compound sentence** (IC + IC, joined by **and, but, or, so, yet** or a semicolon)
   *I wanted to leave, but it started raining.*
3. **Complex sentence** (IC + DC)
   *I left because it was late.*
4. **Compound-complex sentence**
   *I left because it was late, and I took a taxi.*

---

## **7. Word Order**

English has a fairly fixed word order:

### **Affirmative: S + V + O**

*She eats apples.*

### **Questions**

* Auxiliary + Subject + Verb
  *Do you like it?*

### **Adjective order (typical)**

Opinion → Size → Age → Shape → Color → Origin → Material → Noun
*beautiful small old round white Italian marble table*

---

## **8. Tense & Aspect (very short overview)**

English has:

* **3 times**: past, present, future
* **4 aspects**: simple, continuous, perfect, perfect continuous

Examples:

* **Simple**: I eat. / I ate.
* **Continuous**: I am eating.
* **Perfect**: I have eaten.
* **Perfect continuous**: I have been eating.

---

If you want, I can also create:

* a **visual chart**,
* a **beginner-friendly version**,
* a **full detailed grammar outline**, or
* practice exercises.


## requirement

implement the following function with python and spacy,  
following the best practice, 
make them reusable, better support both english and french , 
and include pytest unit test.

1. The clause detection function
uses spaCy’s dependency parse
finds clause boundary
extracts full clause spans/text 
returns clean clauses  

2. The sentence type classifier
counts independent vs. dependent clauses
classify the sentence as simple, compound, complex, or compound-complex or other