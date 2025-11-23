import time
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from app.milvus_client import milvus_search
from app.llm_pipeline import rewrite_query_llm, rerank_llm
from app.embeddings import embed_text


app = FastAPI(title="SHL Recommendation Engine API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendRequest(BaseModel):
    query: str

class AssessmentItem(BaseModel):
    url: str
    name: str
    adaptive_support: str      # "Yes" or "No"
    description: str
    duration: int
    remote_support: str        # "Yes" or "No"
    test_type: List[str]


class RecommendResponse(BaseModel):
    recommended_assessments: List[AssessmentItem]

@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(payload: RecommendRequest):
    print("0. start")
    rewritten = rewrite_query_llm(payload.query)
    print("1. rewrite done")

    q_vec = embed_text(rewritten["normalized_query"])
    print("2. embed done")

    milvus_results = milvus_search(q_vec, top_k=30)
    print("3. milvus done")

    final_items = rerank_llm(payload.query, milvus_results, top_k=10)
    print("4. rerank done")

    print("5. returning response")
    return RecommendResponse(
        recommended_assessments=final_items
    )