from llm.query_rewrite import rewrite_query
from llm.rerank import rerank_candidates
from llm.summarize import generate_summary

def rewrite_query_llm(q):
    return rewrite_query(q)

def rerank_llm(query, candidates, top_k):
    return rerank_candidates(query, candidates, top_k)

def summarize_llm(query, ranked):
    return generate_summary(query, ranked)
