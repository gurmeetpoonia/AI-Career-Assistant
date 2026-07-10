from google import genai
from gemini_client import generate_with_rotation
import os 
import time
def generate_interview_questions(
    resume_text,
    job_description,
    target_role,
    difficulty,
    interview_type,
    num_questions
):

    prompt = f"""
You are an expert technical interviewer.

Generate {num_questions} interview questions.

Candidate Resume:
{resume_text}

Job Description:
{job_description}

Target Role:
{target_role}

Difficulty:
{difficulty}

Interview Type:
{interview_type}

Instructions:
- Generate exactly {num_questions} questions.
- Do not include numbering.
- Return only the questions.
- Each question should be on a new line.
"""

   

    for attempt in range(3):
        try:
            response = generate_with_rotation(
            model="gemini-2.5-flash",
            contents=prompt
        )
            break

        except Exception:
            if attempt == 2:
                raise
            time.sleep(3)

    questions = [
        q.strip("- ").strip()
        for q in response.text.split("\n")
        if q.strip()
    ]

    return questions