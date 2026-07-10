from google import genai
from gemini_client import generate_with_rotation
import json
import os 

def evaluate_complete_interview(questions, answers):

    interview = ""

    for i, (q, a) in enumerate(zip(questions, answers), start=1):
        interview += f"""
Question {i}:
{q}

Candidate Answer:
{a}

"""

    prompt = f"""
You are an expert AI Technical Interviewer.

Evaluate the complete interview.

Interview:

{interview}

Return ONLY valid JSON.

{{
    "overall_score": 85,
    "technical_score": 82,
    "communication_score": 88,
    "confidence_score": 84,

    "strengths": [
        "Strong Python knowledge",
        "Good ML concepts"
    ],

    "weaknesses": [
        "Need better communication",
        "Improve Deep Learning knowledge"
    ],

    "improvements": [
        "Practice system design",
        "Revise NLP",
        "Answer with more examples"
    ],

    "overall_feedback":"Overall performance was good."
}}

Do not return markdown.
Do not return explanation.
Return JSON only.
"""

    try:
        response = generate_with_rotation(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        text = response.text.strip()

        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

        return json.loads(text)

    except Exception:
        return {
            "overall_score": 0,
            "technical_score": 0,
            "communication_score": 0,
            "confidence_score": 0,
            "strengths": [],
            "weaknesses": [],
            "improvements": [],
            "overall_feedback": "Unable to evaluate interview right now. Please try again later."
        }