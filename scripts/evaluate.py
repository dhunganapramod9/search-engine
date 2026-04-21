import argparse
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import _build_services
from config import Config


def precision_at_k(relevant_ids, predicted_ids, k: int) -> float:
    top_k = predicted_ids[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for doc_id in top_k if doc_id in relevant_ids)
    return hits / len(top_k)


def reciprocal_rank(relevant_ids, predicted_ids) -> float:
    for rank, doc_id in enumerate(predicted_ids, start=1):
        if doc_id in relevant_ids:
            return 1.0 / rank
    return 0.0


def run_evaluation(eval_file: Path):
    config = Config()
    _, _, search_service, _ = _build_services(config)
    payload = json.loads(eval_file.read_text(encoding="utf-8"))
    queries = payload["queries"]

    p_at_3_values = []
    rr_values = []
    for query_case in queries:
        results = search_service.hybrid_search(query_case["query"], limit=5, min_score=-1.0)
        predicted = [item["document_id"] for item in results]
        relevant = query_case["relevant_document_ids"]
        p_at_3_values.append(precision_at_k(relevant, predicted, 3))
        rr_values.append(reciprocal_rank(relevant, predicted))

    avg_p_at_3 = sum(p_at_3_values) / len(p_at_3_values) if p_at_3_values else 0.0
    mrr = sum(rr_values) / len(rr_values) if rr_values else 0.0
    print(json.dumps({"queries": len(queries), "precision_at_3": round(avg_p_at_3, 4), "mrr": round(mrr, 4)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate semantic search quality with labeled queries.")
    parser.add_argument("--eval-file", default="eval/sample_queries.json", help="Path to evaluation query file.")
    args = parser.parse_args()
    run_evaluation(Path(args.eval_file))
