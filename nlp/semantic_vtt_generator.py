#!/usr/bin/env python3
"""
Semantic VTT Generator from Whisper JSON
Uses spaCy for intelligent syntactic chunking
"""

import json
import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple

try:
    import spacy
except ImportError:
    print("Error: spaCy is required. Install with: pip install spacy")
    print("Then download models:")
    print("  python -m spacy download fr_core_news_sm")
    print("  python -m spacy download en_core_web_sm")
    exit(1)


class SemanticVTTGenerator:
    # spaCy model names for different languages
    SPACY_MODELS = {
        'fr': 'fr_core_news_sm',
        'en': 'en_core_web_sm'
    }
    
    def __init__(self, max_words: int = 7, min_words: int = 3, 
                 pause_threshold: float = 0.5, language: str = 'fr'):
        self.max_words = max_words
        self.min_words = min_words
        self.pause_threshold = pause_threshold
        self.language = language
        self.nlp = None
        
        # Load spaCy model
        self.load_model(language)
    
    def load_model(self, language: str):
        """Load spaCy model for the specified language"""
        if language not in self.SPACY_MODELS:
            raise ValueError(f"Unsupported language: {language}. Use 'fr' or 'en'")
        
        model_name = self.SPACY_MODELS[language]
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            print(f"Error: spaCy model '{model_name}' not found.")
            print(f"Install with: python -m spacy download {model_name}")
            exit(1)
    
    def format_timestamp(self, seconds: float) -> str:
        """Convert seconds to VTT timestamp format (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millisecs:03d}"
    
    def extract_words(self, data: Dict) -> List[Dict]:
        """Extract all words with timestamps from Whisper JSON"""
        all_words = []
        
        if 'segments' not in data:
            raise ValueError("Invalid JSON: missing 'segments' key")
        
        for segment in data['segments']:
            if 'words' in segment and isinstance(segment['words'], list):
                for word in segment['words']:
                    if 'text' in word and 'start' in word and 'end' in word:
                        all_words.append({
                            'text': word['text'].strip(),
                            'start': word['start'],
                            'end': word['end']
                        })
        
        if not all_words:
            raise ValueError("No words with timestamps found in JSON")
        
        return all_words
    
    def is_clause_boundary(self, token, next_token=None) -> bool:
        """Check if this token marks a clause boundary using spaCy"""
        # Strong punctuation always breaks
        if token.text in '.!?':
            return True
        
        # Comma with sufficient context
        if token.text == ',' and token.i > 2:
            return True
        
        # Coordinating conjunctions at clause level
        if token.dep_ == 'cc' and token.head.pos_ == 'VERB':
            return True
        
        # Subordinating conjunctions
        if token.dep_ == 'mark':
            return True
        
        # Relative pronouns starting clauses
        if token.pos_ == 'PRON' and token.dep_ in ['nsubj', 'obj'] and token.head.pos_ == 'VERB':
            return True
        
        return False
    
    def is_phrase_boundary(self, token, next_token=None) -> bool:
        """Check if this is a natural phrase boundary"""
        # After prepositional phrases (but only if phrase is complete)
        if token.dep_ == 'pobj' and token.head.pos_ == 'ADP':
            return True
        
        # After complete noun phrases
        if token.pos_ in ['NOUN', 'PROPN'] and token.dep_ in ['dobj', 'pobj', 'nsubj']:
            # Check if next token starts new phrase
            if next_token and next_token.pos_ in ['VERB', 'ADP', 'SCONJ', 'CCONJ']:
                return True
        
        # Weak punctuation in right context
        if token.text in ',;:':
            return True
        
        return False
    
    def should_break_here(self, tokens: List, current_idx: int, 
                         current_length: int, time_diff: float) -> bool:
        """Determine if we should break at this position"""
        token = tokens[current_idx]
        next_token = tokens[current_idx + 1] if current_idx + 1 < len(tokens) else None
        
        # Never break if too short
        if current_length < self.min_words:
            # Exception: strong punctuation
            if token.text in '.!?':
                return True
            return False
        
        # Always break if too long
        if current_length >= self.max_words:
            return True
        
        # Break on long pauses
        if time_diff > self.pause_threshold:
            return True
        
        # Check for clause boundary
        if self.is_clause_boundary(token, next_token):
            return True
        
        # Check for phrase boundary if we're at comfortable length
        if current_length >= self.min_words + 2:
            if self.is_phrase_boundary(token, next_token):
                return True
        
        return False
    
    def create_chunks(self, words: List[Dict]) -> List[Dict]:
        """Split words into semantic chunks using spaCy"""
        if not words:
            return []
        
        # Reconstruct text and create mapping
        text_parts = []
        word_map = []  # Maps character position to word index
        
        for i, word in enumerate(words):
            start_char = len(' '.join(text_parts))
            if text_parts:
                start_char += 1  # Add space
            text_parts.append(word['text'])
            word_map.append({
                'word_idx': i,
                'char_start': start_char,
                'char_end': start_char + len(word['text'])
            })
        
        full_text = ' '.join(text_parts)
        
        # Parse with spaCy
        doc = self.nlp(full_text)
        
        # Map tokens back to words
        token_to_word = []
        for token in doc:
            # Find which word this token belongs to
            for wm in word_map:
                if wm['char_start'] <= token.idx < wm['char_end']:
                    token_to_word.append({
                        'token': token,
                        'word_idx': wm['word_idx'],
                        'word': words[wm['word_idx']]
                    })
                    break
        
        # Create chunks based on syntactic analysis
        chunks = []
        current_chunk = {
            'words': [],
            'start': words[0]['start'],
            'end': words[0]['end']
        }
        
        for i, tw in enumerate(token_to_word):
            word_idx = tw['word_idx']
            word = tw['word']
            token = tw['token']
            
            # Get time difference to next word
            next_word = words[word_idx + 1] if word_idx + 1 < len(words) else None
            time_diff = next_word['start'] - word['end'] if next_word else 0
            
            # Add word to current chunk
            current_chunk['words'].append(word['text'])
            current_chunk['end'] = word['end']
            
            # Get next token
            next_token = token_to_word[i + 1]['token'] if i + 1 < len(token_to_word) else None
            
            # Check if we should break
            is_last = word_idx == len(words) - 1
            if is_last or self.should_break_here(
                [tw['token'] for tw in token_to_word],
                i,
                len(current_chunk['words']),
                time_diff
            ):
                # Save current chunk
                chunks.append({
                    'text': ' '.join(current_chunk['words']),
                    'start': current_chunk['start'],
                    'end': current_chunk['end']
                })
                
                # Start new chunk
                if next_word:
                    current_chunk = {
                        'words': [],
                        'start': next_word['start'],
                        'end': next_word['end']
                    }
        
        return chunks
    
    def generate_vtt(self, chunks: List[Dict]) -> str:
        """Generate VTT file content from chunks"""
        vtt_lines = ['WEBVTT\n']
        
        for i, chunk in enumerate(chunks, 1):
            vtt_lines.append(f"{i}")
            start_time = self.format_timestamp(chunk['start'])
            end_time = self.format_timestamp(chunk['end'])
            vtt_lines.append(f"{start_time} --> {end_time}")
            vtt_lines.append(chunk['text'])
            vtt_lines.append('')  # Empty line between cues
        
        return '\n'.join(vtt_lines)
    
    def process_file(self, input_path: str, output_path: str = None):
        """Process a Whisper JSON file and generate VTT"""
        # Read input file
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Detect language from JSON if available
        if 'language' in data:
            detected_lang = data['language']
            if detected_lang in self.SPACY_MODELS and detected_lang != self.language:
                print(f"Detected language: {detected_lang}")
                self.language = detected_lang
                self.load_model(detected_lang)
        
        # Extract words and create chunks
        print("Extracting words...")
        words = self.extract_words(data)
        
        print("Analyzing syntax and creating chunks...")
        chunks = self.create_chunks(words)
        
        # Generate VTT
        vtt_content = self.generate_vtt(chunks)
        
        # Determine output path
        if output_path is None:
            output_path = input_file.with_suffix('.vtt')
        
        # Write output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(vtt_content)
        
        print(f"\n✓ Generated VTT file: {output_path}")
        print(f"  - Language: {self.language}")
        print(f"  - Total chunks: {len(chunks)}")
        print(f"  - Total words: {len(words)}")
        print(f"  - Avg words/chunk: {len(words)/len(chunks):.1f}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate semantic VTT subtitles from Whisper JSON using spaCy',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.json
  %(prog)s input.json -o output.vtt
  %(prog)s input.json -w 8 -m 4 -p 0.6 -l fr
  
Requirements:
  pip install spacy
  python -m spacy download fr_core_news_sm
  python -m spacy download en_core_web_sm
        """
    )
    parser.add_argument(
        'input',
        help='Input Whisper JSON file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output VTT file (default: same name as input with .vtt extension)'
    )
    parser.add_argument(
        '-w', '--max-words',
        type=int,
        default=7,
        help='Maximum words per subtitle line (default: 7)'
    )
    parser.add_argument(
        '-m', '--min-words',
        type=int,
        default=3,
        help='Minimum words per subtitle line (default: 3)'
    )
    parser.add_argument(
        '-p', '--pause-threshold',
        type=float,
        default=0.5,
        help='Pause threshold in seconds for breaking lines (default: 0.5)'
    )
    parser.add_argument(
        '-l', '--language',
        choices=['fr', 'en'],
        default='fr',
        help='Language for spaCy analysis (default: fr, auto-detect from JSON)'
    )
    
    args = parser.parse_args()
    
    try:
        generator = SemanticVTTGenerator(
            max_words=args.max_words,
            min_words=args.min_words,
            pause_threshold=args.pause_threshold,
            language=args.language
        )
        generator.process_file(args.input, args.output)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())