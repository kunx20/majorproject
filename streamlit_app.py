import streamlit as st
import requests

st.title("Clinical Guideline QA System")

question = st.text_area("Ask a clinical question:", height=150)

if st.button("Ask", type="primary"):
    response = requests.post("http://127.0.0.1:8000/api/ask", json={"question": question})
    data = response.json()
    
    st.success("Answer")
    st.write(data["answer"])
    
    st.info("Citations")
    for citation in data["citations"]:
        st.write(f"**{citation['section']}**: {citation['text']}")

st.caption("Powered by FAISS + RAG")
