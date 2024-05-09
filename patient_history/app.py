from flask import Flask, render_template, request
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

def extract(note):
    complaint = re.search(r'chief complaint\s*:\s*(.*?)(major surgical|history of present illness|$)', note, re.IGNORECASE)
    complaint = complaint.group(1).strip()
    patient_sex = re.search(r'sex\s*:\s*([MF])', note, re.IGNORECASE)
    patient_sex = patient_sex.group(1).strip()
    if patient_sex == 'f':
        patient_sex = 'Female'
    elif patient_sex == 'm':
        patient_sex = 'Male'
    return complaint, patient_sex

def generate_random_dob(start_year=1930, end_year=2020):
    start_date = datetime(year=start_year, month=1, day=1)
    end_date = datetime(year=end_year, month=12, day=31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ds12@localhost/patient_note'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class DischargeData(db.Model):
    __tablename__ = 'discharge_first_10'
    note_id = db.Column(db.String(), primary_key=True)
    storetime = db.Column(db.Date)
    subject_id = db.Column(db.String(8), nullable=False)
    text = db.Column(db.Text)

class RadiologyData(db.Model):
    __tablename__ = 'radiology_data'
    note_id = db.Column(db.String(15), primary_key=True)
    subject_id = db.Column(db.String(8), nullable=False)
    storetime = db.Column(db.Date)
    text = db.Column(db.Text)
    examination = db.Column(db.Text, nullable=False)
    summarised = db.Column(db.Text, nullable=False)



@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    # Patient
    subject_id = request.form['subject_id']
    fake = Faker()
    subject_name = fake.name()
    subject_dob = generate_random_dob().strftime('%Y-%m-%d')

    # Patient History
    discharge_entries = DischargeData.query.filter_by(subject_id=subject_id).all()
    discharge_arr = []
    for entry in discharge_entries:
        unsummarised_note = entry.text
        summarised_note = summarise(unsummarised_note)
        complaint, patient_sex = extract(summarised_note)
        entry_data = {
            'note_id': entry.note_id,
            'storetime': entry.storetime,
            'complaint': complaint,
            'text': summarised_note,
            'subject_id': subject_id
        }
        discharge_arr.append(entry_data)

    # Radiology
    radiology_entries = RadiologyData.query.filter_by(subject_id=subject_id).all()
    radiology_arr = []
    for entry in radiology_entries:
        entry_data = {
            'note_id': entry.note_id,
            'storetime': entry.storetime,
            'text': entry.summarised,
            'subject_id': subject_id,
            'examination': entry.examination
        }
        radiology_arr.append(entry_data)

    return render_template('index.html', discharge_arr=discharge_arr, radiology_arr=radiology_arr, subject_id=subject_id, subject_dob=subject_dob, subject_name=subject_name, patient_sex=patient_sex)


if __name__ == '__main__':
    app.run(debug=True)