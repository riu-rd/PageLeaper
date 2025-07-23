# PageLeaper Development Journal

## Initial Excitement and Vision

When I first saw the exam instructions, I immediately felt excited. One of my study goals was to further utilize my knowledge gained from the Google AI School and the Google Gen AI Intensive Course in a practical manner. The instructions were the best way to try out the different use cases and capabilities of Gemini. 

Looking at the specifications, I could see I could also use what I learned about ChromaDB for vectorization and RAG, plus text embedding models from Google for embedding extracted text from documents. For more context, here are my code playgrounds where I practiced:
- [Embedding models and similarity scores](https://www.kaggle.com/code/dariusardales/day-2-embeddings-and-similarity-scores?scriptVersionId=252127997)
- [Document Q&A with RAG using ChromaDB](https://www.kaggle.com/code/dariusardales/day-2-document-q-a-with-rag?scriptVersionId=252127726)
- [Exploring Gemini's capabilities with chat sessions and multimodality](https://github.com/riu-rd/PRACTICE-AI/tree/main/9-Google/Introduction%20to%20Gemini%202.5%20Pro)

## Technology Stack Decisions

As I began thinking about the application, I immediately thought about what technologies I would use. I wanted to keep it simple but still very effective in delivering its task. 

### Document Processing Libraries
I mainly decided on:
- **python-docx** for processing DOCX files based on [this comprehensive guide](https://medium.com/@HeCanThink/python-docx-a-comprehensive-guide-to-creating-and-manipulating-word-documents-in-python-a765cf4b4cb9)
- **PyPDF2** for simple text extraction from PDFs, as I read about in [this analysis](https://medium.com/@uaqureshi_61924/is-pypdf2-the-best-option-extracting-hyperlinks-from-pdfs-a-deep-dive-026fa9cd2518)

### Core AI Components
Of course, I immediately thought of using Google's text embedding model + ChromaDB for powerful RAG and Vector Database functionality, as I've learned and used before. I chose Gemini as my main LLM provider over other options mainly because:
- It's the one I have the most experience with
- I wanted to showcase my knowledge from the Google Gen AI Intensive Course

I also considered using LangChain's [ChatGoogleGenerativeAI](https://python.langchain.com/docs/integrations/chat/google_generative_ai/) as a wrapper for more control in state and memory management. However, I wanted to keep the app simple. I didn't want multiple chat sessions, so Gemini's API with its built-in session creator was enough for a straightforward and robust mechanism for managing a single chat history and making the model able to handle follow-up questions and maintain context.

## Learning Streamlit and Deployment Challenges

I didn't really have much experience with Streamlit. I hadn't thought of using it in my previous projects, so I was initially nervous about it. However, after watching a [quick tutorial video](https://www.youtube.com/watch?v=D0D4Pa22iG0), I realized it's really mostly just a frontend framework in Python. I was easily able to adapt to using it.

### Deployment Pivot
During deployment to Streamlit's cloud, I encountered a small error that doesn't allow ChromaDB during deployment (see [this discussion](https://discuss.streamlit.io/t/issues-with-chroma-and-sqlite/47950)). To mitigate this, I pivoted to using Cloud Run from GCP instead, following [this tutorial](https://www.youtube.com/watch?v=BGMdxpXsbB4). It worked flawlessly, and that's basically it for setting up the initial tech stack.

## Application Architecture

### Authentication Layer
Creating the main page for the app, I decided to put a simple password authentication. Since I'm deploying it, I'm trying to at least prevent unwanted use of my Gemini API so it won't be misused and exhausted. If you're reading this, the password of the app is "GENAI" so you can access it.

### Main Dashboard
The real deal is in `pages/1_dashboard.py`, which houses the main operations of the app. But before I proceed to that, I'd just like to acknowledge that the app was made with a lot of help from Anthropic's Claude, and this journal is also re-edited by Claude (building on top of what I write).

## Document Processing Implementation

First, I decided which file types are supported. Even though the instructions say PDF, I figured I could also include DOCX. At a high level overview (as can be seen in `src/document`), I extracted text using the usual algorithms for PyPDF2 and python-docx.

### Chunking Strategy
- I specified a chunk size (number of characters for a "page")
- Added basic cleaning like removing excessive whitespace
- Each chunk is added as a separate document
- Documents are added to ChromaDB in batches to prevent limit errors from Google's APIs

### Cross-Document Analysis
With this method, when multiple documents are uploaded, all documents are processed together and their chunks are mixed inside a single collection in ChromaDB. The reasoning for this is to allow cross-document analysis – we could somehow make the model try to relate multiple documents when answering queries.

### Document Management Simplification
I didn't deal much with adding and deleting documents. I simplified it so you can keep adding documents, but if you want to remove a document from the knowledge base, you need to create a new session. I structured it this way because:
- It was challenging for me to navigate through the ChromaDB states
- Sometimes ChromaDB would try to access a non-existing collection

### Why Vectorization?
Why use ChromaDB and vectorization? Mainly because this model is designed to accept huge files – PDFs or DOCX with multiple pages. The model would have a hard time going through it if it was given as is.

## Chat Implementation and Prompt Engineering

For the chat portion, I tried to structure it in a way that would rely on Gemini's straightforward chat session API. The way I start it is with a fixed initial message from the agent as seen in `src/config`.

### Prompt Template Strategy
I set up a prompt template that essentially contains both the system prompt and the actual prompt. I know this would cost more tokens; however, I found this method the best so that the model always adapts to the documents uploaded as they could change anytime. It would be challenging to update a system prompt given time constraints and lack of exploration time.

The prompt template follows this structure:
```
"""You are PageLeaper, a helpful document analysis assistant. {document_info}Answer the user's question based on the provided document context. Be comprehensive but concise.

User Question: {user_question}

{context_text}

Please provide a clear and helpful answer based on the documents provided."""
```

This template includes:
- **document_info**: Can dynamically update
- **user_question**: If there already is one
- **context_text**: The most related pages/documents gathered by the RAG functionality

The prompting follows the simple strategy of ROLE/PURPOSE/CONTEXT → QUESTION → EXAMPLES/RAG OUTPUTS.

### Context Structure and Chat Handler
The context_text in the prompt template is structured as follows:
```python
contexts.append({
    'content': doc,
    'filename': metadata.get('filename', 'Unknown'),
    'page': metadata.get('page', 'Unknown'),
    'chunk': metadata.get('chunk', 0)
})
```

The chat handler uses this structure to retrieve context based on the vectorized user query. When a user asks a question, the handler:
1. Vectorizes the user query using the embedding model
2. Searches ChromaDB for the most relevant chunks
3. Formats the retrieved contexts with their metadata (filename, page, chunk)
4. Includes this structured context in the prompt template

This approach ensures the model receives relevant document sections along with their source information, enabling accurate and traceable responses. The structuring is straightforward and designed primarily for context purposes, with minimal additional prompting to let the model focus on the actual content.

### Flexible Input Handling
I structured the handling of user input to maintain the app's capability for usual chatbot functionality. When no documents are uploaded, the system handles raw user input directly without the prompt template, preserving standard conversational AI features. However, when documents are present, it uses the structured template with context retrieval. This design ensures the app doesn't lose its general chatbot capabilities while providing enhanced document analysis when needed.

### Dynamic Prompt Suggestions
I added functionality where if the user uploads documents and isn't chatting with the model yet, there would be dynamic suggested prompts. It's located in `src/ui/components.py` in the `generate_sample_prompts(filenames)` function. 

I implemented this in a rule-based format for now, trying to get keywords from the filenames. Given the time constraints, it would be challenging to somehow try to fetch a random chunk from a document (since they're already mixed) and use that chunk to dynamically generate a prompt for the user to try out. I found this simple rule-based prompt suggester working well, and it also showcases that I can do decent prompt engineering based on certain context.

There are also further sample prompts located in `render_sample_prompts(chat_container)`.

## Model Configuration Features

I tried to add functionality for changing LLM model parameters:

### Model Selection
Users can choose between:
- **Gemini 2.5 Flash**: Optimized for speed
- **Gemini 2.5 Pro**: Has robust thinking functionality, making it more careful and accurate

This lets users choose between fast but less powerful or slow but more powerful options.

### Parameter Adjustments
I added controls for:
- **Temperature**: Control randomness
- **Top-p**: Control diversity
- **Top-k**: Control vocabulary selection

Users can adjust these as they see fit, making the model more factual or more creative.

## Final Thoughts

Overall, this is really just a simple app showcasing the capabilities of LLMs like Gemini combined with embedding models and vector databases like ChromaDB for long context understanding for documents. 

I do believe this can be further improved with better extractions and cleaning of documents using other products like Google's Document AI. 

Lastly, I hope that people who read this will like the implementation and have fun reading this journal!