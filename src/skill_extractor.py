import re
import json
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate

# ------------------ LLM ------------------
llm = Ollama(
    model="mistral:latest",
    base_url="http://localhost:11434"
)

prompt = PromptTemplate(
    input_variables=["resume"],
    template="""
You are an ATS resume parser.

Extract ONLY technical skills (programming languages, frameworks, tools, databases, CS subjects).
Do NOT include names, locations, education, sentences, or soft skills.

Return ONLY valid JSON:
{
  "Job Role": "",
  "Skills": [],
  "Experience Level": ""
}

Resume:
{resume}
"""
)

# ------------------ TECH SKILL VOCAB (OPEN SET) ------------------
TECH_KEYWORDS = [
    # Languages
    "C", "C++", "Java", "Python", "JavaScript",

    # Web
    "HTML", "CSS", "React", "Node.js", "Flask",

    # Databases
    "MySQL", "MongoDB", "PostgreSQL", "Oracle",

    # Core CS
    "OOPS", "DBMS", "CN", "OS",

    # Tools / Tech
    "OpenCV", "Git", "Docker"
]

def extract_skills(resume_text: str) -> dict:
    skills = set()

    # ---------- 1️⃣ SECTION-BASED EXTRACTION ----------
    sections = re.split(
        r"(SKILLS|PROJECTS|TECHNOLOGIES|EXPERIENCE)",
        resume_text,
        flags=re.IGNORECASE
    )

    relevant_text = ""
    for i in range(len(sections)):
        if re.match(r"SKILLS|PROJECTS|TECHNOLOGIES", sections[i], re.IGNORECASE):
            relevant_text += sections[i+1] if i+1 < len(sections) else ""

    # ---------- 2️⃣ KEYWORD VALIDATION ----------
    for skill in TECH_KEYWORDS:
        if re.search(rf"\b{re.escape(skill)}\b", relevant_text, re.IGNORECASE):
            skills.add(skill)

    # ---------- 3️⃣ LLM REFINEMENT ----------
    job_role = "Software Developer"
    experience = "Fresher"

    try:
        response = llm.invoke(prompt.format(resume=relevant_text))
        parsed = json.loads(response)

        job_role = parsed.get("Job Role", job_role)
        experience = parsed.get("Experience Level", experience)

        for s in parsed.get("Skills", []):
            s = s.strip()
            if s in TECH_KEYWORDS:
                skills.add(s)

    except Exception:
        pass

    return {
        "Job Role": job_role,
        "Skills": sorted(skills),
        "Experience Level": experience
    }
