import streamlit as st
from chromadb import Documents, EmbeddingFunction, Embeddings
from google.api_core import retry, exceptions
from google.genai import types
from src.config import EMBEDDING_MODEL, EMBEDDING_DIMENSION, EMBEDDING_TASK_DOCUMENT, EMBEDDING_TASK_QUERY


class GeminiEmbeddingFunction(EmbeddingFunction):
    """Custom embedding function using Google Gemini"""
    
    def __init__(self, client):
        self.client = client
        self.document_mode = True
    
    @retry.Retry(predicate=retry.if_exception_type(
        exceptions.ResourceExhausted,
        exceptions.ServiceUnavailable
    ))
    def __call__(self, input: Documents) -> Embeddings:
        try:
            if self.document_mode:
                embedding_task = EMBEDDING_TASK_DOCUMENT
            else:
                embedding_task = EMBEDDING_TASK_QUERY
            
            response = self.client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=input,
                config=types.EmbedContentConfig(
                    task_type=embedding_task,
                ),
            )
            return [e.values for e in response.embeddings]
        except Exception as e:
            st.error(f"Embedding error: {str(e)}")
            # Return empty embeddings as fallback
            return [[0.0] * EMBEDDING_DIMENSION for _ in input]  # type: ignore