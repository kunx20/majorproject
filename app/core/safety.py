import re


def is_unsafe_medical_query(question: str) -> bool:
    unsafe_keywords = [
        "emergency",
        "heart attack",
        "stroke",
        "suicide",
        "bleeding heavily",
        "not breathing",
        "can't breathe",
        "can t breathe",
        "cannot breathe",
        "difficulty breathing",
        "pregnant complication",
        "chest pain",
        "unconscious",
        "diagnose me",
        "what disease do i have"
    ]

    q = re.sub(r"[^a-z0-9]+", " ", question.lower()).strip()
    return any(keyword in q for keyword in unsafe_keywords)


def get_safety_message() -> str:
    return (
        "This system provides information grounded in uploaded clinical guidelines only. "
        "It is not a diagnosis tool and must not be used for emergencies or urgent medical decisions."
    )
