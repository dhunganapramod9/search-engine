import io
import time


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
    assert response.headers.get("X-Request-ID")


def test_document_upload_and_search_flow(client):
    upload_response = client.post(
        "/documents",
        data={"file": (io.BytesIO(b"python backend semantic search api"), "resume_notes.txt")},
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 202
    job = upload_response.get_json()
    assert job["id"]

    document_id = None
    for _ in range(25):
        job_response = client.get(f"/jobs/{job['id']}")
        assert job_response.status_code == 200
        job_payload = job_response.get_json()
        if job_payload["status"] == "completed":
            document_id = job_payload["document_id"]
            break
        time.sleep(0.02)
    assert document_id is not None

    search_response = client.get("/search?q=python backend")
    assert search_response.status_code == 200
    body = search_response.get_json()
    assert body["count"] >= 1
    assert body["mode"] == "hybrid"
    assert body["results"][0]["filename"] == "resume_notes.txt"
    assert "semantic_score" in body["results"][0]
    assert "lexical_score" in body["results"][0]

    document_response = client.get(f"/documents/{document_id}")
    assert document_response.status_code == 200


def test_search_requires_query(client):
    response = client.get("/search")
    assert response.status_code == 400


def test_openapi_contract_available(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.get_json()
    assert spec["openapi"].startswith("3.")
    assert "/documents" in spec["paths"]
    assert "/search" in spec["paths"]
