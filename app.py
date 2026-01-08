from fastapi import FastAPI, UploadFile
import shutil
import os

from src.resume_parser import extract_resume_text
from src.skill_extractor import extract_skills
from src.job_query_builder import build_job_query
from src.job_fetcher import fetch_jobs
from src.job_matcher import calculate_match_score

app = FastAPI(title="AI Job Finder Agent")

UPLOAD_DIR = "temp"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_JOBS = 25


@app.get("/")
def home():
    return {"message": "AI Job Finder Agent is running"}


@app.post("/find-jobs/")
async def find_jobs(resume: UploadFile):
    # Save resume
    file_path = os.path.join(UPLOAD_DIR, resume.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)

    # Parse resume
    resume_text = extract_resume_text(file_path)
    parsed_resume = extract_skills(resume_text)
    resume_skills = parsed_resume.get("Skills", [])

    # Build multiple queries
    queries = build_job_query(parsed_resume)

    # Fetch jobs for all queries
    all_jobs = []
    for q in queries:
        all_jobs.extend(fetch_jobs(q, max_results=20))

    # Deduplicate jobs
    unique_jobs = {}
    for job in all_jobs:
        key = f"{job['title']}|{job['company']}"
        if key not in unique_jobs:
            unique_jobs[key] = job

    all_jobs = list(unique_jobs.values())

    # Score jobs
    recommended_jobs = []

    for job in all_jobs:
        if len(recommended_jobs) >= MAX_JOBS:
            break

        job_text = f"{job['title']} {job.get('description','')}"
        score = calculate_match_score(resume_skills, job_text)

        recommended_jobs.append({
            "title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "salary": job.get("salary", "Not disclosed"),
            "match_score": max(score, 10),
            "link": job["link"]
        })

    # Sort by relevance
    recommended_jobs.sort(key=lambda x: x["match_score"], reverse=True)

    return {
        "parsed_resume": parsed_resume,
        "job_queries_used": queries,
        "recommended_jobs": recommended_jobs[:MAX_JOBS]
    }
