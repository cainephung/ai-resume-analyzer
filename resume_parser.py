import pdfplumber
import docx
import re
import string
import textstat
from collections import Counter

# Load stopwords from a simple list (you can adjust or externalize it)
STOPWORDS = {
    "and", "or", "but", "so", "because", "a", "an", "the", "to", "for", "with",
    "on", "in", "at", "of", "by", "from", "as", "is", "are", "was", "were", "be",
    "been", "being", "this", "that", "those", "these", "it", "its", "i", "you",
    "your", "we", "they", "them", "he", "she", "him", "her", "my", "our", "their"
}

def extract_resume_text(file_path):
    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        raise ValueError("Unsupported file type. Use PDF or DOCX.")

def clean_text(text):
    text = text.lower()
    text = re.sub(f"[{re.escape(string.punctuation)}]", " ", text)
    return text

def extract_keywords(text):
    text = clean_text(text)
    words = text.split()
    keywords = [word for word in words if word not in STOPWORDS and len(word) > 2]
    return list(set(keywords))

def calculate_match_score(resume_keywords, job_keywords):
    if not resume_keywords or not job_keywords:
        return 0.0
    match_count = len(set(resume_keywords) & set(job_keywords))
    return (match_count / len(set(job_keywords))) * 100

def get_readability_score(text):
    return textstat.flesch_reading_ease(text)

from collections import Counter

def get_suggestions(resume_keywords, job_text):
    job_text_clean = clean_text(job_text)
    job_words = job_text_clean.split()
    job_counter = Counter(job_words)

    # Filter job keywords (excluding common stopwords + short words)
    job_keywords = [
        word for word in job_counter
        if word not in STOPWORDS and len(word) > 2
    ]

    # Missing = words in job, not in resume
    missing = [
        (word, job_counter[word]) for word in job_keywords
        if word not in resume_keywords
    ]

    # Sort by frequency (importance)
    missing_sorted = sorted(missing, key=lambda x: -x[1])

    # Return top 10 keywords only
    return [word for word, _ in missing_sorted[:10]]

