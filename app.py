import streamlit as st
import os
from PyPDF2 import PdfReader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.llms import Ollama
from langchain.chains.question_answering import load_qa_chain
from pymongo import MongoClient
from datetime import datetime

class MongoDBManager:
    def __init__(self, connection_string=None, db_name="chatbot", collection_name="conversations"):
        if connection_string is None:
            connection_string = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
        try:
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            self.collection.create_index([("user_id", 1), ("timestamp", -1)])
            st.success("Connected to MongoDB!")
        except Exception as e:
            st.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def save_conversation(self, user_id, query, response, metadata=None):
        try:
            document = {
                "user_id": user_id,
                "query": query,
                "response": response,
                "timestamp": datetime.utcnow(),
                "metadata": metadata or {}
            }
            self.collection.insert_one(document)
        except Exception as e:
            st.error(f"Failed to save conversation: {str(e)}")

    def get_conversation_history(self, user_id, limit=10):
        try:
            cursor = self.collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
            return [
                {
                    "query": doc["query"],
                    "response": doc["response"],
                    "timestamp": doc["timestamp"].isoformat(),
                    "metadata": doc["metadata"]
                }
                for doc in cursor
            ]
        except Exception as e:
            st.error(f"Failed to load history: {str(e)}")
            return []

    def close(self):
        self.client.close()

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to create FAISS vector store
def create_faiss_vector_store(text, path="faiss_index"):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(text)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    vector_store.save_local(path)

# Load FAISS vector store
def load_faiss_vector_store(path="faiss_index"):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
    return vector_store

# Build QA Chain
def build_qa_chain(vector_store_path="faiss_index"):
    vector_store = load_faiss_vector_store(vector_store_path)
    retriever = vector_store.as_retriever()
    llm = Ollama(model="llama3.2")
    qa_chain = load_qa_chain(llm, chain_type="stuff")
    qa_chain = RetrievalQA(retriever=retriever, combine_documents_chain=qa_chain)
    return qa_chain

# Streamlit App
st.title("RAG Chatbot with FAISS and LLaMA")
st.write("Upload a PDF and ask questions based on its content.")

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = "user_" + str(hash(datetime.now()))
if "messages" not in st.session_state:
    st.session_state.messages = []
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None
if "mongo_db" not in st.session_state:
    st.session_state.mongo_db = MongoDBManager()

# File uploader
uploaded_file = st.file_uploader("Upload your PDF file", type="pdf")

if uploaded_file is not None:
    pdf_path = f"uploaded/{uploaded_file.name}"
    os.makedirs("uploaded", exist_ok=True)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    text = extract_text_from_pdf(pdf_path)
    st.info("Creating FAISS vector store...")
    create_faiss_vector_store(text)
    st.info("Initializing chatbot...")
    st.session_state.qa_chain = build_qa_chain()
    st.success("Chatbot is ready!")

# Chat interface
if st.session_state.qa_chain:
    st.subheader("Ask a Question")
    with st.form(key="chat_form", clear_on_submit=True):
        question = st.text_input("Your question about the uploaded PDF:", key="query_input")
        submit_button = st.form_submit_button("Send")

    if submit_button and question:
        st.info("Querying the document...")
        answer = st.session_state.qa_chain.run(question)
        st.session_state.messages.append({"query": question, "response": answer})
        st.session_state.mongo_db.save_conversation(
            user_id=st.session_state.user_id,
            query=question,
            response=answer,
            metadata={"pdf_name": uploaded_file.name}
        )
        st.success(f"Answer: {answer}")

    # Display conversation history
    st.subheader("Conversation History")
    for msg in reversed(st.session_state.messages):
        with st.chat_message("user"):
            st.markdown(msg["query"])
        with st.chat_message("assistant"):
            st.markdown(msg["response"])

    # Button to load full history from MongoDB
    if st.button("Load Full History"):
        history = st.session_state.mongo_db.get_conversation_history(st.session_state.user_id, limit=10)
        st.session_state.messages = [
            {"query": h["query"], "response": h["response"]}
            for h in reversed(history)
        ]

# Clean up MongoDB connection
def cleanup():
    if "mongo_db" in st.session_state:
        st.session_state.mongo_db.close()

import atexit
atexit.register(cleanup)