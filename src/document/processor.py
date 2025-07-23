import hashlib
import streamlit as st
from src.config import BATCH_SIZE, CHUNK_SIZE
from .extractors import extract_text_from_file
from .chunker import chunk_text


def process_documents(uploaded_files, db):
    """Process uploaded documents and add to ChromaDB"""
    all_documents = []
    all_ids = []
    all_metadata = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, file in enumerate(uploaded_files):
        try:
            status_text.text(f"Processing {file.name}...")
            
            # Extract text based on file type
            pages = extract_text_from_file(file)
            
            # Process pages in smaller chunks
            for page in pages:
                # Split large pages into smaller chunks
                content = page['content']
                chunks = chunk_text(content, CHUNK_SIZE)
                
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