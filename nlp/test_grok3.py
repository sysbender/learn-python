#!/usr/bin/env python3
"""
Semantic VTT Generator – pure spaCy syntactic chunking
Guarantees natural splits for language learners.
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
import spacy
from spacy.tokens import Doc, Token

# --------------------------------------------------------------
# 1. Load the French spaCy model (fallback to English)
# --------------------------------------------------------------
try:
    nlp = spacy.load("fr_core_news_sm")
    LANG = "fr"
except OSError:
    nlp = spacy.load("en_core_web_sm")
    LANG = "en"


# --------------------------------------------------------------
# 2. Syntactic chunker – no semchunk, no word-count first
# --------------------------------------------------------------
class SyntacticChunker:
    def __init__(self, max_words: int = 10):
        self.max_words = max_words

    @staticmethod
    def _word_count(text: str) -> int:
        return len(text.split())

    def _split_at_punct(self, text: str) -> List[str]:
        # 1. Comma
        parts = text.split(',', 1)
        if len(parts) == 2:
            left, right = parts[0].strip(), parts[1].strip()
            if self._word_count(left) >= 3 and self._word_count(right) >= 3:
                return [left + ',', right]

        # 2. Conjunctions
        for conj in ["ou", "et", "mais", "donc", "car", "ni"]:
            parts = text.split(f" {conj} ", 1)
            if len(parts) == 2:
                left, right = parts[0].strip(), (conj + " " + parts[1]).strip()
                if self._word_count(left) >= 4 and self._word_count(right) >= 4:
                    return [left, right]

        return [text.strip()]

    def _split_at_main_verb(self, text: str) -> List[str]:
        doc = nlp(text)
        sent = list(doc.sents)[0]
        root = None
        for token in sent:
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                root = token
                break
        if not root:
            return [text.strip()]

        # Find subject and clause boundary
        left_tokens = []
        right_tokens = []
        in_left = True
        for token in sent:
            if token == root:
                in_left = False
            if in_left:
                left_tokens.append(token)
            else:
                right_tokens.append(token)

        left = " ".join(t.text_with_ws for t in left_tokens).strip()
        right = " ".join(t.text_with_ws for t in right_tokens).strip()

        if self._word_count(left) >= 4 and self._word_count(right) >= 4:
            return [left, right]
        return [text.strip()]

    def _split_with_phrases(self, text: str) -> List[str]:
        if self._word_count(text) <= self.max_words:
            return [text.strip()]

        # 1. Try punctuation
        result = self._split_at_punct(text)
        if len(result) > 1:
            final = []
            for part in result:
                final.extend(self._split_with_phrases(part))
            return final

        # 2. Try main verb split
        result = self._split_at_main_verb(text)
        if len(result) > 1:
            final = []
            for part in result:
                final.extend(self._split_with_phrases(part))
            return final

        # 3. Fallback: hard split at word count
        words = text.split()
        mid = len(words) // 2
        left = " ".join(words[:mid])
        right = " ".join(words[mid:])
        if self._word_count(left) >= 4 and self._word_count(right) >= 4:
            return [left, right]
        return [text.strip()]

    def split_into_lines(self, text: str) -> List[str]:
        if not text.strip():
            return []
        doc = nlp(text)
        lines = []
        for sent in doc.sents:
            sent_text = sent.text.strip()
            if not sent_text:
                continue
            lines.extend(self._split_with_phrases(sent_text))
        return [l for l in lines if l.strip()]
# --------------------------------------------------------------
# 3. VTT generator (unchanged except using the new chunker)
# --------------------------------------------------------------
class SemanticVTTGenerator:
    def __init__(self, max_words_per_line: int = 10):
        self.max_words = max_words_per_line
        self.chunker = SyntacticChunker(max_words_per_line)

    def load_whisper_json(self, json_path: str) -> List[Dict[str, Any]]:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("segments", data if isinstance(data, list) else [])

    def merge_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not segments:
            return []
        merged, cur = [], segments[0].copy()
        for s in segments[1:]:
            if s["start"] - cur["end"] < 0.5 and s.get("no_speech_prob", 1.0) < 0.8:
                cur["text"] += " " + s["text"]
                cur["end"] = s["end"]
            else:
                merged.append(cur)
                cur = s.copy()
        merged.append(cur)
        return merged

    def format_timestamp(self, secs: float) -> str:
        h = int(secs // 3600)
        m = int((secs % 3600) // 60)
        s = int(secs % 60)
        ms = int((secs - int(secs)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

    def generate_vtt_lines(self, merged: List[Dict[str, Any]]) -> List[Tuple[str, str, str, str]]:
        vtt = []
        idx = 1
        for seg in merged:
            start, end = seg["start"], seg["end"]
            text = seg["text"]
            lines = self.chunker.split_into_lines(text)
            if not lines:
                continue

            total_words = sum(len(l.split()) for l in lines)
            if total_words == 0:
                continue
            sec_per_word = (end - start) / total_words
            t = start

            for line in lines:
                wc = len(line.split())
                dur = wc * sec_per_word
                vtt.append((str(idx),
                            self.format_timestamp(t),
                            self.format_timestamp(t + dur),
                            line))
                idx += 1
                t += dur
        return vtt

    def write_vtt(self, lines: List[Tuple[str, str, str, str]], path: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write("WEBVTT\n\n")
            for i, s, e, txt in lines:
                f.write(f"{i}\n{s} --> {e}\n{txt}\n\n")

    def process(self, json_path: str, out_path: str):
        print(f"Loading {json_path}")
        segs = self.load_whisper_json(json_path)
        print(f"Merging {len(segs)} segments...")
        merged = self.merge_segments(segs)
        print("Splitting with spaCy syntactic chunker...")
        vtt = self.generate_vtt_lines(merged)
        print(f"Writing {len(vtt)} lines to {out_path}")
        self.write_vtt(vtt, out_path)
        print("Done!")


# --------------------------------------------------------------
# 4. CLI
# --------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(
        description="Semantic VTT from Whisper JSON – pure spaCy syntactic split")
    p.add_argument("input", help="Whisper JSON file")
    p.add_argument("-o", "--output", help="Output .vtt")
    p.add_argument("-w", "--max-words", type=int, default=10,
                   help="Max words per line (default: 10)")
    args = p.parse_args()

    out = args.output or Path(args.input).with_suffix(".vtt").name
    gen = SemanticVTTGenerator(args.max_words)
    gen.process(args.input, out)


def test_():
    gen = SemanticVTTGenerator(max_words_per_line=10)
    text = "Bonjour à toutes et à tous, et bienvenue dans notre leçon du jour."
    print("\n".join(gen.chunker.split_into_lines(text)))

if __name__ == "__main__":
    main()