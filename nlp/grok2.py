#!/usr/bin/env python3
"""
Semantic VTT Generator using semchunk (No spaCy, No Text Normalization)

Converts Whisper JSON to VTT with short, semantically meaningful lines.
Uses semchunk for fast, accurate sentence/phrase splitting.
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
import semchunk


#!/usr/bin/env python3
# … (all previous imports + semchunk) …

class SemanticVTTGenerator:
    def __init__(self, max_words_per_line: int = 10):
        self.max_words_per_line = max_words_per_line
        self.token_counter = lambda t: len(t.split())
        self.chunker = semchunk.chunkerify(self.token_counter,
                                          chunk_size=max_words_per_line)

        # ---- NEW: French prepositions -------------------------------------------------
        self._FRENCH_PREPOSITIONS = {
            "à", "après", "avant", "avec", "chez", "contre", "dans", "de",
            "depuis", "derrière", "devant", "durant", "en", "entre",
            "hors", "jusque", "par", "pendant", "pour", "sans", "sous",
            "sur", "vers", "voici", "voilà"
        }

    # ---- NEW helper ---------------------------------------------------------------
    def _is_preposition(self, word: str) -> bool:
        return word.lower().rstrip(".,;:!?") in self._FRENCH_PREPOSITIONS

    # ---- REPLACED split_into_lines ------------------------------------------------
    def split_into_lines(self, text: str) -> List[str]:
        if not text.strip():
            return []

        raw_chunks = self.chunker(text)
        chunks = [c.strip() for c in raw_chunks if c.strip()]
        if len(chunks) <= 1:
            return chunks

        merged: List[str] = []
        i = 0
        while i < len(chunks):
            cur = chunks[i]
            if i + 1 < len(chunks):
                nxt = chunks[i + 1]
                first = nxt.split()[0] if nxt.split() else ""
                if self._is_preposition(first):
                    candidate = f"{cur} {nxt}"
                    if self.token_counter(candidate) <= self.max_words_per_line:
                        merged.append(candidate)
                        i += 2
                        continue
            merged.append(cur)
            i += 1
        return merged

    # … (the rest of the class – generate_vtt_lines, write_vtt, process – unchanged) …

    def format_timestamp(self, seconds: float) -> str:
        """Convert seconds to VTT timestamp: HH:MM:SS.mmm"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    def generate_vtt_lines(self, merged_segments: List[Dict[str, Any]]) -> List[Tuple[str, str, str, str]]:
        """Generate VTT entries with proper timing."""
        vtt_lines = []
        subtitle_index = 1

        for seg in merged_segments:
            start = seg['start']
            end = seg['end']
            text = seg['text']  # No normalization

            lines = self.split_into_lines(text)
            if not lines:
                continue

            total_duration = end - start
            total_words = sum(len(line.split()) for line in lines)
            if total_words == 0:
                continue
            time_per_word = total_duration / total_words

            current_time = start
            words_in_segment = [len(line.split()) for line in lines]

            for i, (line, word_count) in enumerate(zip(lines, words_in_segment)):
                line_duration = word_count * time_per_word
                line_start = self.format_timestamp(current_time)
                line_end = self.format_timestamp(current_time + line_duration)

                vtt_lines.append((
                    str(subtitle_index),
                    line_start,
                    line_end,
                    line
                ))
                subtitle_index += 1
                current_time += line_duration

        return vtt_lines

    def write_vtt(self, vtt_lines: List[Tuple[str, str, str, str]], output_path: str):
        """Write standard-compliant VTT file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for idx, start, end, text in vtt_lines:
                f.write(f"{idx}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")

    def process(self, json_path: str, output_path: str):
        """Main pipeline."""
        print(f"Loading: {json_path}")
        segments = self.load_whisper_json(json_path)

        print(f"Merging {len(segments)} segments...")
        merged = self.merge_segments(segments)

        print(f"Splitting text with semchunk (max {self.max_words_per_line} words/line)...")
        vtt_lines = self.generate_vtt_lines(merged)

        print(f"Writing {len(vtt_lines)} lines to: {output_path}")
        self.write_vtt(vtt_lines, output_path)
        print("Done!")


def main():
    parser = argparse.ArgumentParser(
        description="Generate semantic VTT from Whisper JSON using semchunk"
    )
    parser.add_argument("input", help="Input Whisper JSON file")
    parser.add_argument("-o", "--output", help="Output VTT file")
    parser.add_argument("-w", "--max-words", type=int, default=10,
                        help="Max words per line (default: 10)")

    args = parser.parse_args()

    output_path = args.output or Path(args.input).with_suffix('.vtt').name

    generator = SemanticVTTGenerator(max_words_per_line=args.max_words)
    generator.process(args.input, output_path)


if __name__ == "__main__":
    main()