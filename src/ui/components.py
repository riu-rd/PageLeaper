import streamlit as st
import hashlib
import os
from src.config import MAX_FILES, FILE_UPLOAD_HELP, CHAT_INPUT_PLACEHOLDER, NO_DOCUMENTS_INFO
from src.document.processor import process_documents


def render_header_main():
    st.title("PageWise")
    st.caption("Ask more, scroll less.")

def render_authenticator():
    with st.container():
        password = st.text_input("Password", type="password", key="password_input")
        
        if st.button("Enter", use_container_width=True):
            correct_password = os.getenv("PASSWORD")
            
            if password == correct_password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid password.")

def render_footer():
    st.markdown("---")
    st.markdown("Created by Darius Vincent Ardales", help="PH - Machine Learning Engineer (GenAI Track) Take-Home Exam")

def render_header():
    """Render the page header with title and exit button"""
    col1, col2 = st.columns([10, 1])
    with col1:
        st.title("PageWise")
        st.caption("Ask more, scroll less.")
    with col2:
        if st.button("Exit", key="exit_button"):
            st.session_state.authenticated = False
            st.switch_page("main.py")


def render_chat_interface():
    """Render the chat messages interface"""
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    return chat_container


def render_file_uploader():
    """Render the file uploader component"""
    uploaded_files = st.file_uploader(
        "📄 Drag and drop files here",
        type=['pdf', 'docx'],
        accept_multiple_files=True,
        key=f"file_uploader_{st.session_state.file_uploader_key}",
        help=FILE_UPLOAD_HELP,
        disabled=False
    )
    
    if uploaded_files:
        handle_uploaded_files(uploaded_files)
    
    return uploaded_files


def handle_uploaded_files(uploaded_files):
    """Process uploaded files and update session state"""
    # Get list of new files that haven't been processed yet
    new_files = []
    already_processed = 0
    
    for file in uploaded_files:
        file_hash = hashlib.md5((file.name + str(file.size)).encode()).hexdigest()
        if file_hash not in st.session_state.processed_files:
            new_files.append((file, file_hash))
        else:
            already_processed += 1
    
    if already_processed > 0 and not new_files:
        st.info(f"ℹ️ All {already_processed} file(s) have already been processed. You can ask questions about them below.")
    
    if new_files:
        if len(new_files) > MAX_FILES:
            st.error(f"Please upload a maximum of {MAX_FILES} files at a time.")
        else:
            with st.spinner(f"Processing {len(new_files)} new file(s)..."):
                # Process only new files
                files_to_process = [f[0] for f in new_files]
                chunks_added = process_documents(files_to_process, st.session_state.chroma_db)
                
                # Mark files as processed
                for file, file_hash in new_files:
                    st.session_state.processed_files.add(file_hash)
                
                st.session_state.document_count += chunks_added
                st.success(f"✅ Processed {len(new_files)} file(s) into {chunks_added} searchable chunks! You can now ask questions about your documents.")


def render_document_status():
    """Render document status message"""
    if st.session_state.document_count == 0:
        st.info(NO_DOCUMENTS_INFO)
    else:
        st.success(f"✅ {st.session_state.document_count} document chunks loaded | 📚 {len(st.session_state.processed_files)} file(s) uploaded")


def get_chat_input():
    """Get chat input from user"""
    return st.chat_input(CHAT_INPUT_PLACEHOLDER, key="chat_input")