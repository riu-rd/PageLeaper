import streamlit as st
import os
import time
import PyPDF2
import docx
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig
from google.api_core import retry, exceptions
from io import BytesIO
import hashlib

# Set page configuration
st.set_page_config(
    page_title="PageWise - Dashboard",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for responsive design and sticky bottom
st.markdown(
    """
    <style>
        /* Hide default sidebar navigation */
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
        
        /* Make main content area scrollable */
        .main .block-container {
            padding-bottom: 180px;
            max-height: calc(100vh - 180px);
            overflow-y: auto;
        }
        
        /* Sticky bottom container */
        .stBottom {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: white;
            padding: 1rem 2rem;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
            z-index: 999;
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            .stBottom {
                background-color: #0e1117;
            }
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-bottom: 200px;
            }
            .stBottom {
                padding: 0.5rem 1rem;
            }
        }
        
        /* Style file uploader */
        [data-testid="stFileUploader"] {
            margin-bottom: 0.5rem;
        }
        
        /* Right sidebar styling */
        .sidebar-content {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            height: 100%;
        }
        
        /* Dark mode sidebar */
        @media (prefers-color-scheme: dark) {
            .sidebar-content {
                background-color: #262730;
            }
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Check authentication status
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Access denied. Please log in on the main page.")
    st.switch_page("main.py")

# Initialize session states
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chat_session' not in st.session_state:
    st.session_state.chat_session = None
if 'chroma_db' not in st.session_state:
    st.session_state.chroma_db = None
if 'document_count' not in st.session_state:
    st.session_state.document_count = 0
if 'model_config' not in st.session_state:
    st.session_state.model_config = {
        'model': 'gemini-2.0-flash-exp',
        'temperature': 0.35,
        'top_k': 40,
        'top_p': 0.95
    }
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = set()
if 'show_sidebar' not in st.session_state:
    st.session_state.show_sidebar = False

# Constants
MAX_FILES = 5
CHUNK_SIZE = 1000  # Characters per chunk
BATCH_SIZE = 20  # Number of chunks to process at once

# Initialize Google Gemini client
@st.cache_resource
def init_gemini_client():
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Gemini Embedding Function for ChromaDB
class GeminiEmbeddingFunction(EmbeddingFunction):
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
                embedding_task = "retrieval_document"
            else:
                embedding_task = "retrieval_query"
            
            response = self.client.models.embed_content(
                model="models/text-embedding-004",
                contents=input,
                config=types.EmbedContentConfig(
                    task_type=embedding_task,
                ),
            )
            return [e.values for e in response.embeddings]
        except Exception as e:
            st.error(f"Embedding error: {str(e)}")
            # Return empty embeddings as fallback
            return [[0.0] * 768 for _ in input]  # type: ignore # 768 is the dimension of text-embedding-004

# Initialize ChromaDB
@st.cache_resource
def init_chromadb(_client):
    embed_fn = GeminiEmbeddingFunction(_client)
    chroma_client = chromadb.Client()
    db = chroma_client.get_or_create_collection(
        name="pagewise_docs",
        embedding_function=embed_fn
    )
    return db, embed_fn

# Extract text from PDF
def extract_pdf_text(pdf_file):
    pages_text = []
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file.read()))
        total_pages = len(pdf_reader.pages)
        
        for page_num in range(total_pages):
            try:
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                # Clean the text
                if text and text.strip():
                    # Remove excessive whitespace and clean up
                    text = ' '.join(text.split())
                    pages_text.append({
                        'page': page_num + 1,
                        'content': text,
                        'filename': pdf_file.name
                    })
            except Exception as e:
                st.warning(f"Could not extract text from page {page_num + 1} of {pdf_file.name}")
                continue
                
    except Exception as e:
        st.error(f"Error reading PDF {pdf_file.name}: {str(e)}")
    
    return pages_text

# Extract text from DOCX
def extract_docx_text(docx_file):
    pages_text = []
    try:
        doc = docx.Document(BytesIO(docx_file.read()))
        current_page = []
        page_num = 1
        char_count = 0
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                current_page.append(text)
                char_count += len(text)
                
                # Create a new page when we reach CHUNK_SIZE characters
                if char_count >= CHUNK_SIZE:
                    pages_text.append({
                        'page': page_num,
                        'content': '\n'.join(current_page),
                        'filename': docx_file.name
                    })
                    current_page = []
                    char_count = 0
                    page_num += 1
        
        # Add remaining content
        if current_page:
            pages_text.append({
                'page': page_num,
                'content': '\n'.join(current_page),
                'filename': docx_file.name
            })
    
    except Exception as e:
        st.error(f"Error reading DOCX {docx_file.name}: {str(e)}")
    
    return pages_text

# Process uploaded documents
def process_documents(uploaded_files, db):
    all_documents = []
    all_ids = []
    all_metadata = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, file in enumerate(uploaded_files):
        try:
            status_text.text(f"Processing {file.name}...")
            
            # Reset file pointer
            file.seek(0)
            
            # Extract text based on file type
            if file.name.endswith('.pdf'):
                pages = extract_pdf_text(file)
            elif file.name.endswith('.docx'):
                pages = extract_docx_text(file)
            else:
                continue
            
            # Process pages in smaller chunks
            for page in pages:
                # Split large pages into smaller chunks
                content = page['content']
                chunks = []
                
                # Split content into chunks of CHUNK_SIZE characters
                for i in range(0, len(content), CHUNK_SIZE):
                    chunk = content[i:i + CHUNK_SIZE]
                    if chunk.strip():  # Only add non-empty chunks
                        chunks.append(chunk)
                
                # Add each chunk as a separate document
                for chunk_idx, chunk in enumerate(chunks):
                    doc_id = hashlib.md5(
                        f"{file.name}_page_{page['page']}_chunk_{chunk_idx}".encode()
                    ).hexdigest()
                    all_documents.append(chunk)
                    all_ids.append(doc_id)
                    all_metadata.append({
                        'filename': file.name,
                        'page': page['page'],
                        'chunk': chunk_idx
                    })
            
            progress_bar.progress((idx + 1) / len(uploaded_files))
            
        except Exception as e:
            st.error(f"Error processing {file.name}: {str(e)}")
            continue
    
    # Add documents to ChromaDB in batches
    if all_documents:
        total_added = 0
        
        for i in range(0, len(all_documents), BATCH_SIZE):
            batch_docs = all_documents[i:i + BATCH_SIZE]
            batch_ids = all_ids[i:i + BATCH_SIZE]
            batch_metadata = all_metadata[i:i + BATCH_SIZE]
            
            try:
                db.add(
                    documents=batch_docs,
                    ids=batch_ids,
                    metadatas=batch_metadata
                )
                total_added += len(batch_docs)
                status_text.text(f"Indexed {total_added}/{len(all_documents)} chunks...")
            except Exception as e:
                st.error(f"Error indexing batch: {str(e)}")
                continue
    
    progress_bar.empty()
    status_text.empty()
    
    return len(all_documents)

# Search documents
def search_documents(query, db, embed_fn, n_results=5):
    embed_fn.document_mode = False
    results = db.query(query_texts=[query], n_results=n_results)
    embed_fn.document_mode = True
    
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

# Create main layout with optional right sidebar
if st.session_state.show_sidebar:
    main_col, sidebar_col = st.columns([3, 1])
else:
    main_col = st.container()
    sidebar_col = None

# Main content area
with main_col:
    # Create header with Exit button
    col1, col2, col3 = st.columns([10, 1, 1])
    with col1:
        st.title("PageWise")
        st.caption("Ask more, scroll less.")
    with col2:
        if st.button("🔧", key="config_button", help="Configurations"):
            st.session_state.show_sidebar = not st.session_state.show_sidebar
            st.rerun()
    with col3:
        if st.button("Exit", key="exit_button"):
            st.session_state.authenticated = False
            st.switch_page("main.py")

# Right sidebar for configurations
if sidebar_col is not None:
    with sidebar_col:
        st.markdown("### ⚙️ Configurations")
        st.divider()
        
        # Model selection
        model_option = st.radio(
            "Model",
            ["Faster", "Powerful"],
            index=0 if st.session_state.model_config['model'] == 'gemini-2.5-flash' else 1,
            key="model_radio"
        )
        new_model = 'gemini-2.5-flash' if model_option == "Faster" else 'gemini-2.5-pro'
        
        # Temperature
        new_temp = st.slider(
            "Temperature",
            min_value=0.1,
            max_value=1.5,
            value=st.session_state.model_config['temperature'],
            step=0.05,
            key="temp_slider"
        )
        
        # Top-K
        new_top_k = st.slider(
            "Top-K",
            min_value=1,
            max_value=500,
            value=st.session_state.model_config['top_k'],
            key="topk_slider"
        )
        
        # Top-P
        new_top_p = st.slider(
            "Top-P",
            min_value=0.00,
            max_value=1.00,
            value=st.session_state.model_config['top_p'],
            step=0.01,
            key="topp_slider"
        )
        
        # Check if configuration changed
        config_changed = (
            new_model != st.session_state.model_config['model'] or
            new_temp != st.session_state.model_config['temperature'] or
            new_top_k != st.session_state.model_config['top_k'] or
            new_top_p != st.session_state.model_config['top_p']
        )
        
        if config_changed:
            if st.button("Apply Changes", type="primary", key="apply_config"):
                st.session_state.model_config['model'] = new_model
                st.session_state.model_config['temperature'] = new_temp
                st.session_state.model_config['top_k'] = new_top_k
                st.session_state.model_config['top_p'] = new_top_p
                st.session_state.chat_session = None
                st.success("Configuration updated!")
                st.rerun()
        
        st.divider()
        
        # Clear documents option
        if st.button("Clear All Documents", type="secondary", key="clear_docs"):
            # Reset ChromaDB collection
            try:
                chroma_client = chromadb.Client()
                chroma_client.delete_collection("pagewise_docs")
            except:
                pass  # Collection might not exist
            st.session_state.chroma_db = None
            st.session_state.document_count = 0
            st.session_state.processed_files = set()
            st.session_state.messages = []  # Clear chat history
            st.session_state.chat_session = None  # Reset chat session
            st.success("All documents and chat history cleared!")
            st.rerun()

# Initialize services
client = init_gemini_client()
if st.session_state.chroma_db is None:
    db, embed_fn = init_chromadb(client)
    st.session_state.chroma_db = db
else:
    db = st.session_state.chroma_db
    embed_fn = GeminiEmbeddingFunction(client)

# Initialize chat session if needed
if st.session_state.chat_session is None:
    config = GenerateContentConfig(
        temperature=st.session_state.model_config['temperature'],
        top_k=st.session_state.model_config['top_k'],
        top_p=st.session_state.model_config['top_p']
    )
    st.session_state.chat_session = client.chats.create(
        model=st.session_state.model_config['model'],
        config=config
    )
    
    # Send initial message
    initial_message = """Hello! I'm PageWise, your comprehensive document understanding agent. 
    
I can analyze lengthy PDF and DOCX files to help you find information, answer questions, and gain insights from your documents. Simply upload your files using the button below, and then ask me anything about their content!

I'm ready to help you navigate through your documents efficiently. What would you like to know?"""
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": initial_message
    })

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Sticky bottom input section
bottom_container = st.container()
with bottom_container:
    st.markdown('<div class="stBottom">', unsafe_allow_html=True)
    
    # File uploader directly above chat input
    col1, col2 = st.columns([5, 1])
    with col1:
        uploaded_files = st.file_uploader(
            "📄 Drag and drop files here",
            type=['pdf', 'docx'],
            accept_multiple_files=True,
            key="file_uploader",
            help=f"Upload up to {MAX_FILES} PDF or DOCX files"
        )
    with col2:
        if st.session_state.document_count > 0:
            if st.button("🗑️", help="Clear all uploaded documents"):
                # Reset ChromaDB collection
                try:
                    chroma_client = chromadb.Client()
                    chroma_client.delete_collection("pagewise_docs")
                except:
                    pass
                st.session_state.chroma_db = None
                st.session_state.document_count = 0
                st.session_state.processed_files = set()
                st.session_state.messages = []  # Clear chat history
                st.session_state.chat_session = None  # Reset chat session
                st.rerun()
    
    user_input = st.chat_input(
        "Ask about your documents or chat with me...",
        key="chat_input"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Process uploaded files
if uploaded_files:
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
                chunks_added = process_documents(files_to_process, db)
                
                # Mark files as processed
                for file, file_hash in new_files:
                    st.session_state.processed_files.add(file_hash)
                
                st.session_state.document_count += chunks_added
                st.success(f"✅ Processed {len(new_files)} file(s) into {chunks_added} searchable chunks! You can now ask questions about your documents.")

# Handle user input
if user_input and st.session_state.document_count > 0:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with chat_container:
        with st.chat_message("user"):
            st.write(user_input)
    
    # Generate response
    with chat_container:
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            # Show loading with timer
            start_time = time.time()
            with st.spinner("Thinking..."):
                # Search for relevant documents
                contexts = search_documents(user_input, db, embed_fn)
                
                # Build prompt with context
                context_text = ""
                if contexts:
                    context_text = "\n\nRelevant document excerpts:\n"
                    for ctx in contexts:
                        chunk_info = f" - Chunk {ctx['chunk']}" if ctx.get('chunk', 0) > 0 else ""
                        context_text += f"\n[{ctx['filename']} - Page {ctx['page']}{chunk_info}]\n{ctx['content']}\n"
                
                prompt = f"""You are PageWise, a helpful document analysis assistant. Answer the user's question based on the provided document context. Be comprehensive but concise.

User Question: {user_input}

{context_text}

Please provide a clear and helpful answer based on the documents provided."""
                
                # Send message to Gemini
                response = st.session_state.chat_session.send_message(prompt)
                
                elapsed_time = time.time() - start_time
                
            # Display response
            response_placeholder.write(response.text)
            st.caption(f"Generated in {elapsed_time:.1f}s")
            
            # Add to messages
            st.session_state.messages.append({
                "role": "assistant",
                "content": response.text
            })

# Info message about document status
if st.session_state.document_count == 0:
    st.info("📄 Please upload PDF or DOCX files to start analyzing documents. You can upload up to 5 files at once.")
else:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success(f"✅ {st.session_state.document_count} document chunks loaded and ready for analysis!")
    with col2:
        st.info(f"📚 {len(st.session_state.processed_files)} file(s) uploaded")