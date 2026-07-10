from google import genai
from google.genai import types
from gemini_client import generate_with_rotation
import time
from google.genai.errors import APIError 
import os
import json 


def analyze_resume(resume_text, job_description):
    prompt = f"""
You are an expert ATS Resume Analyzer.

Your task is to compare the resume ONLY with the provided job description.

Do NOT use any assumptions.

Rules:
1. ATS score must depend on similarity between resume and job description.
2. Matching skills = only skills present in BOTH.
3. Missing skills = skills in JD but absent in resume.
4. Strengths must come ONLY from resume.
5. Weaknesses must come ONLY from missing skills.
6. Suggestions must directly improve missing skills.
7. Do NOT generate any ATS score.
8. Do NOT generate any final verdict.
9. Only provide strengths, weaknesses and suggestions.

Scoring:

90-100 = Excellent Match
75-89 = Good Match
50-74 = Average Match
Below 50 = Poor Match

Resume:
----------------
{resume_text}

Job Description:
----------------
{job_description}

Return JSON only.
"""

    try:
        response = generate_with_rotation(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.95,    
                response_mime_type="application/json",
                system_instruction=(
                    "Extract technical skills, ignore soft skills, ensure unique entries, proper capitalization, "
                    "keep strengths/weaknesses/suggestions concise, and return an integer ats_score between 0 and 100."
                ),
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "ats_score": {"type": "INTEGER"},
                        "resume_skills": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "job_skills": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "matched_skills": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "missing_skills": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "strengths": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "weaknesses": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "suggestions": {"type": "ARRAY", "items": {"type": "STRING"}},
                        
                    },
                    "required": [
                        "ats_score", "resume_skills", "job_skills", "matched_skills", 
                        "missing_skills", "strengths", "weaknesses", "suggestions"
                    ]
                }
            )
        )

        # If successful, parse and return data
        data = json.loads(response.text.strip())
        data.setdefault("status", "success")
        return data

    except Exception as e:
        error=str(e)
        # If it's a quota error and we have retries left, wait and try again
        if "RESOURCE_EXHAUSTED" in error or "429" in error:
            return {
                "status": "error",
                "message": "🚫 Gemini API quota exceeded. Please wait about 1 minute and try again."
            }
        
        # If all retries fail or it's a quota error on the final attempt
        elif "503" in error or "UNAVAILABLE" in error:
            return {
                "status": "error",
                "message": "⚠️ Gemini servers are busy. Please try again later."
            }

        # JSON Error
        elif "JSON" in error:
            return {
                "status": "error",
                "message": "⚠️ AI returned an invalid response. Please retry."
            }

        # Any other error
        return {
            "status": "error",
            "message": f"System Error: {error}"
        }
    