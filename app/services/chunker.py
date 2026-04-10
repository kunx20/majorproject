from typing import List, Dict
from pathlib import Path
import json

class TextChunker:
    def __init__(self, chunk_size: int = 300, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        if self.overlap >= self.chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        chunks = []
        start = 0
        chunk_id = 1

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_content = text[start:end]

            chunk_metadata = {"chunk_id": chunk_id, "start_char": start, "end_char": end}
            if metadata:
                chunk_metadata.update(metadata)

            chunks.append({
                "text": chunk_content,
                "metadata": chunk_metadata
            })

            if end == len(text):
                break

            start = end - self.overlap
            chunk_id += 1

        return chunks

    def save_chunks(self, chunks: List[Dict], output_dir: Path, base_filename: str):
        """Save chunks to individual text files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for chunk in chunks:
            chunk_id = chunk['metadata']['chunk_id']
            filename = f"{base_filename}_chunk_{chunk_id}.txt"
            filepath = output_dir / filename
            
            content = f"Chunk ID: {chunk_id}\nMetadata: {json.dumps(chunk['metadata'])}\n\nText:\n{chunk['text']}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

    def load_chunks(self, input_dir: Path, pattern: str) -> List[Dict]:
        """Load chunks from text files."""
        chunks = []
        
        for filepath in input_dir.glob(pattern):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the content
            lines = content.split('\n')
            text_start = None
            metadata = {}
            
            for i, line in enumerate(lines):
                if line == 'Text:':
                    text_start = i + 1
                    break
                elif line.startswith('Metadata:'):
                    metadata_str = line[9:].strip()
                    try:
                        metadata = json.loads(metadata_str)
                    except:
                        pass
            
            if text_start is not None:
                text = '\n'.join(lines[text_start:])
                chunks.append({
                    'text': text,
                    'metadata': metadata
                })
        
        return chunks


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> List[Dict]:
    words = text.split()

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    start = 0
    chunk_id = 1

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunk_content = " ".join(chunk_words)

        chunks.append({
            "chunk_id": chunk_id,
            "start_word": start,
            "end_word": end,
            "text": chunk_content
        })

        if end == len(words):
            break

        start = end - overlap
        chunk_id += 1

    return chunks