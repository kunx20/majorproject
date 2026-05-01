import ollama
from app.core.config import settings


def generate_answer_with_ollama_chat(question: str, context: str) -> str:
    """
    Generate a medical answer using Ollama LLM based on retrieved clinical guidelines.
    Optimized for accuracy, clarity, and medical precision.
    
    Args:
        question: The user's clinical question
        context: The clinical guideline context from retrieved chunks
        
    Returns:
        A well-formatted, accurate medical answer
    """
    # Optimized medical prompt for high-quality responses
    system_prompt = """You are an expert medical information assistant specializing in clinical guidelines.

Your role is to:
1. Answer ONLY based on the provided clinical guidelines
2. Provide clear, accurate, and evidence-based information
3. Use medical terminology appropriately (don't over-simplify)
4. Format answers in a structured, easy-to-read manner
5. If information is insufficient, clearly state what's missing

Never:
- Invent or hallucinate medical information
- Provide personal medical advice
- Replace professional medical consultation
- Include information not in the guidelines"""
    
    user_prompt = f"""Based on the clinical guidelines provided below, answer this question:

QUESTION: {question}

CLINICAL GUIDELINES:
{context}

ANSWER:
Provide a clear, structured answer based only on the guidelines above."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        # Configure GPU acceleration if available
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
        raise RuntimeError(f"Error generating answer with Ollama: {str(e)}")


def clean_response(text: str) -> str:
    """Clean and format LLM response for better readability"""
    # Remove excessive whitespace
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = '\n'.join(lines)
    
    # Remove markdown formatting if present
    text = text.replace('**', '').replace('__', '').replace('`', '')
    
    # Clean up common artifacts
    text = text.replace('ANSWER:', '').replace('Answer:', '').strip()
    
    return text
