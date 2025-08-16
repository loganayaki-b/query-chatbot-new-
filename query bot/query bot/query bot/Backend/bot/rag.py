# bot/rag.py
import os
import json
from langchain_community.document_loaders import TextLoader, JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Paths (adjust if needed)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
VECTORSTORE_DIR = os.path.join(os.path.dirname(__file__), 'vectorstore')
os.makedirs(VECTORSTORE_DIR, exist_ok=True)
VECTORSTORE_PATH = os.path.join(VECTORSTORE_DIR, 'faiss_index')

# Embedding model
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Function to load all documents
def load_documents():
    documents = []
    
    # Load .txt files
    txt_files = ['benefits_and_perks.txt', 'company_policies.txt', 'employee_handbook.txt']
    for file in txt_files:
        loader = TextLoader(os.path.join(DATA_DIR, file))
        docs = loader.load()
        documents.extend(docs)
    
    # Load .json files (extract text; adjust schema if needed)
    json_files = ['employee.json', 'query.json']
    for file in json_files:
        with open(os.path.join(DATA_DIR, file), 'r') as f:
            data = json.load(f)
            # Assuming JSON is a list of dicts or dict; convert to text
            if isinstance(data, list):
                for item in data:
                    text = json.dumps(item)  # Or extract specific fields, e.g., item['description']
                    documents.append(Document(page_content=text))
            elif isinstance(data, dict):
                text = json.dumps(data)
                documents.append(Document(page_content=text))
    
    # Split into chunks for better retrieval
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(documents)
    return split_docs

# Build or load vectorstore
def get_vectorstore(rebuild=False):
    if rebuild or not os.path.exists(VECTORSTORE_PATH):
        docs = load_documents()
        vectorstore = FAISS.from_documents(docs, embeddings)
        vectorstore.save_local(VECTORSTORE_PATH)
    else:
        vectorstore = FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)
    return vectorstore

# Module-level vectorstore (load on import)
vectorstore = get_vectorstore()  # Set rebuild=True first time to create index

# RAG retrieval function (can be used in chains)
def retrieve_docs(query, k=5):
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    return retriever.invoke(query)