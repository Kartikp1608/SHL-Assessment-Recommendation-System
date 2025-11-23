# llm/rerank.py
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

PROMPT = """
You are an SHL assessment recommendation engine.

Your goal:
Given a job description query and a list of SHL assessments, rerank the assessments by relevance.

Return ONLY a JSON array in this format:

[
  {{
    "id": "unique id of assessment",
    "score": 4.6,
    "url": "https://...",
    "name": "Assessment Name",
    "adaptive_support": "Yes",
    "description": "Full description",
    "duration": 25,
    "remote_support": "Yes",
    "test_type": ["P", "K"]
  }}
]

Rules:
- Return ONLY valid JSON (no explanation)
- adaptive_support and remote_support: must be “Yes” or “No”
- test_type must be a list of strings
- Duration must be an integer
- Score must be between 0 and 5

Query:
{query}

Candidates:
{candidates}
"""

def rerank_candidates(query: str, candidates: list, top_k: int = 10):
    # Convert candidate metadata for LLM
    cand_json = json.dumps([
        {
            "id": c.get("id") or c.get("assessment_id"),
            "name": c.get("name", ""),
            "description": c.get("description", ""),
            "url": c.get("url", ""),
            "adaptive_support": c.get("adaptive_support", "No"),
            "remote_support": c.get("remote_support", "Yes"),
            "duration": c.get("duration", 0),
            "test_type": c.get("test_type", [])
        }
        for c in candidates
    ], indent=2)

    # Ask Gemini to score + return full structured JSON
    response = model.generate_content(PROMPT.format(query=query, candidates=cand_json))
    text = response.text

    # Extract JSON
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        return []

    try:
        scored = json.loads(text[start:end+1])
    except:
        return []

    # Final safety cleanup: ensure all fields exist
    cleaned = []
    for item in scored:
        cleaned.append({
            "url": item.get("url", ""),
            "name": item.get("name", ""),
            "adaptive_support": item.get("adaptive_support", "No"),
            "description": item.get("description", ""),
            "duration": int(item.get("duration", 0)),
            "remote_support": item.get("remote_support", "Yes"),
            "test_type": item.get("test_type", []),
        })

    # Sort by score (if provided)
    cleaned.sort(key=lambda x: float(item.get("score", 0)), reverse=True)

    return cleaned[:top_k]
