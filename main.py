from flask import Flask, request, jsonify
from flask_cors import CORS
from parser.extract_text import extract_text_from_file
from parser.parse_info import parse_info
from ml.job_matching import compute_overall_match_score
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Upload folder: inside backend/uploads/
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def home():
    return "Resume Analyzer API is running!"

@app.route("/analyze", methods=["POST"])
def analyze_resume():
    if "resume" not in request.files or "job_description" not in request.form:
        return jsonify({"error": "Resume file and job description are required"}), 400

    file = request.files["resume"]
    job_description = request.form["job_description"]

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    try:
        resume_text = extract_text_from_file(save_path)
        extracted_info = parse_info(resume_text)
        resume_skills = extracted_info.get("skills", [])

        match_result = compute_overall_match_score(resume_text, resume_skills, job_description)

        return jsonify({
            "extracted_info": {
                "name": extracted_info.get("name"),
                "email": extracted_info.get("email"),
                "phone": extracted_info.get("phone"),
                "skills": resume_skills,
                "education": extracted_info.get("education")
            },
            "match_score": match_result["overall_score"],
            "text_score": match_result["text_score"],
            "skill_score": match_result["skill_score"],
            "matched_skills": match_result["matched_skills"],
            "missing_skills": match_result["missing_skills"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
