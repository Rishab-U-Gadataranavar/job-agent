import streamlit as st
import requests
from fpdf import FPDF

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="AI Job Finder Agent",
    page_icon="💼",
    layout="wide"
)

# ================== SIDEBAR ==================
st.sidebar.title("⚙️ Settings")
st.sidebar.header("🔎 Filters")

selected_location = st.sidebar.text_input("📍 Location (optional)").strip()
role_keyword = st.sidebar.text_input("💼 Role contains (optional)").strip()
tech_keyword = st.sidebar.text_input("🛠 Tech keyword (optional)").strip()

# ================== HEADER ==================
st.markdown(
    """
    <h1 style="text-align:center;">🤖 AI Job Finder Agent</h1>
    <p style="text-align:center; font-size:18px;">
    Upload your resume and get <b>AI-powered job recommendations</b>
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# ================== UPLOAD ==================
st.subheader("📄 Upload Your Resume")
uploaded_file = st.file_uploader("Upload resume (PDF only)", type=["pdf"])

# ================== PDF GENERATOR (UNICODE SAFE) ==================
def generate_pdf(jobs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, "AI Job Finder - Recommended Jobs", ln=True)
    pdf.ln(5)

    for job in jobs:
        text = (
            f"{job.get('title','')}\n"
            f"{job.get('company','')} - {job.get('location','')}\n"
            f"Salary: {job.get('salary','Not disclosed')}\n"
            f"Match Score: {job.get('match_score',0)}%\n"
            f"{job.get('link','')}\n"
        )

        # 🔒 HARD UNICODE SAFETY
        safe_text = text.encode("latin-1", "ignore").decode("latin-1")

        pdf.multi_cell(0, 8, safe_text)
        pdf.ln(2)

    return pdf

# ================== MAIN ==================
if uploaded_file:
    if st.button("🔍 Analyze Resume & Find Jobs"):
        with st.spinner("Analyzing resume and fetching jobs..."):
            files = {
                "resume": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf"
                )
            }
            response = requests.post(
                "http://127.0.0.1:8000/find-jobs/",
                files=files
            )

        if response.status_code != 200:
            st.error("Backend error. Please ensure FastAPI is running.")
        else:
            data = response.json()

            # ================== RESUME SUMMARY ==================
            st.subheader("🧠 Resume Summary")
            c1, c2, c3 = st.columns(3)
            c1.metric("Job Role", data["parsed_resume"]["Job Role"])
            c2.metric("Experience", data["parsed_resume"]["Experience Level"])
            c3.metric("Skills Found", len(data["parsed_resume"]["Skills"]))

            st.markdown("### 🛠 Skills Identified")
            st.write(", ".join(data["parsed_resume"]["Skills"]))

            # ================== FILTER JOBS ==================
            jobs = data.get("recommended_jobs", [])
            filtered_jobs = []

            for job in jobs:
                if selected_location and selected_location.lower() not in job["location"].lower():
                    continue
                if role_keyword and role_keyword.lower() not in job["title"].lower():
                    continue
                if tech_keyword and tech_keyword.lower() not in job["title"].lower():
                    continue
                filtered_jobs.append(job)

            if not filtered_jobs:
                filtered_jobs = jobs

            # ================== JOB RESULTS ==================
            st.subheader(f"💼 Recommended Jobs ({len(filtered_jobs)})")

            for job in filtered_jobs:
                with st.container():
                    st.markdown("---")
                    col1, col2 = st.columns([4, 1])

                    with col1:
                        st.markdown(f"### 💼 {job['title']}")
                        st.markdown(f"🏢 **Company:** {job['company']}")
                        st.markdown(f"📍 **Location:** {job['location']}")
                        st.markdown(f"💰 **Salary:** {job.get('salary','Not disclosed')}")
                        st.progress(job.get("match_score", 0) / 100)
                        st.caption(f"🎯 Match Score: {job.get('match_score', 0)}%")

                    with col2:
                        if job.get("link"):
                            st.markdown(
                                f"""
                                <a href="{job['link']}" target="_blank">
                                    <button style="
                                        width:100%;
                                        padding:10px;
                                        background-color:#4CAF50;
                                        color:white;
                                        border:none;
                                        border-radius:6px;
                                        font-size:16px;
                                        cursor:pointer;
                                    ">
                                        🚀 Apply Now
                                    </button>
                                </a>
                                """,
                                unsafe_allow_html=True
                            )

            # ================== PDF DOWNLOAD ==================
            if filtered_jobs:
                pdf = generate_pdf(filtered_jobs)
                st.download_button(
                    "📥 Download Jobs as PDF",
                    data=pdf.output(dest="S").encode("latin-1", "ignore"),
                    file_name="job_recommendations.pdf",
                    mime="application/pdf"
                )

            # ================== FOOTER ==================
            st.markdown(
                "<hr><p style='text-align:center;'>Built with ❤️ using FastAPI, Ollama & Streamlit</p>",
                unsafe_allow_html=True
            )
