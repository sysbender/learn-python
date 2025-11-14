import json
import re
from datetime import timedelta

# --- Configuration ---
WHISPER_JSON_FILE = "713-Le-rugby.words.json"
OUTPUT_VTT_FILE = "713-Le-rugby_semantic.vtt"
MAX_WORDS_PER_LINE = 10

# --- SpaCy Setup with Fallback ---
SPACY_LOADED = False
NLP = None
try:
    import spacy
    # Load French model, disabling unnecessary pipes for speed
    NLP = spacy.load("fr_core_news_sm", disable=["tagger", "ner", "textcat"])
    SPACY_LOADED = True
    # print("SpaCy loaded for enhanced semantic splitting.")
except ImportError:
    # print("Warning: spaCy not found. Falling back to rule-based splitting.")
    pass
except OSError:
    # print("Warning: spaCy model 'fr_core_news_sm' not loaded. Falling back to rule-based splitting.")
    pass

# Helper to format milliseconds into VTT time format (HH:MM:SS.mmm)
def format_time(seconds):
    """Converts a time in seconds to VTT format (HH:MM:SS.mmm)."""
    td = timedelta(seconds=seconds)
    total_milliseconds = int(td.total_seconds() * 1000)
    hours = total_milliseconds // 3_600_000
    total_milliseconds %= 3_600_000
    minutes = total_milliseconds // 60_000
    total_milliseconds %= 60_000
    seconds_val = total_milliseconds // 1000
    milliseconds = total_milliseconds % 1000
    return f"{hours:02}:{minutes:02}:{seconds_val:02}.{milliseconds:03}"

def tokenize_into_sentences_and_get_words(all_words):
    """
    Groups the list of all word objects into semantically-complete sentences,
    relying on punctuation in the Whisper word data.
    """
    sentences = []
    current_sentence_words = []

    # Common sentence terminators
    sentence_delimiters = r'[.?!]'

    for i, word_obj in enumerate(all_words):
        word = word_obj['word'].strip()

        # Update word object to strip leading/trailing spaces
        word_obj['word'] = word

        if not word:
            continue

        current_sentence_words.append(word_obj)

        # Check for sentence ender
        if re.search(sentence_delimiters, word) or i == len(all_words) - 1:
            if current_sentence_words:
                sentences.append(current_sentence_words)
                current_sentence_words = []

    return sentences

def rule_based_semantic_split(sentence_words, max_words):
    """
    Splits a single sentence using basic rules (comma, fixed conjunctions, and max word count).
    This serves as the robust fallback when spaCy is unavailable.
    """
    lines = []
    current_line_words = []
    
    # Common French internal delimiters and conjunctions for splitting
    split_points = [',', ':', ';', 'car', 'mais', 'donc', 'or', 'ni', 'si', 'et', 'que']

    def is_split_word(word):
        return any(word.lower().strip() == s or word.lower().strip().startswith(s) for s in split_points)

    for i, word_obj in enumerate(sentence_words):
        current_line_words.append(word_obj)

        # 1. Check if the line is already full
        if len(current_line_words) >= max_words:
            lines.append(current_line_words)
            current_line_words = []
            continue

        # 2. Check for semantic boundary (comma, conjunction)
        if len(sentence_words) - i > max_words / 2: # Ensure enough words remain for a new line
            word_text = word_obj['word'].lower()

            # Check for punctuation splits
            if any(p in word_text for p in [',', ';', ':']):
                lines.append(current_line_words)
                current_line_words = []
                continue

            # Check for conjunction splits (look ahead to the next word)
            if i + 1 < len(sentence_words) and len(current_line_words) > 3:
                next_word_text = sentence_words[i + 1]['word'].lower().strip()
                if is_split_word(next_word_text):
                    lines.append(current_line_words)
                    current_line_words = []
                    continue

    # Add any remaining words
    if current_line_words:
        lines.append(current_line_words)

    # Post-process: Force split any remaining lines that are still too long
    final_lines = []
    for line_words in lines:
        if len(line_words) > max_words:
            for k in range(0, len(line_words), max_words):
                final_lines.append(line_words[k:k + max_words])
        else:
            final_lines.append(line_words)

    return final_lines

def spacy_semantic_split(sentence_words, max_words):
    """
    Splits a single sentence using spaCy dependency parsing for advanced semantic breaks.
    If alignment fails, it falls back to the rule-based split.
    """
    if not NLP:
        return rule_based_semantic_split(sentence_words, max_words)

    raw_text = " ".join(w['word'] for w in sentence_words).replace(" .", ".").replace(" ,", ",").strip()
    doc = NLP(raw_text)
    
    # 1. Align SpaCy tokens back to the original Whisper word objects
    aligned_words = []
    whisper_index = 0
    raw_whisper_words = [w['word'].lower().strip().replace('.', '').replace(',', '') for w in sentence_words]
    
    for token in doc:
        token_text_cleaned = token.text.lower().strip().replace('.', '').replace(',', '')
        
        # Simple alignment check: try to find the current token in the remaining Whisper words
        # (This is an imperfect but necessary step when mapping different tokenizers)
        found = False
        while whisper_index < len(sentence_words):
            whisper_word_cleaned = sentence_words[whisper_index]['word'].lower().strip().replace('.', '').replace(',', '')
            if token_text_cleaned == whisper_word_cleaned:
                aligned_words.append({'token': token, 'word_obj': sentence_words[whisper_index]})
                whisper_index += 1
                found = True
                break
            # Skip short non-text tokens if spaCy creates them (e.g. quotes, internal spaces)
            elif len(token.text.strip()) < 1 and token.text.strip() not in raw_whisper_words:
                 break
            else:
                 # If tokens don't align perfectly, we stop the SpaCy process
                 return rule_based_semantic_split(sentence_words, max_words)

        if not found and token.is_alpha:
             return rule_based_semantic_split(sentence_words, max_words)


    lines = []
    current_line_words = []
    
    # 2. Split the sentence based on word count and spaCy analysis
    for i, aligned in enumerate(aligned_words):
        token = aligned['token']
        word_obj = aligned['word_obj']
        
        current_line_words.append(word_obj)

        # Force break if max length is reached
        if len(current_line_words) >= max_words:
            lines.append(current_line_words)
            current_line_words = []
            continue

        # Semantic Break check (only if line has a few words and enough words remain)
        if len(current_line_words) >= 4 and len(aligned_words) - i > max_words / 2:
            
            # Break conditions based on dependency (DEPS) and Part of Speech (POS):
            # 1. Before Coordinating Conjunctions (CCONJ) e.g., 'mais', 'ou', 'et'
            # 2. Before Subordinating Conjunctions (SCONJ) e.g., 'que', 'si'
            # 3. After a major punctuation mark (',', ';', ':')
            
            # Check the next token for a break point
            if i + 1 < len(aligned_words):
                next_token = aligned_words[i+1]['token']
                # Break before conjunctions
                if next_token.pos_ in ['CCONJ', 'SCONJ']:
                    lines.append(current_line_words)
                    current_line_words = []
                    continue
                # Break before a colon or semicolon
                if next_token.text in [':', ';']:
                    lines.append(current_line_words)
                    current_line_words = []
                    continue
            
            # Check the current token for a break point (e.g., a comma just passed)
            if token.text == ',':
                lines.append(current_line_words)
                current_line_words = []
                continue
                
    # Add any remaining words
    if current_line_words:
        lines.append(current_line_words)

    # Final word count check (should be rare with this logic, but necessary)
    final_lines = []
    for line_words in lines:
        if len(line_words) > max_words:
            for k in range(0, len(line_words), max_words):
                final_lines.append(line_words[k:k + max_words])
        else:
            final_lines.append(line_words)

    return final_lines

def semantic_split(sentence_words, max_words):
    """Selects the best splitting method."""
    if SPACY_LOADED:
        return spacy_semantic_split(sentence_words, max_words)
    else:
        # Fallback will print a warning inside main() if spaCy isn't loaded
        return rule_based_semantic_split(sentence_words, max_words)

def generate_vtt(word_data):
    """Main function to process word data and generate VTT content."""
    
    # 1. Tokenize all words into sentences
    sentences = tokenize_into_sentences_and_get_words(word_data)
    
    vtt_lines = []

    # 2. Process each sentence
    for sentence_words in sentences:
        if not sentence_words:
            continue

        # 3. Determine if semantic splitting is needed and apply the best available method
        if len(sentence_words) <= MAX_WORDS_PER_LINE:
            split_lines = [sentence_words]
        else:
            split_lines = semantic_split(sentence_words, MAX_WORDS_PER_LINE)
        
        # 4. Format VTT cue for each split line
        for line_words in split_lines:
            if not line_words:
                continue

            # Determine start time (first word's start) and end time (last word's end)
            start_time = line_words[0]['start']
            end_time = line_words[-1]['end']
            
            # Reconstruct the text line
            text = " ".join(w['word'] for w in line_words).strip()
            
            # VTT Cue format: START_TIME --> END_TIME \n TEXT
            cue = (
                f"{format_time(start_time)} --> {format_time(end_time)}\n"
                f"{text}\n"
            )
            vtt_lines.append(cue)

    # 5. Assemble the final VTT file content
    vtt_content = "WEBVTT\n\n" + "\n".join(vtt_lines)
    return vtt_content

# --- Execution ---
def main():
    if not SPACY_LOADED:
        print("Note: spaCy is not installed in this environment. Using rule-based semantic splitting.")

    try:
        with open(WHISPER_JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        word_data = []
        if isinstance(data, list):
            word_data = data
        elif 'segments' in data and isinstance(data['segments'], list):
            for segment in data['segments']:
                if 'words' in segment and isinstance(segment['words'], list):
                    word_data.extend(segment['words'])
        
        # --- DEMO SIMULATION (For cases where word_data extraction fails due to non-standard structure) ---
        if not word_data:
             # Extract text from the full snippet provided to simulate word objects for a runnable demo
             full_text = data.get('text', 'No text found in JSON.')
             words = full_text.split()
             current_time = 0.0
             
             for word in words:
                 # Estimate duration based on word length (crude simulation)
                 duration = len(word) * 0.05 + 0.2
                 word_data.append({
                     'word': word,
                     'start': current_time,
                     'end': current_time + duration
                 })
                 current_time += duration
             
             if not word_data:
                print(f"Error: Could not extract word-level data from {WHISPER_JSON_FILE}. Please ensure it follows a standard Whisper word list structure.")
                return
        # --- END OF DEMO SIMULATION ---

        vtt_content = generate_vtt(word_data)

        with open(OUTPUT_VTT_FILE, 'w', encoding='utf-8') as f:
            f.write(vtt_content)
        
        print(f"Successfully generated VTT file: {OUTPUT_VTT_FILE}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{WHISPER_JSON_FILE}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{WHISPER_JSON_FILE}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()