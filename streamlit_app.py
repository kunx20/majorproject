import streamlit as st
import requests
import os

st.title("Clinical Guideline QA System")

api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")

question = st.text_area("Ask a clinical question:", height=150)

if st.button("Ask", type="primary"):
    response = requests.post(f"{api_base_url}/api/ask", json={"question": question})
    data = response.json()
    
    st.success("Answer")
    st.write(data["answer"])
    
    st.info("Citations")
    for citation in data["citations"]:
        st.write(f"**{citation['section']}**: {citation['text']}")

st.caption("Powered by FAISS + RAG")
