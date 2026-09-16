import ollama
from app.core.config import settings

# Test if Ollama is available at startup
OLLAMA_AVAILABLE = False
try:
    # Try to connect to Ollama
    ollama.list()
    OLLAMA_AVAILABLE = True
    print("✓ Ollama service is available")
except Exception as e:
    OLLAMA_AVAILABLE = False
    print(f"✗ Warning: Ollama service not available - using fallback: {str(e)}")


def generate_answer_with_ollama_chat(question: str, context: str) -> str:
    """
    Generate a medical answer using Ollama LLM based on retrieved clinical guidelines.
    Falls back to simple text extraction if Ollama is unavailable.
    
    Args:
        question: The user's clinical question
        context: The clinical guideline context from retrieved chunks
        
    Returns:
        A well-formatted, accurate medical answer
    """
    if not OLLAMA_AVAILABLE or not settings.USE_LLM:
        # Fallback: Use simple context extraction
        return generate_answer_fallback(question, context)
    
    # Plain-language prompt for non-doctor users
    system_prompt = """You are a helpful health information assistant.

Your job is to:
1. Answer using only the provided clinical guidelines
2. Write in very simple, everyday English
3. Explain medical terms in plain words
4. Use short paragraphs and clear bullet points where helpful
5. Say when the information is limited or missing
6. Avoid giving personal medical advice

Important:
- Keep the answer easy for a non-doctor to understand
- Do not use too much technical language
- Do not invent information
- Do not replace a doctor or healthcare professional
- Keep the answer practical and readable"""
    
    user_prompt = f"""Please answer this question in simple, plain language for a general patient.

QUESTION: {question}

CLINICAL GUIDELINES:
{context}

Please:
- start with a short, clear answer
- explain key terms in simple words
- use easy bullet points if helpful
- mention if the guideline is limited or unclear
- end with a gentle note that this is general information, not personal medical advice
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        # Configure generation options
        ollama_options = {
            "temperature": 0.2,  # Very low for medical accuracy
            "top_p": 0.9,
            "num_predict": 300,  # Reduced from 500 for faster response
            "top_k": 40,  # Faster decoding
            "repeat_penalty": 1.1,
            "num_thread": settings.NUM_THREADS,  # Parallel CPU processing
        }
        
        # Enable GPU layers if available
        if settings.ENABLE_GPU:
            ollama_options["num_gpu"] = settings.NUM_GPU_LAYERS
        
        response = ollama.chat(
            model=settings.OLLAMA_MODEL,
            messages=messages,
            stream=False,
            options=ollama_options
        )
        answer = response["message"]["content"].strip()
        
        # Clean up formatting
        answer = clean_response(answer)
        return answer
        
    except Exception as e:
        print(f"Ollama error: {e}, falling back to context extraction")
        return generate_answer_fallback(question, context)


def generate_answer_fallback(question: str, context: str) -> str:
    """Fallback answer generation when Ollama is unavailable"""
    answer = context.strip()
    if len(answer) > 500:
        answer = answer[:500] + "..."

    simple_intro = "Here is the main point in simple language:\n\n"
    return simple_intro + answer + "\n\nThis is general information, not personal medical advice."


def clean_response(text: str) -> str:
    """Clean and format LLM response for better readability"""
    # Remove excessive whitespace
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = '\n'.join(lines)

    # Remove markdown formatting if present
    text = text.replace('**', '').replace('__', '').replace('`', '')

    # Remove prompt/instruction artifacts from model output
    text = text.replace('Sure! Here\'s an example of how to answer this question using plain, simple language for a general patient:', '')
    text = text.replace('Sure! Here\'s an example of how to answer the question using simple, plain language for a general patient:', '')
    text = text.replace('What is the recommended treatment?', '')
    text = text.replace('CLINICAL GUIDELINES:', '').replace('CLINICAL GUIIDELINES:', '')
    text = text.replace('QUESTION:', '')
    text = text.replace('Please:', '')
    text = text.replace('RECOMMENDED TREATMENT:', '')
    text = text.replace('Use clinical guidance only.', '')

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    cleaned_lines = []
    blocked_prefixes = (
        'start with a short',
        'use simple',
        'use easy bullet points',
        'end with a gentle note',
        'please:',
        'here\'s an example',
        'question:',
        'clinical guide',
        'what is the recommended treatment',
        '- start with',
        '- use simple',
        '- use easy',
        '- end with'
    )

    for line in lines:
        low = line.lower()
        if low.startswith(blocked_prefixes):
            continue
        if low in {'sure!', 'sure! here\'s an example of how to answer this question using plain, simple language for a general patient:', 'sure! here\'s an example of how to answer the question using simple, plain language for a general patient:', 'use clinical guidance only.', 'recommended treatment:'}:
            continue
        if 'here\'s an example' in low or 'use clinical guidance only' in low or 'recommended treatment' in low:
            continue
        cleaned_lines.append(line)

    text = '\n'.join(cleaned_lines).strip()

    if not text:
        return "Here is the main point in simple language:\n\nThis guideline does not provide enough detail for a personal medical recommendation. This is general information, not personal medical advice."

    if not text.lower().startswith(('here is', 'in simple', 'short answer', 'the main point')):
        text = "Here is the main point in simple language:\n\n" + text

    if "not personal medical advice" not in text.lower():
        text += "\n\nThis is general information, not personal medical advice."

    return text
