import re
import spacy
from fuzzywuzzy import fuzz
from collections import Counter

# Load NLP model
_nlp = spacy.load("en_core_web_sm")

DEFAULT_SKILLS = {
    "python", "java", "c++", "sql", "excel", "machine learning", "deep learning",
    "ml", "django", "flask", "react", "node", "pandas", "numpy", "aws",
    "html", "css", "javascript", "git", "linux", "tensorflow", "keras", "scikit-learn",
    "data analysis", "data science", "communication", "leadership"
}

EDUCATION_KEYWORDS = [
    "bachelor", "master", "b.tech", "m.tech", "b.sc", "m.sc", "phd",
    "bachelor's", "master's", "degree", "graduated"
]

def extract_email(text: str):
    m = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return m.group(0) if m else None

def extract_phone(text: str):
    m = re.search(r'(\+?\d[\d \-\(\)]{8,}\d)', text)
    return m.group(1) if m else None

def extract_name(text: str):
    doc = _nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_education(text: str):
    lines = text.splitlines()
    education = []
    for line in lines:
        line_lower = line.lower()
        for keyword in EDUCATION_KEYWORDS:
            if keyword in line_lower:
                education.append(line.strip())
                break
    return education[:2]

def extract_skills(text: str, skills: set[str] = None, threshold: int = 85):
    if skills is None:
        skills = DEFAULT_SKILLS
    text_lower = text.lower()
    found = set()

    # Token-based match using spaCy
    doc = _nlp(text_lower)
    tokens = {token.text for token in doc if not token.is_stop and not token.is_punct}
    
    for skill in skills:
        if skill.lower() in text_lower:
            found.add(skill)
        elif fuzz.partial_ratio(skill.lower(), text_lower) >= threshold:
            found.add(skill)
        elif any(fuzz.ratio(skill.lower(), token) >= threshold for token in tokens):
            found.add(skill)

    return sorted(found)

def parse_info(text: str) -> dict:
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text)
    }
