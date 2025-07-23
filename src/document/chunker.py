from src.config import CHUNK_SIZE


def chunk_text(text, chunk_size=CHUNK_SIZE):
    """Split text into chunks of specified size"""
    chunks = []
    
    # Split content into chunks of chunk_size characters
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        if chunk.strip():  # Only add non-empty chunks
            chunks.append(chunk)
    
    return chunks


def chunk_pages(pages):
    """Process pages and split large pages into smaller chunks"""
    all_chunks = []
    
    for page in pages:
        content = page['content']
        chunks = chunk_text(content)
        
        # Create chunk entries with metadata
        for chunk_idx, chunk in enumerate(chunks):
            all_chunks.append({
                'content': chunk,
                'filename': page['filename'],
                'page': page['page'],
                'chunk_idx': chunk_idx
            })
    
    return all_chunks