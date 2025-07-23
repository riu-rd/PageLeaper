import chromadb
import streamlit as st
from .gemini import GeminiEmbeddingFunction
from src.config import COLLECTION_NAME, DEFAULT_SEARCH_RESULTS


@st.cache_resource
def init_chromadb(_client):
    """Initialize ChromaDB with Gemini embeddings"""
    embed_fn = GeminiEmbeddingFunction(_client)
    chroma_client = chromadb.Client()
    db = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn
    )
    return db, embed_fn


def search_documents(query, db, embed_fn, n_results=DEFAULT_SEARCH_RESULTS):
    """Search documents in ChromaDB"""
    # Switch to query mode for embeddings
    embed_fn.document_mode = False
    
    # Perform search
    results = db.query(query_texts=[query], n_results=n_results)
    
    # Switch back to document mode
    embed_fn.document_mode = True
    
    # Process results
    contexts = []
    if results['documents'] and results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            metadata = results['metadatas'][0][i]
            contexts.append({
                'content': doc,
                'filename': metadata.get('filename', 'Unknown'),
                'page': metadata.get('page', 'Unknown'),
                'chunk': metadata.get('chunk', 0)
            })
    
    return contexts