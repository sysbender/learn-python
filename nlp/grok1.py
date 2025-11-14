#!/usr/bin/env python3
"""
Semantic VTT Generator from Whisper JSON

This script converts Whisper JSON transcription output into a semantically
split VTT subtitle file optimized for language learners.

Features:
- Merges consecutive Whisper segments
- Normalizes punctuation
- Splits text into sentences
- Keeps short sentences on one line
- Semantically splits long sentences using spaCy NLP
- Configurable max words per line (default: 10)
- Outputs standard-compliant .vtt file
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
import re
import spacy
from spacy.language import Language
from spacy.tokens import Doc, Token

# Load spaCy model (small English model by default)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Warning: spaCy model 'en_core_web_sm' not found.")
    print("Install with: python -m spacy download en_core_web_sm")
    print("Falling back to basic splitting.")
    nlp = None


class SemanticVTTGenerator:
    def __init__(self, max_words_per_line: int = 10):
        self.max_words_per_line = max_words_per_line
        self.punctuation_pattern = re.compile(r'[.!?]+')
        self.comma_pattern = re.compile(r',\s*')
        self.connection_words = {
            'and', 'but', 'or', 'so', 'because', 'although', 'though',
            'while', 'whereas', 'since', 'unless', 'until', 'after',
            'before', 'if', 'when', 'whenever', 'where', 'wherever'
        }

    def load_whisper_json(self, json_path: str) -> List[Dict[str, Any]]:
        """Load and validate Whisper JSON output."""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle both full transcription and segment list
        if 'segments' in data:
            segments = data['segments']
        elif isinstance(data, list):
            segments = data
        else:
            raise ValueError("Invalid Whisper JSON format: missing 'segments'")

        return segments

    def merge_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge consecutive segments with small gaps into continuous blocks."""
        if not segments:
            return []

        merged = []
        current = segments[0].copy()

        for seg in segments[1:]:
            # If segments are close in time and no major pause
            if (seg['start'] - current['end'] < 0.5 and
                seg.get('no_speech_prob', 1.0) < 0.8):
                # Merge text
                current['text'] += ' ' + seg['text'].strip()
                current['end'] = seg['end']
                # Update words if present
                if 'words' in seg:
                    if 'words' not in current:
                        current['words'] = []
                    current['words'].extend(seg['words'])
            else:
                merged.append(current)
                current = seg.copy()

        merged.append(current)
        return merged

    def normalize_text(self, text: str) -> str:
        """Clean and normalize text with proper punctuation."""
        # Strip whitespace
        text = text.strip()
        # Fix common issues
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'(\w)\s*,\s*(\w)', r'\1, \2', text)
        text = re.sub(r'(\w)\s*\.\s*(\w)', r'\1. \2', text)
        text = re.sub(r'(\w)\s*\?\s*(\w)', r'\1? \2', text)
        text = re.sub(r'(\w)\s*\!\s*(\w)', r'\1! \2', text)

        # Ensure sentence-ending punctuation
        if not text.endswith(('.', '!', '?')):
            # Look for last verb or noun to attach punctuation
            if nlp:
                doc = nlp(text)
                last_token = doc[-1]
                if last_token.pos_ in {'VERB', 'NOUN', 'ADJ', 'ADV'}:
                    text += '.'
                else:
                    text += '.'
            else:
                text += '.'

        return text

    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using spaCy or fallback regex."""
        if nlp:
            doc = nlp(text)
            return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        else:
            # Fallback: split on .!? followed by space and capital letter
            sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
            return [s.strip() for s in sentences if s.strip()]

    def count_words(self, text: str) -> int:
        """Count words in text."""
        return len(text.split())

    def split_semantically(self, sentence: str) -> List[str]:
        """Split long sentence into semantic chunks."""
        words = sentence.split()
        if self.count_words(sentence) <= self.max_words_per_line:
            return [sentence]

        chunks = []
        current_chunk = []
        current_word_count = 0

        if nlp:
            doc = nlp(sentence)
            tokens = list(doc)

            i = 0
            while i < len(tokens):
                token = tokens[i]

                # Add word
                current_chunk.append(token.text_with_ws if token.whitespace_ else token.text)
                current_word_count += 1

                # Check if we need to split
                if current_word_count >= self.max_words_per_line:
                    # Look ahead for good break point
                    break_point = self.find_break_point(tokens, i + 1)
                    if break_point > i:
                        # Split at break point
                        chunk_tokens = tokens[len(current_chunk)-current_word_count:break_point]
                        chunk_text = ''.join([t.text_with_ws if t.whitespace_ else t.text + ' ' 
                                            for t in chunk_tokens]).strip()
                        chunks.append(chunk_text)
                        current_chunk = [t.text_with_ws if t.whitespace_ else t.text + ' ' 
                                       for t in tokens[break_point:i+1]]
                        current_word_count = i + 1 - break_point
                        i = break_point
                    else:
                        # Force split
                        chunk_text = ' '.join(current_chunk).strip()
                        chunks.append(chunk_text)
                        current_chunk = []
                        current_word_count = 0
                i += 1

            if current_chunk:
                chunk_text = ' '.join(current_chunk).strip()
                chunks.append(chunk_text)

        else:
            # Fallback: split on punctuation
            parts = re.split(r'([,;:])\s*', sentence)
            current = ""
            for part in parts:
                if part in ',;:' and current:
                    current += part + " "
                    if self.count_words(current) >= self.max_words_per_line:
                        chunks.append(current.strip())
                        current = ""
                else:
                    temp = current + part
                    if self.count_words(temp) > self.max_words_per_line and current:
                        chunks.append(current.strip())
                        current = part + " "
                    else:
                        current = temp + " "
            if current:
                chunks.append(current.strip())

        # Ensure no chunk exceeds limit
        final_chunks = []
        for chunk in chunks:
            if self.count_words(chunk) > self.max_words_per_line:
                words = chunk.split()
                subchunk = []
                for word in words:
                    subchunk.append(word)
                    if len(subchunk) >= self.max_words_per_line:
                        final_chunks.append(' '.join(subchunk))
                        subchunk = []
                if subchunk:
                    final_chunks.append(' '.join(subchunk))
            else:
                final_chunks.append(chunk)

        return final_chunks

    def find_break_point(self, tokens: List[Token], start_idx: int) -> int:
        """Find best semantic break point after start_idx."""
        # Look for punctuation
        for i in range(start_idx, len(tokens)):
            if tokens[i].text in {',', ';', ':', '.'}:
                return i + 1

        # Look for conjunctions
        for i in range(start_idx, min(start_idx + 5, len(tokens))):
            if tokens[i].lower_ in self.connection_words:
                return i

        # Look for clause boundaries
        for i in range(start_idx, len(tokens)):
            if tokens[i].dep_ in {'cc', 'conj', 'advmod'}:
                return i

        return start_idx

    def format_timestamp(self, seconds: float) -> str:
        """Convert seconds to VTT timestamp format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    def generate_vtt_lines(self, merged_segments: List[Dict[str, Any]]) -> List[Tuple[str, str, str]]:
        """Generate VTT subtitle lines with timestamps and text."""
        vtt_lines = []
        subtitle_index = 1

        for seg in merged_segments:
            start_time = seg['start']
            end_time = seg['end']
            text = self.normalize_text(seg['text'])

            sentences = self.split_into_sentences(text)

            current_time = start_time
            total_duration = end_time - start_time
            total_words = sum(self.count_words(s) for s in sentences)
            time_per_word = total_duration / max(total_words, 1)

            for sentence in sentences:
                word_count = self.count_words(sentence)
                sentence_duration = word_count * time_per_word

                if word_count <= self.max_words_per_line:
                    lines = [sentence]
                else:
                    lines = self.split_semantically(sentence)

                for line in lines:
                    line_start = self.format_timestamp(current_time)
                    line_end = self.format_timestamp(current_time + sentence_duration / len(lines))
                    vtt_lines.append((str(subtitle_index), line_start, line_end, line))
                    subtitle_index += 1
                    current_time += sentence_duration / len(lines)

        return vtt_lines

    def write_vtt(self, vtt_lines: List[Tuple[str, str, str, str]], output_path: str):
        """Write VTT file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for index, start, end, text in vtt_lines:
                f.write(f"{index}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")

    def process(self, json_path: str, output_path: str):
        """Main processing pipeline."""
        print(f"Loading Whisper JSON from: {json_path}")
        segments = self.load_whisper_json(json_path)

        print(f"Merging {len(segments)} segments...")
        merged = self.merge_segments(segments)

        print(f"Generating VTT lines from {len(merged)} merged segments...")
        vtt_lines = self.generate_vtt_lines(merged)

        print(f"Writing {len(vtt_lines)} subtitle lines to: {output_path}")
        self.write_vtt(vtt_lines, output_path)
        print("Done!")


def main():
    parser = argparse.ArgumentParser(description="Generate semantic VTT from Whisper JSON")
    parser.add_argument("input", help="Path to Whisper JSON file")
    parser.add_argument("-o", "--output", help="Output VTT file path")
    parser.add_argument("-w", "--max-words", type=int, default=10,
                        help="Maximum words per subtitle line (default: 10)")
    parser.add_argument("--no-spacy", action="store_true",
                        help="Disable spaCy (use regex fallback)")

    args = parser.parse_args()

    # Set output path
    if args.output:
        output_path = args.output
    else:
        input_path = Path(args.input)
        output_path = input_path.with_suffix('.vtt').name

    # Disable spaCy if requested
    global nlp
    if args.no_spacy:
        nlp = None

    # Run generator
    generator = SemanticVTTGenerator(max_words_per_line=args.max_words)
    generator.process(args.input, output_path)


if __name__ == "__main__":
    main()