import time
import streamlit as st
from src.embedding.chromadb import search_documents
from src.config import PROMPT_TEMPLATE


def handle_user_input(user_input, chat_container):
    """Handle user chat input and generate response"""
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with chat_container:
        with st.chat_message("user"):
            st.write(user_input)
    
    with chat_container:
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            # Show loading with timer
            start_time = time.time()
            with st.spinner("Thinking..."):
                if st.session_state.document_count == 0:
                    # Handle chat without documents
                    response = st.session_state.chat_session.send_message(user_input)
                else:
                    # Handle chat with document context
                    response = handle_document_query(user_input)
                
                elapsed_time = time.time() - start_time
            
            response_placeholder.write(response.text)
            st.caption(f"Generated in {elapsed_time:.1f}s")
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": response.text
            })


def handle_document_query(user_input):
    """Handle query with document context"""
    # Search for relevant documents
    contexts = search_documents(
        user_input, 
        st.session_state.chroma_db, 
        st.session_state.embed_fn
    )
    
    # Build prompt with context
    prompt = build_prompt_with_context(user_input, contexts)
    
    # Send message to Gemini
    return st.session_state.chat_session.send_message(prompt)


def build_prompt_with_context(user_input, contexts):
    """Build prompt with document context"""
    context_text = ""
    
    # Build document info for the system prompt
    processed_files = st.session_state.processed_files
    document_count = st.session_state.document_count
    
    # Get unique filenames from processed files (simplified approach)
    file_names = []
    if contexts:
        unique_files = set()
        for ctx in contexts:
            unique_files.add(ctx['filename'])
        file_names = list(unique_files)
    
    if file_names:
        document_info = f"You have access to {len(file_names)} document(s) in this session: {', '.join(file_names)}. Total document chunks available: {document_count}. "
    else:
        document_info = f"You have access to {len(processed_files)} document(s) in this session with {document_count} total chunks available. "
    
    if contexts:
        context_text = "\n\nRelevant document excerpts:\n"
        for ctx in contexts:
            chunk_info = f" - Chunk {ctx['chunk']}" if ctx.get('chunk', 0) > 0 else ""
            context_text += f"\n[{ctx['filename']} - Page {ctx['page']}{chunk_info}]\n{ctx['content']}\n"
    
    return PROMPT_TEMPLATE.format(
        document_info=document_info,
        user_question=user_input,
        context_text=context_text
    )