import streamlit as st
from main import *

st.title("📚 Interactive Textbook Q&A")
st.markdown("Ask questions about your textbooks and get answers with citations")

if 'qa_chain' not in st.session_state:
    with st.spinner("Loading system..."):
        vectorstore = load_vector_store()
        if vectorstore:
            st.session_state.qa_chain = create_qa_chain(vectorstore)
            st.success("Ready!")
        else:
            st.error("No database found. Run main.py first.")

question = st.text_input("Ask a question:", placeholder="e.g., Explain Newton's first law")

if st.button("Get Answer") and question:
    if 'qa_chain' in st.session_state:
        result = ask_question(st.session_state.qa_chain, question)
        
        st.markdown("### Answer:")
        st.write(result["answer"])
        
        if result["citations"]:
            st.markdown("### Citations:")
            for citation in result["citations"]:
                st.write(f"📖 {citation['textbook']} - {citation['chapter']}, Page {citation['page']}")
    else:
        st.error("System not initialized.")
