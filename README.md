# Semantic Search Engine

A document search application I built for my machine learning class project. Instead of just matching keywords, it understands the meaning of your search using AI embeddings. You can upload different types of documents and search through them semantically.

## What it does

This project lets you search through documents based on meaning rather than exact keyword matches. I implemented it using Flask for the web interface and Sentence Transformers for the AI part.

### Main features

- Search documents by meaning using sentence embeddings
- Upload TXT, PDF, and DOCX files
- Get snippets from relevant documents with similarity scores
- Keep track of search history and favorite documents
- Simple web interface that works on mobile too

### Technical stuff I learned

- How to use pre-trained transformer models for semantic search
- Building a Flask web application with proper structure
- Handling file uploads and text extraction
- Session management and user interface design
- Basic security practices for web apps

## How I built it

**Backend**: Flask (Python web framework)
**AI Model**: Sentence Transformers (all-MiniLM-L6-v2 model)
**File processing**: PyPDF2 for PDFs, python-docx for Word docs
**Frontend**: HTML, CSS, and basic JavaScript
**Data storage**: Files on disk, sessions for user data

## Project structure

```
search-engine/
├── app.py                 # Main Flask application
├── utils.py              # Helper functions for document processing
├── static/
│   └── style.css         # Styling for the web interface
├── templates/
│   ├── index.html        # Main search page
│   ├── document.html     # Document viewer
│   └── error.html        # Error page
├── documents/            # Where uploaded documents are stored
│   ├── doc1.txt
│   ├── doc2.txt
│   └── doc3.txt
├── requirements.txt      # Python dependencies
└── README.md
```

## Setting it up

### What you need

- Python 3.8 or newer
- pip for installing packages

### Installation steps

1. **Download the code**

   ```bash
   git clone <repository-url>
   cd semantic-search-engine
   ```

2. **Set up a virtual environment** (recommended)

   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On Mac/Linux
   source venv/bin/activate
   ```

3. **Install the required packages**

   ```bash
   pip install -r requirements.txt
   ```

4. **Optional: Set environment variables**

   ```bash
   # Windows
   set SECRET_KEY=your-secret-key-here
   set DOCUMENTS_FOLDER=documents

   # Mac/Linux
   export SECRET_KEY=your-secret-key-here
   export DOCUMENTS_FOLDER=documents
   ```

5. **Run the application**

   ```bash
   python app.py
   ```

6. **Open in your browser**
   Go to `http://localhost:5000`

## Configuration options

You can customize the app using environment variables:

| Variable           | What it does                  | Default value  |
| ------------------ | ----------------------------- | -------------- |
| `SECRET_KEY`       | Secret key for Flask sessions | Auto-generated |
| `DOCUMENTS_FOLDER` | Where to store uploaded files | `documents`    |
| `FLASK_DEBUG`      | Enable debug mode             | `False`        |
| `PORT`             | Which port to run on          | `5000`         |

## How to use it

### Basic searching

1. Type your search query in the search box
2. Look at the results ranked by how similar they are
3. Click on document names to read the full content

### Uploading files

1. Click "Choose File" to pick a document
2. Supports TXT, PDF, and DOCX files (up to 16MB)
3. Click "Upload" to add it to the search index

### Other features

- Click the star to favorite documents for easy access later
- Your recent searches are saved automatically
- Use `/api/search?q=your-query` for programmatic access

## API endpoint

If you want to use this programmatically:

```
GET /api/search?q=<your query>
```

Returns JSON like this:

```json
{
  "query": "machine learning",
  "results": [
    {
      "filename": "ml_notes.txt",
      "score": 85.7,
      "snippet": "Machine learning is a subset of artificial intelligence..."
    }
  ]
}
```

## Running for development vs production

### For development

```bash
export FLASK_DEBUG=true
python app.py
```

### For production deployment

1. **Set production environment**

   ```bash
   export SECRET_KEY=your-production-secret-key
   export FLASK_DEBUG=false
   export PORT=8000
   ```

2. **Use a proper web server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

## What I learned from this project

- How semantic search works and why it's better than keyword matching
- Working with pre-trained AI models without training them myself
- Building a complete web application from scratch
- Handling different file formats and text extraction
- Making web interfaces that work well on different devices
- Basic security practices like input validation and file handling

## Challenges I faced

- Understanding how sentence transformers work and which model to use
- Figuring out efficient ways to handle document embeddings in memory
- Making the file upload feature secure and reliable
- Getting the CSS to look good on both desktop and mobile
- Learning proper Flask application structure

## Future improvements

If I continue working on this, I'd like to add:

- User accounts and authentication
- Better document management (delete, organize)
- Support for more file types
- Advanced search filters
- Document highlighting for matched sections

## Dependencies

All the Python packages needed are listed in `requirements.txt`. The main ones are:

- Flask for the web framework
- sentence-transformers for the AI model
- PyPDF2 and python-docx for file processing
- Standard libraries for everything else

## Contributing

This is a learning project, but if you find bugs or have suggestions, feel free to open an issue or submit a pull request.

## License

This project is open source under the MIT License.

---

Built as a machine learning class project using Flask and Sentence Transformers
