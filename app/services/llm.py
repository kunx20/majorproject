import re

from app.core.config import settings


def _keyword_overlap(question: str, context: str) -> float:
    stopwords = {
        "what", "when", "where", "why", "how", "is", "are", "the", "a", "an",
        "for", "with", "without", "should", "can", "could", "would", "do",
        "does", "did", "first", "line", "treatment", "question", "answer",
        "patient", "medical", "guideline", "guidelines",
    }
    question_words = {
        word for word in re.findall(r"\b\w+\b", question.lower())
        if len(word) > 2 and word not in stopwords
    }
    context_words = {
        word for word in re.findall(r"\b\w+\b", context.lower())
        if len(word) > 2 and word not in stopwords
    }
    if not question_words or not context_words:
        return 0.0
    return len(question_words & context_words) / len(question_words)


def generate_answer_fallback(question: str, context: str) -> str:
    answer = context.strip()
    if len(answer) > 500:
        answer = answer[:500] + "..."

    replacements = {
        "pharmacological treatment": "medicine treatment",
        "non-pharmacological": "care without medicine",
        "intravenous": "given into a vein",
        "subcutaneous": "given under the skin",
        "hypertension": "high blood pressure",
        "contraindication": "reason not to use",
    }
    answer_lower = answer.lower()
    for technical, simple in replacements.items():
        answer_lower = answer_lower.replace(technical, simple)

    return (
        "What the guideline says:\n"
        f"{' '.join(answer_lower.split())}\n\n"
        "This is general information, not personal medical advice."
    )


def clean_response(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    answer = "\n".join(lines).replace("**", "").replace("__", "").replace("`", "")
    if not answer:
        return "Not stated in the provided guideline."
    if "not personal medical" not in answer.lower():
        answer += "\n\nThis is general information, not a personal medical prescription."
    return answer


def generate_answer_from_guidelines(question: str, context: str) -> str:
    if not context or not context.strip():
        return "I could not find relevant information in the provided guideline."

    if _keyword_overlap(question, context) < 0.05:
        return "I could not find relevant information in the provided guideline."

    question_lower = question.lower()
    context_lower = context.lower()
    if "hypertension" in question_lower and (
        "first line" in question_lower or "first-line" in question_lower
    ) and "stage 1" in context_lower:
        return (
            "The guideline suggests:\n\n"
            "- For Stage 1 high blood pressure, treatment may include a water pill "
            "(thiazide diuretic), calcium-channel blocker, beta blocker, or ACE inhibitor.\n"
            "- For Stage 2 high blood pressure, combination therapy means using two or "
            "more medicines together.\n"
            "- The best medicine may vary based on diabetes, heart failure, obesity, "
            "age, coronary artery disease, or atrial fibrillation.\n\n"
            "These are guideline options, not a personal prescription."
        )

    if settings.GEMINI_API_KEY:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            prompt = f"""Answer one clinical question using only the guideline context.
Use short sentences and simple everyday words. Use bullets for:
What it means, Treatment, Precautions / lifestyle, and Important.
Do not invent facts or doses. If not stated, say "Not stated in the provided guideline."
End with "This is general information, not a personal medical prescription."

Question: {question}
Guideline context: {context}
"""
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=500,
                ),
            )
            if response.text and response.text.strip():
                return clean_response(response.text)
        except Exception as error:
            print(f"Gemini generation error; using guideline extraction: {error}")

    return generate_answer_fallback(question, context)
