import os
import sys
import json
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from llm.query_rewrite import rewrite_query
from llm.rerank import rerank_candidates
from llm.summarize import generate_summary

from pymilvus import connections, Collection#type: ignore

MILVUS_URI = "/home/kartikpal/Desktop/SHL/data/milvus.db"
COLLECTION_NAME = "shl_assessments"
EMBED_FILE = "embeddings/embeddings.npy"
META_FILE = "embeddings/metadata.json"

embeddings = np.load(EMBED_FILE)
with open(META_FILE, "r") as f:
    metadata = json.load(f)

def connect_milvus():
    connections.disconnect("default")
    connections.connect("default", uri=MILVUS_URI)
    print("Milvus Connected.")

def milvus_search(query_vec, top_k=20):
    col = Collection(COLLECTION_NAME)
    col.load()

    search_params = {
        "metric_type": "COSINE",
        "params": {}
    }

    res = col.search(
        data=[query_vec.tolist()],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        output_fields=["id", "name", "url"]
    )

    hits = []
    for h in res[0]:
        row = {
            "id": h.entity.get("id"),
            "name": h.entity.get("name"),
            "url": h.entity.get("url"),
            "score": float(h.distance)
        }
        hits.append(row)

    return hits

def recommend(query, top_k=5):
    print("\n======= ORIGINAL QUERY =======")
    print(query)

    rewritten = rewrite_query(query)

    print("\n======= REWRITTEN QUERY =======")
    print(rewritten)

    normalized = rewritten["normalized_query"]

    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    q_vec = embedder.encode([normalized])[0]

    connect_milvus()
    candidates = milvus_search(q_vec, top_k=30)

    print("\n===== RAW CANDIDATES (Top 5) =====")
    for c in candidates[:5]:
        print(c["name"], c["score"])

    reranked = rerank_candidates(normalized, candidates, top_k=top_k)

    summary = generate_summary(query, reranked)

    return {
        "query_original": query,
        "rewritten_query": rewritten,
        "recommended_assessments": reranked,
        "summary": summary
    }

if __name__ == "__main__":
    res = recommend("I want to hire a Senior Data Analyst with 5 years of experience and expertise in SQL, Excel and Python. The assessment can be 1-2 hour long", top_k=5)
    print("\n\nFINAL OUTPUT:")
    print(json.dumps(res, indent=2))
