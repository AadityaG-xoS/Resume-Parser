# Resume Parser Project in Jupyter Notebook

# Install required libraries
!pip install PyMuPDF pdfminer.six python-docx spacy transformers nltk ipywidgets

# Install spaCy English model
!python -m spacy download en_core_web_sm

# Import necessary modules
import fitz  # PyMuPDF
from pdfminer.high_level import extract_text
from docx import Document
import spacy
import re
import json
import os
import nltk
from ipywidgets import FileUpload, Output
from IPython.display import display

# Download the necessary NLTK data
nltk.download('punkt')

# Define input processing functions
def process_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def process_docx(file_path):
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def process_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def process_file(file_path):
    if file_path.endswith('.pdf'):
        return process_pdf(file_path)
    elif file_path.endswith('.docx'):
        return process_docx(file_path)
    elif file_path.endswith('.txt'):
        return process_txt(file_path)
    else:
        raise ValueError("Unsupported file format")

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Define data extraction functions
def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_contact_info(text):
    phone_pattern = re.compile(r'\b\d{10}\b')
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    phone = phone_pattern.search(text)
    email = email_pattern.search(text)
    return phone.group() if phone else None, email.group() if email else None

def extract_education(text):
    education_keywords = ['school', 'college', 'university', 'institute', 'academy', 'degree', 'bachelor', 'master', 'phd']
    sentences = nltk.sent_tokenize(text)
    education = []
    for sent in sentences:
        if any(keyword in sent.lower() for keyword in education_keywords):
            education.append(sent.strip())
    return education

def extract_experience(text):
    experience_keywords = ['experience', 'worked', 'employed', 'job', 'position', 'role', 'responsibility']
    sentences = nltk.sent_tokenize(text)
    experience = []
    for sent in sentences:
        if any(keyword in sent.lower() for keyword in experience_keywords):
            experience.append(sent.strip())
    return experience

def extract_skills(text):
    # This function should be customized to your needs
    skills = ["Python", "NLP", "Machine Learning", "Data Analysis", "Project Management", "Leadership"]
    extracted_skills = [skill for skill in skills if skill in text]
    return extracted_skills

def extract_data(text):
    name = extract_name(text)
    phone, email = extract_contact_info(text)
    education = extract_education(text)
    experience = extract_experience(text)
    skills = extract_skills(text)

    return {
        "name": name,
        "phone": phone,
        "email": email,
        "education": education,
        "experience": experience,
        "skills": skills
    }

# Define output generation function
def generate_output(data, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Upload and process the file
def upload_and_process(change):
    for file_name, file_info in uploader.value.items():
        with open(file_name, 'wb') as f:
            f.write(file_info['content'])
        text = process_file(file_name)
        data = extract_data(text)
        output_path = f"{os.path.splitext(file_name)[0]}.json"
        generate_output(data, output_path)
        
        with open(output_path, 'r') as file:
            parsed_data = json.load(file)
        
        out.clear_output()
        with out:
            print(f"Parsed data for {file_name}:")
            print(json.dumps(parsed_data, indent=4))
            print("\n" + "="*50 + "\n")

# Create an uploader widget
uploader = FileUpload(accept='.pdf,.docx,.txt', multiple=False)
uploader.observe(upload_and_process, names='value')

out = Output()

display(uploader, out)
