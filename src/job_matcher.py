import re

def calculate_match_score(resume_skills, job_text):
    if not resume_skills or not job_text:
        return 0

    matched = 0
    job_text = job_text.lower()

    for skill in resume_skills:
        if re.search(rf"\b{re.escape(skill.lower())}\b", job_text):
            matched += 1

    return round((matched / len(resume_skills)) * 100)
