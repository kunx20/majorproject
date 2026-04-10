import re
from typing import List

class TextCleaner:
    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        """Clean extracted text by normalizing whitespace and removing page breaks."""
        text = text.replace("\r", "\n")
        text = re.sub(r'\n+', ' ', text)  # Replace all newlines with spaces
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'--- Page \d+ ---', '', text)
        return text.strip()

    def extract_key_terms(self, text: str) -> List[str]:
        """Extract key medical terms from text (simple implementation)."""
        # Simple keyword extraction - in practice, this would use NLP
        medical_terms = [
            'hypertension', 'diabetes', 'cardiovascular', 'treatment', 'patient',
            'diagnosis', 'symptoms', 'therapy', 'medication', 'clinical'
        ]
        
        found_terms = []
        text_lower = text.lower()
        for term in medical_terms:
            if term in text_lower:
                found_terms.append(term)
        
        return found_terms

    def split_into_sections(self, text: str) -> List[str]:
        """Split text into sections based on headings."""
        # Simple section splitting based on uppercase lines or common section headers
        lines = text.split('\n')
        sections = []
        current_section = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line looks like a section header (all caps, or common headers)
            if (line.isupper() and len(line) > 3) or line.upper() in [
                'INTRODUCTION', 'METHODOLOGY', 'CONCLUSION', 'RESULTS', 'DISCUSSION',
                'ABSTRACT', 'BACKGROUND', 'MATERIALS', 'METHODS'
            ]:
                if current_section:
                    sections.append('\n'.join(current_section))
                    current_section = []
                current_section.append(line)
            else:
                current_section.append(line)
        
        if current_section:
            sections.append('\n'.join(current_section))
        
        return sections


def clean_extracted_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'--- Page \d+ ---', '', text)
    return text.strip()