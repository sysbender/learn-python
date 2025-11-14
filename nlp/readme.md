https://github.com/isaacus-dev/semchunk

## requirement
 

**Semantic VTT Generator from Whisper JSON**

**Goal:**
Generate VTT subtitles from Whisper JSON transcriptions, splitting text into short, semantically meaningful lines that are suitable for language learners.

**Features:**

* Limit each subtitle line to a configurable number of words (default: 10).
* Merge consecutive Whisper segments into a continuous timeline.
* Split text into sentences.
* Sentences that do not exceed the word limit (default: 10) are kept on a single VTT line.
* Sentences that exceed the word limit are split semantically so that each line stays within the limit. Semantic splitting is performed using:

  * Punctuation, such as commas.
  * Connection words in complex sentences.
  * Other meaningful natural phrase boundaries, such as part-of-speech boundaries.
* NLP tools like **spaCy** can be used to achieve semantic splitting.
* Output a clean, standard-compliant VTT file.

**Input:**
Whisper JSON transcription containing text and timestamps.
 

 



## short requirement

 

**Semantic VTT Generator from Whisper JSON**

**Goal:**
Transform Whisper JSON transcriptions into clean, learner-friendly VTT subtitles with short, semantically meaningful lines.

**Key Features:**

* Configurable word limit per line (default: 10).
* Merge consecutive Whisper segments into a smooth, continuous timeline.
* Automatically normalize text with proper punctuation.
* Sentence-aware splitting:

  * Short sentences stay on one line.
  * Longer sentences are split semantically at natural boundaries: punctuation, conjunctions, or part-of-speech breaks.
* Leverages NLP tools (e.g., **spaCy**) for intelligent semantic splitting.
* Produces standard-compliant, ready-to-use VTT files.

**Input:**
Whisper JSON containing transcribed text and timestamps.








SOLUTION: EXTRACT + MERGE STRATEGY

Extract syntactic phrases (PP, VP, NP)
Merge adjacent phrases if total ≤ max_words
Only split at safe boundaries (commas, conjunctions)
Never split inside PP



 
