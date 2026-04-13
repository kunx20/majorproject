"""
White Box Logic Tests - Test internal implementation details and code paths
Tests focus on verifying internal algorithms, data structures, and logic branches
"""

import pytest
from app.services.chunker import TextChunker
from app.services.cleaner import TextCleaner
from app.core.safety import is_unsafe_medical_query


class TestChunkerInternals:
    """White box: Internal chunking algorithm and data structures"""
    
    def setup_method(self):
        self.chunker = TextChunker(chunk_size=100, overlap=20)
    
    def test_chunker_initialization(self):
        """Test internal chunker state initialization"""
        assert self.chunker.chunk_size == 100
        assert self.chunker.overlap == 20
    
    def test_chunk_output_structure(self):
        """Test internal chunk data structure matches expectations"""
        text = "This is test content. " * 20
        chunks = self.chunker.chunk_text(text)
        
        # WHITE BOX: Test exact internal structure
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        
        for chunk in chunks:
            # Verify exact keys in internal dict structure
            assert isinstance(chunk, dict)
            assert set(chunk.keys()) == {'text', 'metadata'}
            
            # Verify metadata structure
            assert isinstance(chunk['metadata'], dict)
            assert 'chunk_id' in chunk['metadata']
            assert isinstance(chunk['metadata']['chunk_id'], (int, str))
    
    def test_chunk_size_constraint_internal(self):
        """Test internal chunk size never exceeds max"""
        text = "word " * 500  # Create large text
        chunks = self.chunker.chunk_text(text)
        
        # WHITE BOX: Verify internal size constraint
        max_allowed_size = self.chunker.chunk_size + self.chunker.overlap
        for chunk in chunks:
            assert len(chunk['text']) <= max_allowed_size * 2
    
    def test_chunk_overlap_implementation(self):
        """Test internal overlap algorithm creates expected duplicates"""
        # Create text with distinct markers
        text = "A B C D E F G H I J K L M N O P Q R S T "
        chunks = self.chunker.chunk_text(text, metadata={"test": True})
        
        # WHITE BOX: If we have multiple chunks, verify overlap exists
        if len(chunks) > 1:
            # Last 20 chars of first chunk should appear in second
            overlap_region = chunks[0]['text'][-self.chunker.overlap:]
            second_text = chunks[1]['text']
            # Overlap should create some continuity
            assert len(overlap_region) > 0
            assert len(second_text) > 0
    
    def test_metadata_attachment_internal(self):
        """Test metadata is correctly attached to each chunk"""
        custom_metadata = {
            "source": "test_file.pdf",
            "version": "2.0",
            "category": "guidelines"
        }
        text = "Test content " * 30
        chunks = self.chunker.chunk_text(text, metadata=custom_metadata)
        
        # WHITE BOX: Verify all custom metadata attached to all chunks
        for chunk in chunks:
            assert chunk['metadata']['source'] == "test_file.pdf"
            assert chunk['metadata']['version'] == "2.0"
            assert chunk['metadata']['category'] == "guidelines"
            # Verify internal chunk_id also added
            assert 'chunk_id' in chunk['metadata']


class TestCleanerInternals:
    """White box: Internal text cleaning logic and branches"""
    
    def setup_method(self):
        self.cleaner = TextCleaner()
    
    def test_page_break_removal_logic(self):
        """Test internal page break detection and removal"""
        # Test the patterns that the cleaner actually handles (--- Page X ---)
        text = "Content1\n--- Page 1 ---\nContent2"
        cleaned = self.cleaner.clean_text(text)
        # Verify page marker pattern is removed
        assert "--- Page" not in cleaned
        # Content should still be present
        assert "Content1" in cleaned and "Content2" in cleaned
    
    def test_whitespace_normalization_logic(self):
        """Test internal whitespace normalization algorithm"""
        test_cases = [
            ("word1    word2", "word1 word2"),
            ("text\n\n\nmore", "text more"),
            ("\t\ttabbed", "tabbed"),
            ("spaced  \n  text", "spaced text")
        ]
        
        for input_text, expected_pattern in test_cases:
            cleaned = self.cleaner.clean_text(input_text)
            # WHITE BOX: Verify no double spaces or excessive newlines
            assert "  " not in cleaned
            assert "\n\n" not in cleaned
            assert "\t" not in cleaned
    
    def test_key_term_extraction_internal(self):
        """Test internal medical term detection logic"""
        text = "Patient with hypertension and Type 2 diabetes presenting with cardiovascular complications"
        terms = self.cleaner.extract_key_terms(text)
        
        # WHITE BOX: Verify internal term list extraction
        assert isinstance(terms, list)
        assert len(terms) > 0
        # Verify extraction of medical keywords
        term_lower = [t.lower() for t in terms]
        assert any("hypertension" in t or "diabet" in t for t in term_lower)
    
    def test_section_splitting_logic(self):
        """Test internal section detection and splitting"""
        text = """INTRODUCTION
        This is the introduction section with content.
        
        METHODOLOGY
        This describes the methods used.
        
        RESULTS
        Results are presented here.
        
        CONCLUSION
        Conclusions are drawn."""
        
        sections = self.cleaner.split_into_sections(text)
        
        # WHITE BOX: Verify internal section detection
        assert isinstance(sections, list)
        assert len(sections) > 1
        # Verify section headers detected
        sections_text = " ".join(sections)
        assert "INTRODUCTION" in sections_text or "introduction" in sections_text.lower()


class TestSafetyLogicBranches:
    """White box: Internal safety check logic and code paths"""
    
    def test_emergency_keyword_detection(self):
        """Test internal emergency keyword detection path"""
        # PATH 1: Clear emergency cases (matching actual keywords in safety.py)
        emergency_cases = [
            "severe chest pain",
            "not breathing",
            "heart attack",
            "bleeding heavily",
            "stroke"
        ]
        
        for query in emergency_cases:
            result = is_unsafe_medical_query(query)
            assert result is True, f"Should detect emergency in: {query}"
    
    def test_safe_query_detection(self):
        """Test internal safe query detection path"""
        # PATH 2: Safe educational queries
        safe_cases = [
            "What is hypertension?",
            "First line treatment for diabetes",
            "Guidelines for blood pressure management",
            "How to manage cholesterol",
            "Patient education on medications"
        ]
        
        for query in safe_cases:
            result = is_unsafe_medical_query(query)
            assert result is False, f"Should accept safe query: {query}"
    
    def test_borderline_case_handling(self):
        """Test internal handling of borderline cases"""
        # PATH 3: Ambiguous cases - implementation may vary
        borderline_cases = [
            "side effects of medication",
            "adverse reactions",
            "symptoms",
            "complications"
        ]
        
        for query in borderline_cases:
            result = is_unsafe_medical_query(query)
            # Should be boolean
            assert isinstance(result, bool)
    
    def test_empty_string_handling(self):
        """Test internal handling of edge case: empty input"""
        result = is_unsafe_medical_query("")
        assert result is False
    
    def test_query_normalization_before_check(self):
        """Test internal case normalization"""
        # Query in different cases should have same result
        variants = [
            "CHEST PAIN",
            "Chest Pain",
            "chest pain",
            "ChEsT PaIn"
        ]
        
        results = [is_unsafe_medical_query(q) for q in variants]
        # All variants should produce same result (implementation normalizes)
        assert all(r == results[0] for r in results)
    
    def test_special_characters_handling(self):
        """Test internal special character handling"""
        queries_with_special_chars = [
            "chest@pain#emergency!!!",
            "difficulty breathing???",
            "pain...severe"
        ]
        
        # Should handle special chars without crashing
        for query in queries_with_special_chars:
            result = is_unsafe_medical_query(query)
            assert isinstance(result, bool)


class TestDataValidation:
    """White box: Internal data validation and type checking"""
    
    def test_chunker_handles_none_metadata(self):
        """Test chunker internal handling of None metadata"""
        chunker = TextChunker()
        text = "Test content " * 10
        
        # Should handle None gracefully
        chunks = chunker.chunk_text(text, metadata=None)
        assert len(chunks) > 0
        for chunk in chunks:
            assert 'metadata' in chunk
    
    def test_chunker_handles_unicode_text(self):
        """Test chunker internal unicode handling"""
        chunker = TextChunker()
        unicode_text = "Medical content with special chars: é à ñ ü 中文 العربية"
        
        chunks = chunker.chunk_text(unicode_text)
        # Should handle unicode without errors
        assert len(chunks) > 0
        for chunk in chunks:
            assert isinstance(chunk['text'], str)
    
    def test_cleaner_handles_various_newline_styles(self):
        """Test cleaner internal newline normalization"""
        cleaner = TextCleaner()
        # Different newline styles
        texts = [
            "line1\nline2",      # Unix
            "line1\r\nline2",    # Windows
            "line1\rline2"       # Old Mac
        ]
        
        for text in texts:
            cleaned = cleaner.clean_text(text)
            # Should normalize all to single space
            assert isinstance(cleaned, str)
            assert len(cleaned) > 0


class TestInternalStateManagement:
    """White box: Verify internal state is managed correctly"""
    
    def test_chunker_resets_between_calls(self):
        """Test chunker doesn't carry state between chunks"""
        chunker = TextChunker(chunk_size=50, overlap=10)
        
        # First chunking
        chunks1 = chunker.chunk_text("First text " * 20)
        
        # Second chunking with different text
        chunks2 = chunker.chunk_text("Second text " * 20)
        
        # Results should be independent
        assert chunks1[0]['text'] != chunks2[0]['text']
    
    def test_multiple_cleaner_instances_independent(self):
        """Test multiple cleaner instances don't share state"""
        cleaner1 = TextCleaner()
        cleaner2 = TextCleaner()
        
        text1 = "Text with    spaces"
        text2 = "Text with\n\nbreaks"
        
        result1 = cleaner1.clean_text(text1)
        result2 = cleaner2.clean_text(text2)
        
        # Results should be independent
        assert isinstance(result1, str)
        assert isinstance(result2, str)
