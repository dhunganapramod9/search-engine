def get_openapi_spec():
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Semantic Document Search API",
            "version": "1.0.0",
            "description": "Backend-first API for async document ingestion and hybrid semantic search.",
        },
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health check",
                    "responses": {"200": {"description": "Service healthy"}},
                }
            },
            "/documents": {
                "post": {
                    "summary": "Create ingestion job",
                    "requestBody": {
                        "required": True,
                        "content": {"multipart/form-data": {"schema": {"type": "object"}}},
                    },
                    "responses": {"202": {"description": "Job accepted"}},
                }
            },
            "/jobs/{job_id}": {
                "get": {
                    "summary": "Get ingestion job status",
                    "parameters": [{"name": "job_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "responses": {"200": {"description": "Job status"}},
                }
            },
            "/documents/{document_id}": {
                "get": {
                    "summary": "Get indexed document content",
                    "parameters": [
                        {"name": "document_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "responses": {"200": {"description": "Document found"}, "404": {"description": "Not found"}},
                }
            },
            "/search": {
                "get": {
                    "summary": "Hybrid semantic + lexical search",
                    "parameters": [
                        {"name": "q", "in": "query", "required": True, "schema": {"type": "string"}},
                        {"name": "top_k", "in": "query", "required": False, "schema": {"type": "integer"}},
                        {"name": "min_score", "in": "query", "required": False, "schema": {"type": "number"}},
                    ],
                    "responses": {"200": {"description": "Ranked search results"}},
                }
            },
        },
    }
