import streamlit as st
import chromadb
from src.config import DEFAULT_MODEL_CONFIG, COLLECTION_NAME


def check_authentication():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.error("Access denied. Please log in on the main page.")
        st.switch_page("main.py")
        return False
    return True


def initialize_session_states():
    """Initialize all session state variables"""
    defaults = {
        'messages': [],
        'chat_session': None,
        'chroma_db': None,
        'embed_fn': None,
        'document_count': 0,
        'model_config': DEFAULT_MODEL_CONFIG.copy(),
        'processed_files': set(),
        'uploaded_filenames': [],
        'confirm_apply': False,
        'confirm_new_session': False,
        'file_uploader_key': 0
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_session(clear_all=False):
    """Reset session state. If clear_all is True, also clear documents."""
    if clear_all:
        try:
            chroma_client = chromadb.Client()
            chroma_client.delete_collection(COLLECTION_NAME)
        except:
            pass  # Collection might not exist
        
        # Clear the cached init_chromadb function to force reinitialization
        if hasattr(st, 'cache_resource'):
            # Import here to avoid circular import
            from src.embedding import init_chromadb
            init_chromadb.clear()
        
        st.session_state.chroma_db = None
        st.session_state.embed_fn = None
        st.session_state.document_count = 0
        st.session_state.processed_files = set()
        st.session_state.uploaded_filenames = []
        # Increment file uploader key to clear files
        st.session_state.file_uploader_key += 1
    
    # Always clear chat
    st.session_state.messages = []
    st.session_state.chat_session = None
    
    # Reset confirmation states
    st.session_state.confirm_apply = False
    st.session_state.confirm_new_session = False