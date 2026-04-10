from app.core.safety import is_unsafe_medical_query

def test_unsafe_query():
    assert is_unsafe_medical_query("I have severe chest pain and not breathing") is True

def test_safe_query():
    assert is_unsafe_medical_query("What is the first line treatment for hypertension?") is False
