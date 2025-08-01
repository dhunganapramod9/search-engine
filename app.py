import os
import logging
from typing import List, Dict, Any, Optional
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from sentence_transformers import SentenceTransformer, util
from utils import load_documents, extract_text_from_file, sanitize_filename, extract_snippet
import secrets


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    DOCUMENTS_FOLDER = os.environ.get('DOCUMENTS_FOLDER', 'documents')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    MODEL_NAME = "all-MiniLM-L6-v2"
    MAX_SEARCH_RESULTS = 20
    MIN_SIMILARITY_SCORE = 0.1


class SearchEngine:
    
    def __init__(self, config: Config):
        self.config = config
        self.model = None
        self.documents = []
        self.filenames = []
        self.doc_embeddings = None
        self._initialize()
    
    def _initialize(self):
        try:
            logging.info("Loading sentence transformer model...")
            self.model = SentenceTransformer(self.config.MODEL_NAME)
            self.reload_documents()
            logging.info("Search engine initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize search engine: {e}")
            raise
    
    def reload_documents(self):
        try:
            self.documents, self.filenames = load_documents(self.config.DOCUMENTS_FOLDER)
            if self.documents:
                self.doc_embeddings = self.model.encode(self.documents, convert_to_tensor=True)
                logging.info(f"Loaded {len(self.documents)} documents")
            else:
                logging.warning("No documents found")
        except Exception as e:
            logging.error(f"Error loading documents: {e}")
            self.documents, self.filenames = [], []
            self.doc_embeddings = None
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        if not query.strip() or not self.documents:
            return []
        
        try:
            query_embedding = self.model.encode(query, convert_to_tensor=True)
            scores = util.cos_sim(query_embedding, self.doc_embeddings)[0]
            
            results = []
            for filename, content, score in zip(self.filenames, self.documents, scores):
                score_val = float(score)
                if score_val >= self.config.MIN_SIMILARITY_SCORE:
                    snippet = extract_snippet(content)
                    results.append({
                        "filename": filename,
                        "score": round(score_val * 100, 2),
                        "snippet": snippet
                    })
            
            # Sort by score and limit results
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:self.config.MAX_SEARCH_RESULTS]
            
        except Exception as e:
            logging.error(f"Error during search: {e}")
            return []
    
    def add_document(self, filename: str, content: str) -> bool:
        try:
            safe_filename = sanitize_filename(filename)
            filepath = os.path.join(self.config.DOCUMENTS_FOLDER, safe_filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Reload all documents to update embeddings
            self.reload_documents()
            logging.info(f"Added document: {safe_filename}")
            return True
            
        except Exception as e:
            logging.error(f"Error adding document {filename}: {e}")
            return False


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    
    # Initialize search engine
    search_engine = SearchEngine(config_class)
    
    @app.route("/", methods=["GET", "POST"])
    def index():
        results = []
        query = ""
        

        
        if request.method == "POST":
            query = request.form.get("query", "").strip()
            if query:
                results = search_engine.search(query)
                
                if not results:
                    flash("No matching documents found.", "info")
        
        return render_template(
            "index.html",
            results=results,
            query=query
        )
    
    @app.route("/document/<filename>")
    def view_document(filename: str):
        safe_filename = sanitize_filename(filename)
        filepath = os.path.join(app.config['DOCUMENTS_FOLDER'], safe_filename)
        
        if not os.path.exists(filepath):
            flash("Document not found.", "error")
            return redirect(url_for("index"))
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return render_template("document.html", filename=safe_filename, content=content)
        except Exception as e:
            logging.error(f"Error reading document {safe_filename}: {e}")
            flash("Error reading document.", "error")
            return redirect(url_for("index"))
    
    @app.route("/upload", methods=["POST"])
    def upload_file():
        if "file" not in request.files:
            flash("No file selected.", "error")
            return redirect(url_for("index"))
        
        file = request.files["file"]
        if not file or not file.filename:
            flash("No file selected.", "error")
            return redirect(url_for("index"))
        
        # Validate file type
        allowed_extensions = {'.txt', '.pdf', '.docx'}
        file_ext = os.path.splitext(file.filename.lower())[1]
        if file_ext not in allowed_extensions:
            flash("Only TXT, PDF, and DOCX files are allowed.", "error")
            return redirect(url_for("index"))
        
        try:
            content = extract_text_from_file(file)
            if not content.strip():
                flash("The uploaded file appears to be empty.", "warning")
                return redirect(url_for("index"))
            
            if search_engine.add_document(file.filename, content):
                flash(f"Successfully uploaded: {file.filename}", "success")
            else:
                flash("Error uploading file. Please try again.", "error")
                
        except Exception as e:
            logging.error(f"Error processing upload: {e}")
            flash("Error processing file. Please try again.", "error")
        
        return redirect(url_for("index"))
    

    
    @app.route("/api/search")
    def api_search():
        query = request.args.get("q", "").strip()
        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
        
        results = search_engine.search(query)
        return jsonify({"query": query, "results": results})
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template("error.html", error="Page not found"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logging.error(f"Internal error: {error}")
        return render_template("error.html", error="Internal server error"), 500
    
    return app


if __name__ == "__main__":
    app = create_app()
    # Use environment variables for production deployment
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
