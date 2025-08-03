import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
import tempfile
import io
import re
import os
import requests
from bs4 import BeautifulSoup
from docx import Document
import spacy

# Set streamlit layout
st.set_page_config(page_title="LazyHuntAi", layout="centered")

# Load spaCy model
@st.cache_resource
def get_nlp_model():
    return spacy.load("en_core_web_sm")

nlp = get_nlp_model()

# Skill extraction keywords
tech_keywords = {
    'Python', 'PowerShell', 'Azure', 'AWS', 'GCP', 'Kubernetes', 'MLflow', 'Kubeflow', 'RAG',
    'LLM', 'Langchain', 'Mistral', 'Llama', 'GPT-4', 'TensorFlow', 'PyTorch', 'Django',
    'Ansible', 'StackStorm', 'ADO', 'GitHub', 'Bitbucket', 'Vector DB', 'Databricks'
}

# Resume builder logic
def build_resume(data, file_path):
    doc = SimpleDocTemplate(file_path, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Header', fontSize=18, leading=22, spaceAfter=10, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='SubHeader', fontSize=13, leading=16, spaceAfter=6))
    styles.add(ParagraphStyle(name='List', fontSize=10.5, leading=14, spaceAfter=6))

    flow = []
    flow.append(Paragraph(data['name'], styles['Header']))

    contact_info_style = ParagraphStyle(name='ContactInfo', parent=styles['Normal'], alignment=TA_CENTER)
    contact_info = f"{data['location']} | {data['phone']} | {data['email']}"
    flow.append(Paragraph(contact_info, contact_info_style))
    flow.append(Spacer(1, 12))

    flow.append(Paragraph("Professional Summary", styles['SubHeader']))
    flow.append(Paragraph(data['summary'], styles['List']))

    flow.append(Paragraph("Experience", styles['SubHeader']))
    for exp in data['experience']:
        flow.append(Paragraph(f"{exp['role']} at {exp['company']} ({exp['duration']})", styles['List']))
        for resp in exp['tasks'].split('\n'):
            flow.append(Paragraph(f"• {resp.strip()}", styles['List']))
        flow.append(Spacer(1, 6))

    flow.append(Paragraph("Education", styles['SubHeader']))
    for edu in data['education']:
        flow.append(Paragraph(f"{edu['degree']}, {edu['institution']} ({edu['duration']})", styles['List']))

    flow.append(Paragraph("Skills", styles['SubHeader']))
    flow.append(Paragraph(", ".join(data['skills']), styles['List']))

    doc.build(flow)

# Job description extractor
def extract_job_desc(url: str) -> str:
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.content, 'html.parser')
        for cls in ['description', 'jobDescription', 'job-desc', 'job-description', 'Job Description']:
            jd_div = soup.find(class_=cls)
            if jd_div:
                text = jd_div.get_text(" ", strip=True)
                if text:
                    return text
        return soup.body.get_text(" ", strip=True)[:5000]
    except Exception as e:
        st.error(f"Failed to extract job description: {e}")
        return ""

def extract_skills(text, nlp_model):
    doc = nlp_model(text)
    found = set()
    for token in doc:
        if token.text in tech_keywords:
            found.add(token.text)
    matches = re.findall(r'\b[A-Z][a-zA-Z\d\-\+\.#]{2,}\b', text)
    found.update([m for m in matches if m in tech_keywords])
    return sorted(found)

def read_docx(file) -> tuple[Document, list]:
    file_buffer = io.BytesIO(file.read())
    doc = Document(file_buffer)
    lines = [p.text for p in doc.paragraphs]
    return doc, lines

def update_skills_only(doc: Document, lines: list, new_skills: list):
    header = "skills"
    idx = None
    for i, line in enumerate(lines):
        if header in line.lower():
            idx = i
            break
    if idx is not None:
        nexti = idx + 1
        existing = set()
        if nexti < len(lines) and len(lines[nexti]) < 300:
            existing.update({s.strip().lower() for s in re.split(r',|/|;|\n', lines[nexti]) if len(s.strip()) > 2})
        merged = set(existing)
        merged.update({s.lower() for s in new_skills})
        updated_skills = ", ".join(sorted({s.title() for s in merged}))
        doc.paragraphs[nexti].text = updated_skills

# ------------------ Main Page -------------------
st.title("💫 LazyHuntAi: Your Resume Assistant")

option = st.radio("Choose a Feature:", ["Build Resume from Scratch", "Update Resume Skills from Job URL"])

if option == "Build Resume from Scratch":
    st.subheader("📄 Get Your Resume Ready in Minutes")

    name = st.text_input("Full Name")
    location = st.text_input("Location", key="main_location")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email Address")
    summary = st.text_area("Professional Summary")

    experience = []
    st.markdown("### Experience")
    exp_count = st.number_input("Number of Experiences", min_value=1, max_value=5, value=1, step=1)
    for i in range(int(exp_count)):
        with st.expander(f"Experience {i+1}"):
            exp_company = st.text_input(f"Company", key=f"company_{i}")
            exp_location = st.text_input(f"Location", key=f"location_{i}")
            exp_role = st.text_input(f"Role", key=f"role_{i}")
            exp_duration = st.text_input(f"Duration", key=f"duration_{i}")
            exp_tasks = st.text_area(f"Responsibilities (one per line)", key=f"tasks_{i}")
            experience.append({
                'company': exp_company,
                'location': exp_location,
                'role': exp_role,
                'duration': exp_duration,
                'tasks': exp_tasks
            })

    education = []
    st.markdown("### Education")
    edu_count = st.number_input("Number of Education Entries", min_value=1, max_value=5, value=1, step=1)
    for i in range(int(edu_count)):
        with st.expander(f"Education {i+1}"):
            degree = st.text_input("Degree", key=f"degree_{i}")
            institution = st.text_input("Institution", key=f"institution_{i}")
            duration = st.text_input("Duration", key=f"edu_duration_{i}")
            education.append({
                'degree': degree,
                'institution': institution,
                'duration': duration
            })

    skills = st.text_area("Enter skills separated by commas")

    if st.button("Generate Resume"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            resume_data = {
                'name': name,
                'location': location,
                'phone': phone,
                'email': email,
                'summary': summary,
                'experience': experience,
                'education': education,
                'skills': [s.strip() for s in skills.split(",") if s.strip()]
            }
            build_resume(resume_data, tmp_file.name)
            st.success("✅ Resume generated successfully!")
            with open(tmp_file.name, "rb") as f:
                st.download_button("⬇️ Download Resume PDF", f, file_name="resume.pdf")

elif option == "Update Resume Skills from Job URL":
    st.subheader("🎯 Smart Resume Skill Updater")
    job_url = st.text_input("Paste Job Post URL")
    uploaded_file = st.file_uploader("Upload Resume (.docx)", type=["docx"])

    if st.button("Update Skills from JD"):
        if not job_url or not uploaded_file:
            st.warning("Please provide both a Job Post URL and a resume.")
        else:
            with st.spinner("Extracting Job Description..."):
                jd_text = extract_job_desc(job_url)

            if not jd_text:
                st.error("❌ Could not extract job description from the provided URL.")
            else:
                doc, doc_lines = read_docx(uploaded_file)
                jd_skills = extract_skills(jd_text, nlp)

                if jd_skills:
                    update_skills_only(doc, doc_lines, jd_skills)

                output = io.BytesIO()
                doc.save(output)
                output.seek(0)

                st.success("✅ Skills updated successfully — everything else is untouched!")
                st.download_button(
                    label="⬇️ Download Updated Resume",
                    data=output,
                    file_name="resume_with_skills_updated.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
