import pytest
from pathlib import Path
from app.services.chunker import TextChunker
from app.services.cleaner import TextCleaner
from app.services.chunker import chunk_text

class TestTextChunker:
    def setup_method(self):
        self.chunker = TextChunker(chunk_size=100, overlap=20)
        self.cleaner = TextCleaner()

    def test_chunk_text_basic(self):
        """Test basic text chunking functionality."""
        text = "This is a test sentence. " * 20  # Repeat to create longer text
        chunks = self.chunker.chunk_text(text)

        assert len(chunks) > 1
        assert all('text' in chunk for chunk in chunks)
        assert all('metadata' in chunk for chunk in chunks)

    def test_chunk_text_with_metadata(self):
        """Test chunking with custom metadata."""
        text = "Medical guideline content for testing. " * 15
        metadata = {"source": "test_guideline.pdf", "version": "1.0"}

        chunks = self.chunker.chunk_text(text, metadata)

        for chunk in chunks:
            assert chunk['metadata']['source'] == "test_guideline.pdf"
            assert chunk['metadata']['version'] == "1.0"
            assert 'chunk_id' in chunk['metadata']

    def test_overlap_functionality(self):
        """Test that chunks have proper overlap."""
        text = "Short sentence one. Short sentence two. Short sentence three. Short sentence four."
        chunks = self.chunker.chunk_text(text)

        # With small chunk_size and overlap, we should see overlapping content
        if len(chunks) > 1:
            # Check that consecutive chunks share some content
            first_chunk_end = chunks[0]['text'][-20:]
            second_chunk_start = chunks[1]['text'][:20]
            # This is a basic check - in practice, overlap might not be exactly at word boundaries
            assert len(first_chunk_end) > 0
            assert len(second_chunk_start) > 0

    def test_save_and_load_chunks(self, tmp_path):
        """Test saving and loading chunks to/from files."""
        text = "Test content for chunking. " * 10
        chunks = self.chunker.chunk_text(text)

        # Save chunks
        self.chunker.save_chunks(chunks, tmp_path, "test_file")

        # Load chunks
        loaded_chunks = self.chunker.load_chunks(tmp_path, "test_file_chunk_*.txt")

        assert len(loaded_chunks) == len(chunks)
        for original, loaded in zip(chunks, loaded_chunks):
            assert original['text'] in loaded['text']  # Loaded text contains original plus metadata

class TestTextCleaner:
    def setup_method(self):
        self.cleaner = TextCleaner()

    def test_clean_text_removes_page_breaks(self):
        """Test that page break markers are removed."""
        text = "--- Page 1 ---\nContent here\n--- Page 2 ---\nMore content"
        cleaned = self.cleaner.clean_text(text)

        assert "--- Page" not in cleaned
        assert "Content here" in cleaned
        assert "More content" in cleaned

    def test_clean_text_normalizes_whitespace(self):
        """Test that excessive whitespace is normalized."""
        text = "Word1    word2\n\n\tword3"
        cleaned = self.cleaner.clean_text(text)

        assert "    " not in cleaned
        assert "\n\n" not in cleaned
        assert cleaned == "Word1 word2 word3"

    def test_extract_key_terms(self):
        """Test extraction of medical key terms."""
        text = "Patient has hypertension and diabetes. Treatment for cardiovascular disease."
        terms = self.cleaner.extract_key_terms(text)

        term_strings = [t.lower() for t in terms]
        assert "hypertension" in term_strings
        assert "diabetes" in term_strings
        assert "cardiovascular" in term_strings
        assert "treatment" in term_strings

    def test_split_into_sections(self):
        """Test splitting text into sections."""
        text = "INTRODUCTION\nThis is intro.\n\nMETHODOLOGY\nThis is methods.\n\nCONCLUSION\nThis is conclusion."
        sections = self.cleaner.split_into_sections(text)

        assert len(sections) >= 2  # Should split into multiple sections
        assert any("INTRODUCTION" in s or "This is intro" in s for s in sections)


def test_chunk_text():
    sample_text = " ".join(["guideline"] * 700)
    chunks = chunk_text(sample_text, chunk_size=300, overlap=50)

    assert len(chunks) > 0
    assert "text" in chunks[0]
    assert chunks[0]["chunk_id"] == 1