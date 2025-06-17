# --- PATCH TORCH WATCHER ---
from streamlit.watcher import local_sources_watcher
def skip_torch_modules_watcher():
    original_func = local_sources_watcher.get_module_paths
    def safe_func(module):
        if module.__name__.startswith("torch"):
            return []
        return original_func(module)
    local_sources_watcher.get_module_paths = safe_func
skip_torch_modules_watcher()

# --- Imports ---
import streamlit as st
import os
import tempfile
import base64
import json
from pathlib import Path
from fpdf import FPDF
from ml_model import semantic_similarity
from resume_parser import (
    extract_resume_text,
    extract_keywords,
    calculate_match_score,
    get_suggestions,
)
import re
from html import escape
from collections import defaultdict

# --- Constants ---
HISTORY_PATH = os.path.join(tempfile.gettempdir(), "resume_analysis_history.json")

# --- Functions ---
def load_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f)

def highlight_matches(text, keywords):
    def replacer(match):
        return f'<span style="background-color: yellow; color: black">{escape(match.group(0))}</span>'
    for kw in sorted(keywords, key=len, reverse=True):
        pattern = re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
        text = pattern.sub(replacer, text)
    return text

# --- UI Setup ---
st.set_page_config(page_title="AI Resume Analyzer", layout="centered")
# --- Hide Streamlit's default deploy button and menu ---
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("AI Resume Analyzer")

st.markdown("""
Upload your resume (PDF or DOCX) and paste the job description below.
The tool will evaluate match quality using keyword and ML-based semantic scoring, and suggest improvements based on your input.
""")

# --- Load History ---
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = load_history()

# --- Inputs ---
st.header("Resume & Job Description")
resume_file = st.file_uploader("Resume file", type=["pdf", "docx"])
job_description = st.text_area("Job description")

# --- Analysis Button ---
if st.button("Analyze Resume"):
    if not resume_file or not job_description:
        st.warning("Both a resume and job description are required.")
    else:
        file_ext = Path(resume_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            tmp.write(resume_file.read())
            tmp_path = tmp.name

        try:
            resume_text = extract_resume_text(tmp_path)
        except Exception as e:
            st.error(f"Could not read resume: {e}")
            os.unlink(tmp_path)
            st.stop()
        os.unlink(tmp_path)

        job_text = job_description
        resume_keywords = extract_keywords(resume_text)
        job_keywords = extract_keywords(job_text)

        match_score = calculate_match_score(resume_keywords, job_keywords)
        semantic_score = semantic_similarity(resume_text, job_text)
        suggestions = get_suggestions(resume_keywords, job_text)

        st.header("Match Analysis")
        col1, col2 = st.columns(2)
        col1.metric("Keyword Match", f"{match_score:.2f}%")
        col2.metric("Semantic Match", f"{semantic_score:.2f}%")

        st.subheader("Suggestions")
        if suggestions:
            st.write("Consider including keywords like:")
            st.markdown(f"`{', '.join(suggestions)}`")
        else:
            st.success("Your resume already covers most key terms.")

        new_entry = {
            "filename": resume_file.name,
            "match_score": match_score,
            "semantic_score": semantic_score,
            "suggestions": suggestions,
            "resume_text": resume_text,
            "job_text": job_text
        }
        st.session_state.analysis_history.append(new_entry)
        save_history(st.session_state.analysis_history)

        # --- PDF Download ---
        class PDF(FPDF):
            def header(self):
                self.set_font("Arial", "B", 14)
                self.cell(0, 10, "Resume Match Report", ln=True, align="C")

            def body(self):
                self.set_font("Arial", "", 12)
                self.ln(10)
                self.cell(0, 10, f"Keyword Match Score: {match_score:.2f}%", ln=True)
                self.cell(0, 10, f"Semantic Match Score: {semantic_score:.2f}%", ln=True)
                self.ln(10)
                if suggestions:
                    self.multi_cell(0, 10, "Suggestions:\n" + ", ".join(suggestions))

            def footer(self):
                self.set_y(-15)
                self.set_font("Arial", "I", 8)
                self.cell(0, 10, "Generated by AI Resume Analyzer", align="C")

        pdf = PDF()
        pdf.add_page()
        pdf.body()
        pdf_path = os.path.join(tempfile.gettempdir(), "resume_report.pdf")
        pdf.output(pdf_path)

        with open(pdf_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="resume_report.pdf">Download PDF Report</a>'
            st.markdown(href, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("This analysis runs fully offline using local models.")

# --- History Viewer ---
grouped = defaultdict(list)
for entry in st.session_state.analysis_history:
    grouped[entry["filename"]].append(entry)

if grouped:
    st.markdown("---")
    # --- Clear History Button ---
    if st.button("🗑️ Clear All Analysis History"):
        st.session_state.analysis_history = []
        if os.path.exists(HISTORY_PATH):
            os.remove(HISTORY_PATH)
        st.success("History cleared!")
        st.rerun()

    st.header("Resume Analysis History")

    selected_group = st.selectbox("Select Resume Group", list(grouped.keys()))

    if selected_group:
        entries = grouped[selected_group]
        st.markdown(f"### {selected_group} ({len(entries)} records)")

        for idx, entry in enumerate(reversed(entries)):
            with st.expander(f"Record {len(entries) - idx}", expanded=False):
                st.write(f"**Keyword Match:** {entry['match_score']:.2f}%")
                st.write(f"**Semantic Match:** {entry['semantic_score']:.2f}%")
                if entry["suggestions"]:
                    st.markdown(f"`{', '.join(entry['suggestions'])}`")

                if st.toggle("Show Resume vs Job Description", key=f"text_toggle_{selected_group}_{idx}"):
                    layout_mode = st.radio(
                        "Compare layout",
                        ["Side-by-Side", "Stacked"],
                        horizontal=True,
                        key=f"layout_mode_{selected_group}_{idx}"  
                    )

                    job_keywords = extract_keywords(entry["job_text"])
                    resume_keywords = extract_keywords(entry["resume_text"])

                    # Only highlight shared words in the job description
                    common_keywords = set(job_keywords) & set(resume_keywords)

                    highlighted_resume = highlight_matches(entry["resume_text"], job_keywords)
                    highlighted_job = highlight_matches(entry["job_text"], common_keywords)


                    if layout_mode == "Side-by-Side":
                        resume_col, spacer, job_col = st.columns([1, 0.05, 1])
                        with resume_col:
                            st.subheader("Resume Text")
                            st.markdown(highlighted_resume, unsafe_allow_html=True)

                        with job_col:
                            st.markdown("<div style='border-left: 1px solid #ddd; height: 100%;'></div>", unsafe_allow_html=True)

                        with job_col:
                            st.subheader("Job Description")
                            st.markdown(highlighted_job, unsafe_allow_html=True)

                    else:
                        st.subheader("Resume Text")
                        st.markdown(highlighted_resume, unsafe_allow_html=True)
                        st.markdown("<hr style='border-top: 1px solid #bbb;'>", unsafe_allow_html=True)
                        st.subheader("Job Description")
                        st.markdown(highlighted_job, unsafe_allow_html=True)
