import os
from dotenv import load_dotenv
from serpapi.google_search import GoogleSearch

load_dotenv()

def fetch_jobs(query: str, max_results=40):
    params = {
        "engine": "google_jobs",
        "q": query,
        "location": "India",
        "api_key": os.getenv("SERPAPI_API_KEY")
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    jobs = []

    for job in results.get("jobs_results", []):
        title = job.get("title", "")
        company = job.get("company_name", "")
        location = job.get("location", "India")
        salary = job.get("salary", "Not disclosed")
        description = job.get("description", "")

        apply_link = None

        # ✅ BEST: Direct apply options
        if job.get("apply_options"):
            apply_link = job["apply_options"][0].get("link")

        # ✅ SECOND: Related links (LinkedIn / Indeed / Company)
        if not apply_link and job.get("related_links"):
            apply_link = job["related_links"][0].get("link")

        # ❌ DO NOT USE GOOGLE SEARCH FALLBACK
        # If no apply link exists, we skip the job
        if not apply_link:
            continue

        jobs.append({
            "title": title,
            "company": company,
            "location": location,
            "salary": salary,
            "description": description,
            "link": apply_link
        })

        if len(jobs) >= max_results:
            break

    return jobs
