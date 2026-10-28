import os
import re
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_core.prompts import PromptTemplate
from config import *

def load_textbook_with_metadata(file_path, textbook_name):
    """Load textbook and add metadata (chapter, page, textbook name)."""
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    for doc in documents:
        doc.metadata['textbook'] = textbook_name
        doc.metadata['page'] = doc.metadata.get('page', 0)
        doc.metadata['chapter'] = extract_chapter_info(doc.page_content)
    
    return documents

def extract_chapter_info(content):
    """Simple chapter extraction - looks for chapter patterns in text."""
    content_lower = content[:500].lower()
    if 'chapter' in content_lower:
        match = re.search(r'chapter\s+(\d+)', content_lower)
        if match:
            return f"Chapter {match.group(1)}"
    return "Unknown Chapter"

def load_all_textbooks(directory):
    """Load all textbooks from directory."""
    all_documents = []
    
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist!")
        return all_documents
    
    pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
    if not pdf_files:
        print(f"No PDF files found in '{directory}'")
        return all_documents
    
    print(f"Found {len(pdf_files)} textbook(s)")
    for filename in pdf_files:
        file_path = os.path.join(directory, filename)
        textbook_name = os.path.splitext(filename)[0]
        print(f"Loading: {textbook_name}")
        
        try:
            docs = load_textbook_with_metadata(file_path, textbook_name)
            all_documents.extend(docs)
            print(f"  ✓ Loaded {len(docs)} pages")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
    
    print(f"\nTotal pages loaded: {len(all_documents)}")
    return all_documents

def split_documents_with_metadata(documents):
    """Split documents while preserving metadata."""
    print("\nSplitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    
    for chunk in chunks:
        if 'textbook' not in chunk.metadata:
            chunk.metadata['textbook'] = 'Unknown'
        if 'page' not in chunk.metadata:
            chunk.metadata['page'] = 0
        if 'chapter' not in chunk.metadata:
            chunk.metadata['chapter'] = 'Unknown Chapter'
    
    print(f"Created {len(chunks)} chunks")
    return chunks

def create_embeddings():
    """Create Gemini embeddings using the configured API key."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_KEY not found. Add your Gemini API key to .env.")
    
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

def create_vector_store(chunks):
    """Create vector database with Gemini embeddings."""
    print("\nCreating vector database...")
    
    embeddings = create_embeddings()
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR
    )
    print(f"✓ Vector database created")
    return vectorstore

def load_vector_store():
    """Load existing vector database using Gemini embeddings."""
    if os.path.exists(VECTOR_DB_DIR) and os.listdir(VECTOR_DB_DIR):
        print("Loading existing vector database...")
        embeddings = create_embeddings()
        vectorstore = Chroma(
            persist_directory=VECTOR_DB_DIR,
            embedding_function=embeddings
        )
        print("✓ Database loaded")
        return vectorstore
    return None

def create_qa_chain(vectorstore):
    """Create Q&A chain with Gemini LLM and citation support."""
    print("\nSetting up Q&A chain...")
    
    # Swapped to Google Generative AI
    llm = GoogleGenerativeAI(
        model=MODEL_NAME,
        api_key=GEMINI_API_KEY,
        temperature=TEMPERATURE
    )
    
    template = """You are a helpful educational assistant. Answer the student's question based on the textbook content provided. 
    Be clear, educational, and provide examples when possible. Always cite the source when referencing specific information.

    Context from textbook:
    {context}

    Question: {question}

    Answer (include citations):"""
    
    PROMPT = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_kwargs={"k": NUM_RETRIEVED_DOCS}
        ),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
    print("✓ Q&A chain ready")
    return qa_chain

def ask_question(qa_chain, question):
    """Ask question and get answer with citations."""
    print(f"\nQuestion: {question}")
    print("Searching textbook...")
    
    try:
        result = qa_chain({"query": question})
        answer = result["result"]
        sources = result.get("source_documents", [])
        
        citations = []
        seen = set()
        for source in sources:
            textbook = source.metadata.get('textbook', 'Unknown')
            page = source.metadata.get('page', 'N/A')
            chapter = source.metadata.get('chapter', 'Unknown')
            
            citation_key = f"{textbook}_page_{page}"
            if citation_key not in seen:
                citations.append({
                    'textbook': textbook,
                    'chapter': chapter,
                    'page': page
                })
                seen.add(citation_key)
        
        return {
            "answer": answer,
            "sources": sources,
            "citations": citations
        }
    except Exception as e:
        return {
            "answer": f"Error: {str(e)}",
            "sources": [],
            "citations": []
        }

def main():
    """Main function."""
    print("=" * 60)
    print("📚 Interactive Textbook Q&A System")
    print("=" * 60)
    
    vectorstore = load_vector_store()
    if vectorstore is None:
        print("\nCreating new database...")
        documents = load_all_textbooks(TEXTBOOKS_DIR)
        if not documents:
            print("No textbooks found! Add PDF files to 'textbooks' folder.")
            return
        chunks = split_documents_with_metadata(documents)
        vectorstore = create_vector_store(chunks)
    
    qa_chain = create_qa_chain(vectorstore)
    
    print("\n" + "=" * 60)
    print("System ready! Ask questions about your textbooks")
    print("Type 'quit' to exit")
    print("=" * 60)
    
    while True:
        question = input("\n👤 Your question: ").strip()
        if question.lower() in ['quit', 'exit', 'q']:
            print("Goodbye! 👋")
            break
        if not question:
            continue
            
        result = ask_question(qa_chain, question)
        
        print("\n" + "-" * 60)
        print("📖 Answer:")
        print("-" * 60)
        print(result["answer"])
        
        if result["citations"]:
            print("\n" + "-" * 60)
            print("📚 Citations:")
            print("-" * 60)
            for i, citation in enumerate(result["citations"], 1):
                print(f"{i}. {citation['textbook']} - {citation['chapter']}, Page {citation['page']}")
        print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
