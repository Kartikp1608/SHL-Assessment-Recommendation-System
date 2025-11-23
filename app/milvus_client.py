import os
from pymilvus import connections, Collection

MILVUS_DB = os.getenv("MILVUS_DB", "data/milvus.db")
COLLECTION = "shl_assessments"

_conn = False

def connect():
    global _conn
    if _conn:
        return
    connections.connect("default", uri=MILVUS_DB)
    _conn = True


def milvus_search(query_vec, top_k=30):
    connect()
    col = Collection(COLLECTION)
    
    res = col.search(
        [query_vec.tolist()],
        "embedding",
        param={"metric_type": "COSINE"},
        limit=top_k,
        output_fields=["id", "name", "url"]
    )

    hits = []
    for hit in res[0]:
        hits.append({
            "id": hit.entity.get("id"),
            "name": hit.entity.get("name"),
            "url": hit.entity.get("url"),
            "distance": hit.distance
        })

    return hits
