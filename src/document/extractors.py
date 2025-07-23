import PyPDF2
import docx
import streamlit as st
from io import BytesIO
from src.config import CHUNK_SIZE


def extract_pdf_text(pdf_file):
    """Extract text from PDF file"""
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


def extract_docx_text(docx_file):
    """Extract text from DOCX file"""
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


def extract_text_from_file(file):
    """Extract text based on file type"""
    # Reset file pointer
    file.seek(0)
    
    if file.name.endswith('.pdf'):
        return extract_pdf_text(file)
    elif file.name.endswith('.docx'):
        return extract_docx_text(file)
    else:
        raise ValueError(f"Unsupported file type: {file.name}")