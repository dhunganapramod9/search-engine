import logging
import time
from typing import Optional
from uuid import uuid4

from flask import Flask, g, jsonify, request

from config import Config
from services.ingest import IngestService
from services.jobs import JobService
from services.search import SearchService, SentenceTransformerEmbedder
from services.storage import StorageService
from utils.files import is_allowed_extension
from openapi import get_openapi_spec


def _build_services(config: Config, embedder=None):
    embedder = embedder or SentenceTransformerEmbedder(config.model_name)
    storage_service = StorageService(config.database_path)
    ingest_service = IngestService(
        storage_service=storage_service,
        embedder=embedder,
        uploads_dir=config.uploads_dir,
        max_chunk_size=config.max_chunk_size,
        chunk_overlap=config.chunk_overlap,
    )
    search_service = SearchService(storage_service=storage_service, embedder=embedder)
    job_service = JobService(
        storage_service=storage_service,
        ingest_service=ingest_service,
        max_workers=config.ingestion_workers,
    )
    return storage_service, ingest_service, search_service, job_service


def create_app(config: Optional[Config] = None, embedder=None) -> Flask:
    config = config or Config()
    config.ensure_runtime_dirs()

    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = config.max_content_length

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    storage_service, ingest_service, search_service, job_service = _build_services(config, embedder=embedder)

    @app.before_request
    def before_request():
        g.request_id = request.headers.get("X-Request-ID", str(uuid4()))
        g.start_time = time.perf_counter()

    @app.after_request
    def after_request(response):
        elapsed_ms = (time.perf_counter() - g.start_time) * 1000
        response.headers["X-Request-ID"] = g.request_id
        logging.info(
            "request_id=%s method=%s path=%s status=%s latency_ms=%.2f",
            g.request_id,
            request.method,
            request.path,
            response.status_code,
            elapsed_ms,
        )
        return response

    @app.get("/")
    def index():
        return jsonify(
            {
                "name": config.app_name,
                "message": "Use /documents to upload files and /search?q=... to query indexed content.",
                "docs": "/docs",
            }
        )

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/openapi.json")
    def openapi_spec():
        return jsonify(get_openapi_spec())

    @app.get("/docs")
    def docs():
        return """
        <!doctype html>
        <html>
          <head>
            <title>Semantic Search API Docs</title>
            <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
          </head>
          <body>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
            <script>
              window.ui = SwaggerUIBundle({url: '/openapi.json', dom_id: '#swagger-ui'});
            </script>
          </body>
        </html>
        """

    @app.post("/documents")
    def upload_document():
        if "file" not in request.files:
            return jsonify({"error": "Missing multipart file field named 'file'."}), 400

        uploaded = request.files["file"]
        if not uploaded or not uploaded.filename:
            return jsonify({"error": "File is required."}), 400
        if not is_allowed_extension(uploaded.filename):
            return jsonify({"error": "Unsupported file type. Allowed: .txt, .pdf, .docx"}), 400

        payload = uploaded.read()
        if not payload:
            return jsonify({"error": "Uploaded file is empty."}), 400

        try:
            job = job_service.create_ingestion_job(uploaded.filename, payload)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            logging.exception("Unexpected ingestion failure")
            return jsonify({"error": "Failed to queue ingestion job."}), 500
        return jsonify(job), 202

    @app.get("/jobs/<string:job_id>")
    def get_job(job_id: str):
        job = job_service.get_job(job_id)
        if not job:
            return jsonify({"error": "Job not found."}), 404
        return jsonify(job)

    @app.get("/documents/<int:document_id>")
    def get_document(document_id: int):
        document = storage_service.get_document(document_id)
        if not document:
            return jsonify({"error": "Document not found."}), 404
        return jsonify(document)

    @app.get("/search")
    def search():
        query = (request.args.get("q") or "").strip()
        if not query:
            return jsonify({"error": "Query parameter 'q' is required."}), 400
        top_k = min(max(int(request.args.get("top_k", config.max_search_results)), 1), 100)
        min_score = float(request.args.get("min_score", config.min_similarity_score))

        try:
            results = search_service.hybrid_search(
                query=query,
                limit=top_k,
                min_score=min_score,
                semantic_weight=config.hybrid_semantic_weight,
                lexical_weight=config.hybrid_lexical_weight,
                rerank_top_k=config.rerank_top_k,
            )
        except Exception:
            logging.exception("Search failed")
            return jsonify({"error": "Search failed."}), 500
        return jsonify({"query": query, "count": len(results), "results": results, "mode": "hybrid"})

    @app.errorhandler(413)
    def payload_too_large(_):
        return jsonify({"error": f"File exceeds max size of {config.max_content_length} bytes."}), 413

    return app


if __name__ == "__main__":
    runtime_config = Config()
    flask_app = create_app(runtime_config)
    flask_app.run(host="0.0.0.0", port=runtime_config.port, debug=runtime_config.flask_debug)
