import os
import json
import google.generativeai as genai  # type: ignore
from dotenv import load_dotenv # type: ignore

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

PROMPT = """
You are an SHL assessment recommendation explainer.

Given:
1) the original user query
2) the final ranked assessments list (with name, description, and LLM score)

Produce:
- Provide a 4–5 sentence executive summary, then list assessments:
- A concise explanation of why each assessment was chosen
- Keep language professional, simple, and SHL-style

Return JSON ONLY:

{{
  "summary": "...",
  "assessments": [
    {{
      "name": "...",
      "score": 4.6,
      "why_selected": "..."
    }}
  ]
}}

Query:
{query}

Ranked Assessments:
{results}
"""

def generate_summary(query: str, ranked_results: list):
    try:
        # Prepare JSON for LLM
        results_json = json.dumps([
            {
                "name": r.get("name"),
                "score": r.get("score", 0),
                "description": r.get("description", "")
            }
            for r in ranked_results
        ], indent=2)

        response = model.generate_content(
            PROMPT.format(query=query, results=results_json)
        )
        text = response.text

        # extract JSON
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            return {"summary": "", "assessments": []}

        return json.loads(text[start:end + 1])

    except Exception as e:
        print("SUMMARY LLM ERROR:", e)
        # fallback
        return {
            "summary": "These assessments match the user's query based on semantic similarity.",
            "assessments": [
                {
                    "name": r.get("name", ""),
                    "score": r.get("score", 0),
                    "why_selected": "Relevant to the user's query."
                }
                for r in ranked_results
            ]
        }


if __name__ == "__main__":
    example_ranked = [
        {"name": "Numerical Reasoning", "description": "Math skills", "score": 4.8},
        {"name": "Verbal Reasoning", "description": "Reading comprehension", "score": 3.1}
    ]

    print(generate_summary("Finance analyst strong with numbers", example_ranked))
