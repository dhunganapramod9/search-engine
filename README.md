# Semantic Document Search Engine (Flask)

This project is a backend-first semantic search API for uploaded documents. It ingests TXT, PDF, and DOCX files asynchronously, extracts and chunks text, creates vector embeddings, and returns hybrid-ranked search results with snippets. The codebase is intentionally compact and structured to highlight API design, ingestion pipelines, ranking quality, persistence, and operational reliability.

## Key Backend Features

- Flask REST API with clear endpoint contracts and JSON responses
- Asynchronous ingestion jobs (`queued` -> `processing` -> `completed/failed`)
- Hybrid retrieval (semantic + lexical) with reranking
- Text normalization and chunking for retrieval quality
- Semantic ranking with Sentence Transformers embeddings plus score breakdown
- SQLite persistence for document metadata and chunk index
- Structured request logging with request IDs and latency tracking
- OpenAPI contract (`/openapi.json`) + Swagger UI (`/docs`)
- Evaluation harness for `precision@k` and `MRR`
- Production-minded validation and error handling
- Pytest suite covering ingestion, extraction, search, and API behavior

## Architecture Overview

```text
search-engine/
  app.py
  config.py
  services/
    ingest.py
    jobs.py
    search.py
    storage.py
  openapi.py
  scripts/
    evaluate.py
  eval/
    sample_queries.json
  utils/
    files.py
    text_processing.py
  tests/
    test_ingest.py
    test_file_extraction.py
    test_search.py
    test_api.py
  uploads/      # runtime, gitignored
  data/         # runtime, gitignored
```

Data flow:
1. `POST /documents` creates an ingestion job and returns a `job_id`.
2. Job pipeline extracts text, normalizes/chunks it, creates embeddings, and persists indexed chunks in SQLite.
3. `GET /jobs/<id>` exposes status and resulting `document_id`.
4. `GET /search` runs hybrid retrieval and reranking for ranked snippets.

## API Endpoints

### `POST /documents`
Queue an async ingestion job.

Request (multipart):
```bash
curl -X POST http://localhost:5000/documents \
  -F "file=@notes.txt"
```

Response:
```json
{
  "id": "6dc3d9d2-6ca3-43d1-a66a-52f6276a7ae9",
  "filename": "notes.txt",
  "status": "queued",
  "document_id": null,
  "error_message": null,
  "created_at": "2026-04-21T12:00:00+00:00",
  "updated_at": "2026-04-21T12:00:00+00:00"
}
```

### `GET /jobs/<job_id>`
Check ingestion progress and final status.

### `GET /search?q=...`
Run hybrid semantic + lexical search with reranking.

Request:
```bash
curl "http://localhost:5000/search?q=backend+flask+api"
```

Response:
```json
{
  "query": "backend flask api",
  "count": 1,
  "results": [
    {
      "document_id": 1,
      "filename": "notes.txt",
      "chunk_index": 0,
      "score": 0.8123,
      "semantic_score": 0.7921,
      "lexical_score": 0.8750,
      "snippet": "Flask API design with semantic indexing..."
    }
  ],
  "mode": "hybrid"
}
```

### `GET /documents/<id>`
Fetch indexed document metadata and extracted content.

### `GET /health`
Simple health check endpoint.

### `GET /openapi.json` and `GET /docs`
Machine-readable API contract and interactive Swagger UI.

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python app.py
   ```

Optional environment variables:
- `MODEL_NAME` (default: `all-MiniLM-L6-v2`)
- `DATABASE_PATH` (default: `data/search_engine.db`)
- `UPLOADS_DIR` (default: `uploads`)
- `MAX_CONTENT_LENGTH` (default: `16777216`)
- `MAX_SEARCH_RESULTS` (default: `10`)
- `MIN_SIMILARITY_SCORE` (default: `0.1`)
- `HYBRID_SEMANTIC_WEIGHT` (default: `0.75`)
- `HYBRID_LEXICAL_WEIGHT` (default: `0.25`)
- `RERANK_TOP_K` (default: `30`)
- `INGESTION_WORKERS` (default: `2`)
- `FLASK_DEBUG` (default: `false`)
- `PORT` (default: `5000`)

## Tests

Run:
```bash
pytest -q
```

The test suite covers ingestion persistence, file extraction, semantic ranking behavior, and API endpoint contracts.

Evaluation metrics:
```bash
python scripts/evaluate.py --eval-file eval/sample_queries.json
```

## Example Use Case

Index internal engineering notes and design docs, then query with natural language (for example, "how we handle cache invalidation") to retrieve semantically relevant passages while still benefiting from lexical signal for exact terminology.

## Why This Project Matters

This repository demonstrates practical backend engineering patterns: API-first design, clear service boundaries, local persistence, text processing pipelines, and reliable tests. It is intentionally scoped to remain understandable while still reflecting production-minded implementation decisions.

## Future Improvements

- Add document deletion and re-indexing endpoints
- Add pagination and cursor-based navigation for large result sets
- Add model/provider abstraction for optional external embedding backends
- Expand offline evaluation set with domain-specific relevance labels
