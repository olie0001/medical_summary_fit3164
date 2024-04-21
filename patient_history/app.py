import pandas as pd
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from transformers import AutoTokenizer, BertLMHeadModel
import re
from faker import Faker
import random
from datetime import datetime, timedelta

def summarise(note):
    model_name = "microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract"
    model = BertLMHeadModel.from_pretrained(model_name, is_decoder=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    inputs = tokenizer.encode("summarize: " + note, return_tensors="pt", max_length=512, truncation=True)
    summary_ids = model.generate(inputs, max_length=513, min_length=50, num_beams=4, early_stopping=True)

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def chief_complaint(note):
    complaint = re.search(r'chief complaint\s*:\s*(.*?)(major surgical|history of present illness|$)', note, re.IGNORECASE)
    if complaint:
        return complaint.group(1).strip()
    else:
        return None

def generate_random_dob(start_year=1930, end_year=2020):
    start_date = datetime(year=start_year, month=1, day=1)
    end_date = datetime(year=end_year, month=12, day=31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date

def clean_medical_note(note):
    # Define regular expressions to match different sections
    section_patterns = {
        "Name": r"Name:(.*?)Admission Date:",
        "Admission Date": r"Admission Date:(.*?)Discharge Date:",
        "Discharge Date": r"Discharge Date:(.*?)Date of Birth:",
        "Date of Birth": r"Date of Birth:(.*?)Sex:",
        "Sex": r"Sex:(.*?)Service:",
        "Service": r"Service:(.*?)Allergies:",
        "Allergies": r"Allergies:(.*?)Attending:",
        "Attending": r"Attending:(.*?)Chief Complaint:",
        "Chief Complaint": r"Chief Complaint:(.*?)Major Surgical or Invasive Procedure:",
        "Major Surgical or Invasive Procedure": r"Major Surgical or Invasive Procedure:(.*?)History of Present Illness:",
        "History of Present Illness": r"History of Present Illness:(.*?)Past Medical History:",
        "Past Medical History": r"Past Medical History:(.*?)Social History:",
        "Social History": r"Social History:(.*?)Family History:",
        "Family History": r"Family History:(.*?)Physical Exam:",
        "Physical Exam": r"Physical Exam:(.*?)Discharge:",
        "Discharge": r"Discharge:(.*?)Pertinent Results:",
        "Pertinent Results": r"Pertinent Results:(.*?)CXR:",
        "CXR": r"CXR:(.*?)U/S:",
        "U/S": r"U/S:(.*?)Brief Hospital Course:",
        "Brief Hospital Course": r"Brief Hospital Course:(.*?)Medications on Admission:",
        "Medications on Admission": r"Medications on Admission:(.*?)Discharge Medications:",
        "Discharge Medications": r"Discharge Medications:(.*?)Discharge Disposition:",
        "Discharge Disposition": r"Discharge Disposition:(.*?)Discharge Diagnosis:",
        "Discharge Diagnosis": r"Discharge Diagnosis:(.*?)Discharge Condition:",
        "Discharge Condition": r"Discharge Condition:(.*?)Discharge Instructions:",
        "Discharge Instructions": r"Discharge Instructions:(.*?)Followup Instructions:",
        "Followup Instructions": r"Followup Instructions:(.*?)$",
    }
    # Initialize an empty dictionary to store section data
    section_data = {}
    # Extract section data using regular expressions
    for section, pattern in section_patterns.items():
        match = re.search(pattern, note, re.DOTALL)
        if match:
            section_data[section] = match.group(1).strip()
        else:
            section_data[section] = None
    # Convert dictionary to DataFrame
    df = pd.DataFrame.from_dict(section_data, orient='index', columns=['Text'])
    df.index.name = 'Section'
    return df

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ds12@localhost/patient_note'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class DischargeData(db.Model):
    __tablename__ = 'discharge_data'
    note_id = db.Column(db.String(), primary_key=True)
    storetime = db.Column(db.Date)
    subject_id = db.Column(db.String(8), nullable=False)
    text = db.Column(db.Text)

@app.route('/')
def index():
    # Patient
    subject_id = '10000032'
    fake = Faker()
    subject_name = fake.name()
    subject_dob = generate_random_dob()

    # Patient History
    discharge_entries = DischargeData.query.filter_by(subject_id=subject_id).all()
    discharge_arr = []
    for entry in discharge_entries:
        unsummarised_note = entry.text
        summarised_note = summarise(unsummarised_note)
        complaint = chief_complaint(summarised_note)
        entry_data = {
            'note_id': entry.note_id,
            'storetime': entry.storetime,
            'complaint': complaint,
            'text': summarised_note,
        }
        discharge_arr.append(entry_data)

    return render_template('index.html', discharge_arr=discharge_arr, subject_dob=subject_dob, subject_name=subject_name)

if __name__ == '__main__':
    app.run(debug=True)
