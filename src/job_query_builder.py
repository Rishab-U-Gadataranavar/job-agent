def build_job_query(parsed_resume):
    role = parsed_resume.get("Job Role", "Software Developer")
    skills = set(parsed_resume.get("Skills", []))

    queries = []

    frontend = {"HTML", "CSS", "JavaScript", "React"}
    backend = {"Java", "Python", "Node.js", "Flask"}
    database = {"MySQL", "MongoDB"}

    if skills & frontend:
        queries.append("Frontend Developer")

    if skills & backend:
        queries.append("Backend Developer")

    if skills & frontend and skills & backend:
        queries.append("Full Stack Developer")

    if "Java" in skills:
        queries.append("Java Developer Fresher")

    if "Python" in skills:
        queries.append("Python Developer Fresher")

    if database & skills:
        queries.append("Software Developer Database")

    if not queries:
        queries.append("Software Developer Fresher")

    return list(set(queries))
