import os
import time
import fitz  # PyMuPDF
import google.generativeai as genai
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from fpdf import FPDF
from supabase_utils import supabase, download_analysis_pdf  # your existing Supabase client

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file")

genai.configure(api_key=api_key)

# Flask app
app = Flask(__name__)
CORS(app)  # Allow requests from React frontend

# Gemini model configuration
configuration = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain"
}
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=configuration
)

# Function to extract text from PDF resume
def extract_text_from_resume(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Function to analyze resume using Gemini
def analyse_resume_gemini(resume_content, job_description):
    prompt = f"""
    You are a professional resume analyzer.

    Resume:
    {resume_content}

    Job Description:
    {job_description}

    Task:
    - Analyze the resume against the job description
    - Give a match score out of 100
    - Highlight missing skills or experiences
    - Suggest improvements

    Return in structured format:
    Match Score: XX/100
    Missing Skills:
    - ...
    Suggestions:
    - ...
    Summary:
    ...
    """
    response = model.generate_content(prompt)
    return response.text

# Function to generate PDF of analysis
def generate_analysis_pdf(user_id, filename, analysis_text):
    pdf_name = f"{user_id}_analysis_{int(time.time())}.pdf"  # unique name with timestamp
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", "B", 16)
    pdf.multi_cell(0, 10, f"Analysis of {filename}\n\n")
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 8, analysis_text)
    pdf.output(pdf_name)
    return pdf_name

# API endpoint for React frontend
@app.route("/analyze", methods=["POST"])
def analyze_resume():
    try:
        if "resume" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["resume"]
        file_path = "uploaded_resume.pdf"
        file.save(file_path)

        job_description = request.form.get("job_description", "")
        user_id = request.form.get("user_id", "guest")  # for Supabase storage

        # Extract text and analyze
        resume_content = extract_text_from_resume(file_path)
        analysis_text = analyse_resume_gemini(resume_content, job_description)

        # Generate PDF
        pdf_name = generate_analysis_pdf(user_id, file.filename, analysis_text)

        # Upload PDF to Supabase
        with open(pdf_name, "rb") as pdf_file:
            storage = supabase.storage.from_("resumes")
            # Optional: delete existing file first
            try:
                storage.remove([f"{user_id}/{pdf_name}"])
            except:
                pass
            storage.upload(f"{user_id}/{pdf_name}", pdf_file)

        pdf_url = f"http://localhost:5000/download-analysis/{user_id}/{pdf_name}"  # link for React

        return jsonify({"analysis": analysis_text, "pdf_url": pdf_url})

    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(traceback_str)
        return jsonify({"error": str(e), "traceback": traceback_str}), 500

# Endpoint to download analysis PDF
@app.route("/download-analysis/<user_id>/<filename>", methods=["GET"])
def download_analysis(user_id, filename):
    save_path = f"temp_{filename}"
    download_analysis_pdf(user_id, filename, save_as=save_path)
    return send_file(save_path, as_attachment=True)

# Optional: Local testing without React
if __name__ == "__main__":
    app.run(debug=True, port=5000)
