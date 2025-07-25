from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import fuzz

def compute_match_score(resume_text, job_description):
    corpus = [resume_text, job_description]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return round(float(similarity[0][0]) * 100, 2)

def compute_skill_score(resume_skills, job_description):
    job_description = job_description.lower()
    matched_skills = []
    missing_skills = []

    for skill in resume_skills:
        matches = [fuzz.partial_ratio(skill.lower(), jd_word.strip()) for jd_word in job_description.split()]
        max_score = max(matches) if matches else 0
        if max_score > 80:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    total = len(resume_skills)
    skill_score = round((len(matched_skills) / total) * 100, 2) if total > 0 else 0.0

    return skill_score, matched_skills, missing_skills

def compute_overall_match_score(resume_text, resume_skills, job_description, weight_text=0.6, weight_skills=0.4):
    text_score = compute_match_score(resume_text, job_description)
    skill_score, matched_skills, missing_skills = compute_skill_score(resume_skills, job_description)
    overall_score = round((text_score * weight_text) + (skill_score * weight_skills), 2)

    return {
        "text_score": text_score,
        "skill_score": skill_score,
        "overall_score": overall_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }