import os
import json
import google.generativeai as genai #type:ignore
from dotenv import load_dotenv #type:ignore

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

PROMPT = """You are an assistant that prepares job-role queries for semantic retrieval against an assessment catalog.

Task:
  1) Rewrite the user's free-form job description/query into a concise, search-optimized "normalized_query".
  2) Extract a short list (3-8) of **skills/competencies** (single words or short phrases).
  3) Produce an "expanded_keywords" string (comma-separated) to improve recall.

Return JSON ONLY with keys:
- normalized_query (string)
- skills (array of strings)
- expanded_keywords (string)

Example input:
"Senior Java engineer to lead microservices and APIs"

Example output:
{{
  "normalized_query": "senior java backend engineer - microservices & APIs",
  "skills": ["java", "microservices", "rest api", "spring boot", "system design"],
  "expanded_keywords": "java, backend, spring boot, microservices, rest api, api development, distributed systems"
}}

Now respond for the following query:
{query}
"""

def rewrite_query(query: str):
    response = model.generate_content(PROMPT.format(query=query))
    text = response.text

    # Extract JSON robustly
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return {"normalized_query": query, "skills": [], "expanded_keywords": query}

    try:
        return json.loads(text[start:end+1])
    except:
        return {"normalized_query": query, "skills": [], "expanded_keywords": query}


if __name__ == "__main__":
    print(rewrite_query("We need a senior python developer for ML pipelines"))
   