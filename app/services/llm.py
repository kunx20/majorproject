import ollama
from app.core.config import settings


def generate_answer_with_ollama(question: str, context: str) -> str:
    """
    Generate an answer using Ollama LLM based on retrieved context.
    
    Args:
        question: The user's question
        context: The clinical guideline context from retrieved chunks
        
    Returns:
        The LLM-generated answer
    """
    prompt = f"""You are a medical assistant. Answer the following question based ONLY on the provided clinical guidelines.
Be concise, accurate, and avoid making up information not in the guidelines.
If the guidelines don't contain enough information to answer, say so clearly.

Question: {question}

Clinical Guidelines Context:
{context}

Answer:"""
    
    try:
        response = ollama.generate(
            model=settings.OLLAMA_MODEL,
            prompt=prompt,
            stream=False,
            options={
                "temperature": 0.3,  # Low temperature for consistency
                "top_p": 0.9,
                "top_k": 40,
            }
        )
        return response["response"].strip()
    except Exception as e:
        raise RuntimeError(f"Error generating answer with Ollama: {str(e)}")


def generate_answer_with_ollama_chat(question: str, context: str) -> str:
    """
    Alternative method using Ollama chat API for better quality responses.
    
    Args:
        question: The user's question
        context: The clinical guideline context from retrieved chunks
        
    Returns:
        The LLM-generated answer
    """
    messages = [
        {
            "role": "system",
            "content": "You are a medical assistant. Answer questions based ONLY on the provided clinical guidelines. Be concise and accurate. Do not invent information."
        },
        {
            "role": "user",
            "content": f"Question: {question}\n\nClinical Guidelines:\n{context}"
        }
    ]
    
    try:
        response = ollama.chat(
            model=settings.OLLAMA_MODEL,
            messages=messages,
            stream=False,
            options={
                "temperature": 0.3,
                "top_p": 0.9,
            }
        )
        return response["message"]["content"].strip()
    except Exception as e:
        raise RuntimeError(f"Error generating answer with Ollama chat: {str(e)}")
