# PageLeaper

*Skip the reading, get the knowledge.*

## Overview

PageLeaper is an intelligent document processing application that leverages advanced AI capabilities to extract, analyze, and provide insights from large volumes of PDF and DOCX documents. Built with Streamlit and powered by Google's Gemini AI, it implements Retrieval-Augmented Generation (RAG) to enable intelligent querying of uploaded documents.

The application is deployed via Google Cloud Run and is accessible at: https://pageleaper-431714973110.asia-southeast1.run.app

## Purpose and Use Cases

PageLeaper transforms how users interact with extensive document collections by:

- **Academic Research**: Process multiple research papers, textbooks, or academic materials to quickly extract relevant information
- **Legal Document Analysis**: Navigate through contracts, agreements, and legal documentation efficiently
- **Business Intelligence**: Analyze reports, proposals, and business documents for quick decision-making
- **Knowledge Management**: Create searchable knowledge bases from organizational documents
- **Content Summarization**: Generate concise summaries and insights from lengthy documents

## Key Features

### 1. **Text Extraction and Processing**
- Supports PDF and DOCX file formats
- Robust text extraction with error handling
- Maintains document structure and formatting context

### 2. **Intelligent Chunking**
- Documents are split into manageable chunks for optimal processing
- Preserves semantic coherence within chunks
- Configurable chunk sizes based on use case

### 3. **Vectorization and RAG Implementation**
- Converts text chunks into high-dimensional embeddings
- Utilizes ChromaDB for efficient vector storage and retrieval
- Implements semantic search for contextually relevant information retrieval

### 4. **Interactive Chat Interface**
- Natural language querying of uploaded documents
- Context-aware responses using RAG
- Maintains conversation history for coherent interactions

### 5. **Intelligent Sample Prompts**
- "Get Started" feature with context-aware prompt suggestions
- Helps users understand document capabilities quickly
- Dynamically generated based on uploaded content

### 6. **Multiple Document Upload**
- Process multiple files simultaneously
- Cross-document querying and analysis
- Unified knowledge base from diverse sources

### 7. **Configurable LLM Parameters**
- Adjustable model temperature for response creativity
- Model selection options for different use cases

## Architecture

### High-Level System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                    (Streamlit Web Application)                  │
├─────────────────────────────────────────────────────────────────┤
│                         Frontend Layer                          │
│  ┌─────────────┐  ┌───────────────┐  ┌────────────────────┐     │
│  │   main.py   │  │ 1_dashboard.py│  │  UI Components     │     │
│  │(Entry Point)│  │ (Main App)    │  │    (src/ui)        │     │
│  └─────────────┘  └───────────────┘  └────────────────────┘     │
├─────────────────────────────────────────────────────────────────┤
│                       Application Flow Layer                    │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐      │
│  │    Auth     │  │  Gemini Chat │  │      Document      │      │
│  │ (src/auth)  │  │  (src/chat)  │  │     Processing     │      │
│  └─────────────┘  └──────────────┘  │   (src/document)   │      │
│                                     └────────────────────┘      │
├─────────────────────────────────────────────────────────────────┤
│                        Data Layer                               │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐      │
│  │  Embedding  │  │   ChromaDB   │  │      Google        │      │
│  │   Engine    │  │Vector Store  │  │     Embedding      │      │
│  │(src/embed..)│  │(src/embed..) │  │   (src/embed..)    │      │
│  └─────────────┘  └──────────────┘  └────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
ML_Eng_Exam/
├── main.py                    # Application entry point with authentication
├── Dockerfile                 # Docker configuration for deployment
├── LICENSE                    # MIT License file
├── README.md                  # Project documentation
├── ProjectJournal.md          # Development journal with design decisions and challenges
├── requirements.txt           # Python dependencies
├── pages/
│   └── 1_dashboard.py        # Main dashboard interface
├── src/
│   ├── auth/
│   │   ├── __init__.py
│   │   └── session.py        # Authentication and session management
│   ├── chat/
│   │   ├── __init__.py
│   │   ├── handler.py        # Chat message handling and processing
│   │   └── session.py        # Chat session initialization
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py       # Application configuration and constants
│   ├── document/
│   │   ├── __init__.py
│   │   ├── chunker.py        # Text chunking for embeddings
│   │   ├── extractors.py     # Text extraction from PDF/DOCX
│   │   └── processor.py      # Document processing pipeline
│   ├── embedding/
│   │   ├── __init__.py
│   │   ├── chromadb.py       # ChromaDB vector store operations
│   │   └── gemini.py         # Google Gemini embedding integration
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── components.py     # Reusable UI components
│   │   ├── sidebar.py        # Configuration sidebar
│   │   └── styles.py         # Custom CSS styling
│   └── utils/
│       ├── __init__.py
│       └── helpers.py        # Utility functions and Gemini client
└── test_docs/
    ├── 2023_Annual_Report.docx  # Sample DOCX document for testing
    └── 2023_Annual_Report.pdf   # Sample PDF document for testing
```

## File Descriptions

### Root Files

- **`main.py`**: Entry point for the Streamlit application. Handles initial page configuration, authentication state management, and routing to the dashboard.

- **`Dockerfile`**: Docker configuration for containerized deployment to cloud platforms.

- **`LICENSE`**: MIT License file for the project.

- **`README.md`**: This file - comprehensive project documentation.

- **`ProjectJournal.md`**: A comprehensive journal detailing design decisions, challenges faced, solutions implemented, and prompt engineering strategies throughout the development process.

- **`requirements.txt`**: Lists all Python dependencies required for the project, including ChromaDB SQLite fixes.

### Pages Directory

- **`pages/1_dashboard.py`**: Main application interface containing the chat functionality, document upload, configuration options, and sample prompt generation. Manages the core user experience.

### Source Directory (src/)

#### Authentication Module (src/auth/)

- **`session.py`**: Implements authentication logic, session state management, and session reset functionality.

#### Chat Module (src/chat/)

- **`handler.py`**: Manages chat message processing, document query handling, and prompt building with context.

- **`session.py`**: Handles Gemini chat session initialization with configurable parameters.

#### Configuration Module (src/config/)

- **`settings.py`**: Central configuration file containing application constants, model options, UI text, and prompt templates.

#### Document Module (src/document/)

- **`chunker.py`**: Implements intelligent text chunking strategies for optimal embedding and retrieval.

- **`extractors.py`**: Extracts text content from PDF and DOCX files with appropriate error handling.

- **`processor.py`**: Document processing pipeline that coordinates extraction, chunking, and embedding operations.

#### Embedding Module (src/embedding/)

- **`chromadb.py`**: ChromaDB vector store operations including initialization, document storage, and similarity search.

- **`gemini.py`**: Google Gemini embedding integration for converting text to vectors.

#### UI Module (src/ui/)

- **`components.py`**: Reusable UI components including authentication, file upload, chat interface, and dynamic sample prompts.

- **`sidebar.py`**: Configuration sidebar with model parameter controls and session management.

- **`styles.py`**: Custom CSS styles for the Streamlit interface.

#### Utilities Module (src/utils/)

- **`helpers.py`**: Utility functions including Gemini client initialization and helper methods.

### Test Documents

- **`test_docs/`**: Sample PDF and DOCX files for testing document processing and analysis capabilities.

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Google Gemini API key

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/pageleaper.git
cd pageleaper
```

### Step 2: Set Up Python Environment

#### Using Python venv

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

#### Using Conda

```bash
# Create conda environment
conda create -n pageleaper python=3.8

# Activate environment
conda activate pageleaper
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file and add your credentials
# GEMINI_API_KEY=your_gemini_api_key_here
# PASSWORD=your_chosen_password
```

### Step 5: Run the Application

```bash
streamlit run main.py
```

The application will start and be accessible at `http://localhost:8501`

## Deployment

PageLeaper is deployed on Google Cloud Platform using Cloud Run, providing:
- Automatic scaling based on traffic
- HTTPS encryption
- Global accessibility
- Containerized deployment

Access the live application at: https://pageleaper-431714973110.asia-southeast1.run.app

## Technologies Used

- **Streamlit**: Web application framework for the user interface
- **Google Gemini API**: AI-powered language model for chat responses and document embeddings
- **ChromaDB**: Vector database for storing and searching document embeddings
- **PyPDF2**: PDF text extraction library
- **python-docx**: DOCX document processing library
- **Python-dotenv**: Environment variable management
- **Google Cloud Run**: Serverless deployment platform

## Key Resources

This project was developed with reference to the following resources:

- **[Streamlit Documentation](https://docs.streamlit.io/)**: Official documentation for building data applications
- **[ChromaDB Practice Notebook](https://www.kaggle.com/code/dariusardales/day-2-document-q-a-with-rag?scriptVersionId=252127726)**: Implementation examples for document Q&A with RAG
- **[Gemini Practice Notebook](https://github.com/riu-rd/PRACTICE-AI/tree/main/9-Google/Introduction%20to%20Gemini%202.5%20Pro)**: Introduction to Gemini 2.5 Pro capabilities
- **[Embedding Practice Notebook](https://www.kaggle.com/code/dariusardales/day-2-embeddings-and-similarity-scores?scriptVersionId=252127997)**: Understanding embeddings and similarity scores

## Acknowledgments

Created with the assistance of Anthropic Claude, leveraging advanced AI capabilities to streamline development and enhance functionality.

## License

This project is licensed under the MIT License - see the LICENSE file for details.