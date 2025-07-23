import streamlit as st
import hashlib
import os
from src.config import MAX_FILES, FILE_UPLOAD_HELP, CHAT_INPUT_PLACEHOLDER, NO_DOCUMENTS_INFO
from src.document.processor import process_documents
from src.chat.handler import handle_user_input


def render_header_main():
    st.title("PageWise")
    st.caption("Ask more, scroll less.")

def authenticate_user():
    """Handle authentication logic"""
    password = st.session_state.password_input
    correct_password = os.getenv("PASSWORD")
    
    if password == correct_password:
        st.session_state.authenticated = True
        st.rerun()
    else:
        st.session_state.auth_error = True

def render_authenticator():
    with st.container():
        password = st.text_input(
            "Password", 
            type="password", 
            key="password_input",
            on_change=authenticate_user
        )
        
        if hasattr(st.session_state, 'auth_error') and st.session_state.auth_error:
            st.error("Invalid password.")
            st.session_state.auth_error = False
        
        if st.button("Enter", use_container_width=True):
            authenticate_user()

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
        st.info(f"ℹ️ All {already_processed} file(s) have already been processed. You can ask questions about them above.")
    
    if new_files:
        if len(new_files) > MAX_FILES:
            st.error(f"Please upload a maximum of {MAX_FILES} files at a time.")
        else:
            with st.spinner(f"Processing {len(new_files)} new file(s)..."):
                # Process only new files
                files_to_process = [f[0] for f in new_files]
                chunks_added = process_documents(files_to_process, st.session_state.chroma_db)
                
                # Mark files as processed and store filenames
                for file, file_hash in new_files:
                    st.session_state.processed_files.add(file_hash)
                    if file.name not in st.session_state.uploaded_filenames:
                        st.session_state.uploaded_filenames.append(file.name)
                
                st.session_state.document_count += chunks_added
                st.success(f"✅ Processed {len(new_files)} file(s) into {chunks_added} searchable chunks! You can now ask questions about your documents.")
                st.rerun()


def render_document_status():
    """Render document status message"""
    if st.session_state.document_count == 0:
        st.info(NO_DOCUMENTS_INFO)
    else:
        st.success(f"✅ {st.session_state.document_count} document chunks loaded | 📚 {len(st.session_state.processed_files)} file(s) uploaded")


def generate_sample_prompts(filenames):
    """Generate context-aware sample prompts based on uploaded filenames"""
    prompts = []
    
    for filename in filenames:
        if "annual report" in filename.lower() or "report" in filename.lower():
            prompts.append(f"Summarize the key financial takeaways from {filename}")
        elif "contract" in filename.lower() or "agreement" in filename.lower():
            prompts.append(f"What are the main terms and conditions in {filename}?")
        elif "research" in filename.lower() or "study" in filename.lower():
            prompts.append(f"What are the key findings and conclusions in {filename}?")
        elif "manual" in filename.lower() or "guide" in filename.lower():
            prompts.append(f"What are the main procedures outlined in {filename}?")
        elif "policy" in filename.lower():
            prompts.append(f"What are the key policy requirements in {filename}?")
        elif "invoice" in filename.lower() or "receipt" in filename.lower():
            prompts.append(f"What are the payment details and amounts in {filename}?")
        elif "proposal" in filename.lower():
            prompts.append(f"What are the main objectives and benefits outlined in {filename}?")
        elif "specification" in filename.lower() or "spec" in filename.lower():
            prompts.append(f"What are the technical requirements in {filename}?")
        else:
            # Generic prompts based on file type
            if filename.endswith('.pdf') or filename.endswith('.docx'):
                prompts.append(f"What are the main topics covered in {filename}?")
    
    # Add some generic prompts if we have multiple files
    if len(filenames) > 1:
        prompts.append("Compare the key themes across all uploaded documents")
        prompts.append("What common information appears in multiple documents?")
    
    # Limit to 4 prompts to avoid cluttering the UI
    return prompts[:4]


def render_sample_prompts(chat_container):
    """Render sample prompt buttons when documents are uploaded"""
    # Check if we have documents loaded (either from filenames or processed files)
    has_documents = (bool(st.session_state.uploaded_filenames) or 
                    st.session_state.document_count > 0 or 
                    len(st.session_state.processed_files) > 0)
    
    user_has_not_chatted = len(st.session_state.messages) <= 1
    
    # Show sample prompts if we have documents and haven't started chatting yet
    # (1 message = initial greeting, 2+ messages = user has started chatting)
    if has_documents and user_has_not_chatted:
        st.markdown("### Get Started")
        st.markdown("Try these questions about your documents:")
        
        # Use uploaded_filenames if available, otherwise generate generic prompts
        if st.session_state.uploaded_filenames:
            sample_prompts = generate_sample_prompts(st.session_state.uploaded_filenames)
        else:
            # Generate generic prompts when we have documents but no specific filenames yet
            sample_prompts = [
                "What are the main topics covered in the uploaded documents?",
                "Summarize the key information from the documents",
                "What are the most important points in these documents?",
                "Can you provide an overview of the document contents?"
            ]
        
        cols = st.columns(2)
        
        for i, prompt in enumerate(sample_prompts):
            col = cols[i % 2]
            with col:
                if st.button(prompt, key=f"sample_prompt_{i}", use_container_width=True):
                    handle_user_input(prompt, chat_container)
                    st.rerun()


def get_chat_input():
    """Get chat input from user"""
    return st.chat_input(CHAT_INPUT_PLACEHOLDER, key="chat_input")