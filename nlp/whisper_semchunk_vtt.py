import json
import argparse
from semchunk import semchunk_text

def load_whisper_json(json_file):
    """Load Whisper JSON and extract words with timing."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    words = []
    for seg in data.get("segments", []):
        for w in seg.get("words", []):
            words.append({
                "text": w["text"],
                "start": w["start"],
                "end": w["end"]
            })
    return words

def words_to_text(words):
    """Convert list of word dicts to plain text."""
    return " ".join(w["text"] for w in words)

def create_vtt(chunks, output_file="output.vtt"):
    """Write chunks to a VTT file with timing from first/last word."""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for i, chunk in enumerate(chunks, 1):
            start = chunk[0]["start"]
            end = chunk[-1]["end"]
            text = " ".join(w["text"] for w in chunk)
            f.write(f"{format_time(start)} --> {format_time(end)}\n{text}\n\n")
    print(f"VTT file created: {output_file}")

def format_time(seconds):
    """Convert seconds to VTT timestamp (HH:MM:SS.mmm)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02}.{ms:03}"

def semantically_chunk(words, max_words=7):
    """Chunk words semantically using semchunk."""
    text = words_to_text(words)
    
    # Use semchunk_text to split into semantic chunks
    chunks_text = semchunk_text(text)
    
    # Convert back to word chunks with timing
    chunks = []
    idx = 0
    current_chunk = []
    
    for chunk_text in chunks_text:
        chunk_words = chunk_text.split()
        for w in chunk_words:
            # Skip words not in original word list
            if idx < len(words) and words[idx]["text"] == w:
                current_chunk.append(words[idx])
                idx += 1
            # Safety fallback
            elif idx < len(words):
                current_chunk.append(words[idx])
                idx += 1
            
            # Split further if chunk too long
            if len(current_chunk) >= max_words:
                chunks.append(current_chunk)
                current_chunk = []
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def main():
    parser = argparse.ArgumentParser(description="Convert Whisper JSON to semantically chunked VTT")
    parser.add_argument("json_file", help="Whisper JSON file")
    parser.add_argument("--output", default="output.vtt", help="Output VTT file")
    parser.add_argument("--max_words", type=int, default=7, help="Maximum words per subtitle")
    args = parser.parse_args()

    words = load_whisper_json(args.json_file)
    print(f"✅ Extracted {len(words)} words from Whisper JSON.")
    
    chunks = semantically_chunk(words, max_words=args.max_words)
    create_vtt(chunks, args.output)

if __name__ == "__main__":
    main()
