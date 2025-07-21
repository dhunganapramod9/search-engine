# Semantic Search Engine

This is a personal document search engine I built using Flask and Sentence Transformers. It helps find documents based on meaning, not just exact keyword matches. I added file upload support, document previews, score visualization, search history, and a way to mark favorites.

-Features

- Semantic search with sentence embeddings
- Preview the first matching line from each result
- Color-coded relevance score bars
- View full content of each document
- Upload `.txt`, `.pdf`, or `.docx` files
- Session-based search history and favorites
- (Optional) Smart answer generator using OpenAI

search-engine/
├── app.py                # Flask backend app – handles routes, queries, and model interaction
├── utils.py              # Utility to load and preprocess documents from /documents
├── documents/            # Folder to store text documents to be indexed and searched
│   ├── doc1.txt
│   ├── doc2.txt
│   └── ...               # Add more plain text files here
├── templates/            # HTML templates rendered by Flask
│   ├── index.html        # Main search interface with form
│   └── document.html     # Full document view template




## Setup Instructions

1. Clone the repository

  git clone https://github.com/your-username/semantic-search-engine.git
  cd semantic-search-engine


2 Install dependencies

  pip install flask sentence-transformers openai python-docx PyPDF2
  (Optional) Set your OpenAI API key


  export OPENAI_API_KEY=your_key_here
  Run the application

  python app.py
  Open in browser

  http://127.0.0.1:5000

Notes
        Uploaded files are saved in the documents/ folder

        Search history and favorites are stored in the session

        OpenAI integration is optional; the app works without it
        

Why I Made This

I wanted a simple way to search through my own documents without needing exact keywords. Adding semantic search
and file upload made it way more useful. It’s a lightweight tool I can build on later or integrate into other 
projects.


