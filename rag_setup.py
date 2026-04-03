"""
rag_setup.py
────────────
Initialises the RAG (Retrieval-Augmented Generation) system:
  • loads the error knowledge-base text file
  • splits it into chunks
  • creates HuggingFace embeddings
  • builds a FAISS vector store

Exposes a single public function: `search(query)` → list of matching chunks.
All tuneable parameters come from config.py.
"""

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

import config

# ── Module-level singleton (built once on first import) ──────────────────────
_db: FAISS | None = None


def _build_db() -> FAISS:
    """Load the errors file, embed it, and return a FAISS index."""
    print("🔄  Loading error knowledge base …")
    loader    = TextLoader(config.ERRORS_FILE, encoding="utf-8")
    documents = loader.load()

    splitter = CharacterTextSplitter(
        chunk_size    = config.CHUNK_SIZE,
        chunk_overlap = config.CHUNK_OVERLAP,
    )
    docs = splitter.split_documents(documents)

    print("🔄  Creating embeddings …")
    embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)

    db = FAISS.from_documents(docs, embeddings)
    print("✅  RAG system ready!\n")
    return db


def get_db() -> FAISS:
    """Return the FAISS index, initialising it on the first call."""
    global _db
    if _db is None:
        _db = _build_db()
    return _db


def search(query: str) -> list:
    """
    Run a similarity search against the knowledge base.

    Parameters
    ----------
    query : natural-language question / error description

    Returns
    -------
    List of LangChain Document objects (up to TOP_K results).
    """
    return get_db().similarity_search(query, k=config.TOP_K)
