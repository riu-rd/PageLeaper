import streamlit as st
from src.config import (
    PAGE_ICON, INITIAL_MESSAGE
)
from src.auth import check_authentication, initialize_session_states
from src.config.settings import PAGE_TITLE_DASHBOARD
from src.ui import (
    apply_custom_styles, render_configuration_sidebar,
    render_header, render_chat_interface, render_file_uploader,
    render_document_status, get_chat_input, render_sample_prompts
)
from src.embedding import init_chromadb
from src.chat import initialize_chat_session, handle_user_input
from src.utils import init_gemini_client

st.set_page_config(
    page_title=PAGE_TITLE_DASHBOARD,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(apply_custom_styles(), unsafe_allow_html=True)

if not check_authentication():
    st.stop()

initialize_session_states()

client = init_gemini_client()

# Initialize ChromaDB if needed
if st.session_state.chroma_db is None:
    db, embed_fn = init_chromadb(client)
    st.session_state.chroma_db = db
    st.session_state.embed_fn = embed_fn

# Initialize chat session if needed
if st.session_state.chat_session is None:
    st.session_state.chat_session = initialize_chat_session(
        client, 
        st.session_state.model_config
    )

    if len(st.session_state.messages) == 0:
        st.session_state.messages.append({
            "role": "assistant",
            "content": INITIAL_MESSAGE
        })

# Create main layout
main_col, config_col = st.columns([3, 1])

with main_col:
    render_header()

    st.divider()
    
    chat_container = render_chat_interface()

    st.divider()

    user_input = get_chat_input()

    uploaded_files = render_file_uploader()
    
    if user_input:
        handle_user_input(user_input, chat_container)

    render_document_status()

    st.divider()

    render_sample_prompts(chat_container)
    
with config_col:
    render_configuration_sidebar()