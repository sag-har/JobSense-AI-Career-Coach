import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


# 100% free — runs locally, downloads once (~90MB), cached after that
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)


def ingest_pdf(pdf_path: str) -> FAISS:
    """Load a PDF file → split into chunks → embed → return FAISS store."""
    loader = PyMuPDFLoader(pdf_path)
    docs = loader.load()

    if not docs:
        raise ValueError("Could not extract text from PDF. Make sure it's not a scanned image.")

    chunks = splitter.split_documents(docs)
    return FAISS.from_documents(chunks, embeddings)


def ingest_text(text: str) -> FAISS:
    """Convert plain text (job description) → embed → return FAISS store."""
    if not text.strip():
        raise ValueError("Job description is empty.")

    chunks = splitter.split_documents([Document(page_content=text)])
    return FAISS.from_documents(chunks, embeddings)