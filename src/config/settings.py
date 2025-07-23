import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PASSWORD = os.getenv("PASSWORD")

# Document Processing
MAX_FILES = 5
CHUNK_SIZE = 1000  # Characters per chunk
BATCH_SIZE = 20  # Number of chunks to process at once

# Model Configuration Defaults
DEFAULT_MODEL_CONFIG = {
    'model': 'gemini-2.5-flash',
    'temperature': 0.35,
    'top_k': 40,
    'top_p': 0.95
}

# Model Options
MODEL_OPTIONS = {
    "Faster (Gemini 2.5 Flash)": "gemini-2.5-flash",
    "Powerful (Gemini 2.5 Pro)": "gemini-2.5-pro"
}

# ChromaDB
COLLECTION_NAME = "pageleaper_docs"
EMBEDDING_MODEL = "models/text-embedding-004"
EMBEDDING_DIMENSION = 768
DEFAULT_SEARCH_RESULTS = 10

# Embedding Task Types
EMBEDDING_TASK_DOCUMENT = "retrieval_document"
EMBEDDING_TASK_QUERY = "retrieval_query"

# UI Messages
INITIAL_MESSAGE = """Hello! I'm PageLeaper, your comprehensive document understanding agent. 
    
I can analyze lengthy PDF and DOCX files to help you find information, answer questions, and gain insights from your documents. Simply upload your files using the button below, and then ask me anything about their content!

I'm ready to help you navigate through your documents efficiently. What would you like to know?"""

PROMPT_TEMPLATE = """You are PageLeaper, a helpful document analysis assistant. {document_info}Answer the user's question based on the provided document context. Be comprehensive but concise.

User Question: {user_question}

{context_text}

Please provide a clear and helpful answer based on the documents provided."""

# Page Configuration
PAGE_TITLE_MAIN = "PageLeaper - Authentication"
PAGE_TITLE_DASHBOARD = "PageLeaper - Dashboard"
PAGE_ICON = "📖"

# UI Text
FILE_UPLOAD_HELP = f"Upload up to {MAX_FILES} PDF or DOCX files. Note: Individual file deletion is disabled - use 'New Session' to clear all files."
CHAT_INPUT_PLACEHOLDER = "Ask about your documents or chat with me..."
NO_DOCUMENTS_INFO = "📄 Please upload PDF or DOCX files to start analyzing documents. You can upload up to 5 files at once."
CONFIG_WARNING = "⚠️ This will restart your session and clear the current chat."
NEW_SESSION_WARNING = "⚠️ This will clear all documents and chat history."