from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from transformers import AutoTokenizer, BertLMHeadModel
import re
from faker import Faker
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ds12@localhost:5433/patient_note'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class DischargeData(db.Model):
    __tablename__ = 'discharge_data'  # Changed to a more appropriate table name
    note_id = db.Column(db.String(15), primary_key=True)
    subject_id = db.Column(db.String(8), nullable=False)
    storetime = db.Column(db.Date)
    text = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text)
    dob = db.Column(db.Date)
    complaint = db.Column(db.Text, nullable=False)
    patient_sex = db.Column(db.String(6), nullable=False)
    history_present_illness = db.Column(db.Text, nullable=False)
    family_history = db.Column(db.Text, nullable=False)
    past_history = db.Column(db.Text, nullable=False)

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
    
    # Patient History
    discharge_entries = DischargeData.query.filter_by(subject_id=subject_id).all()
    discharge_arr = []
    for entry in discharge_entries:
        entry_data = {
            'note_id': entry.note_id,
            'storetime': entry.storetime,
            'complaint': entry.complaint,
            'text': entry.text,
            'history_present_illness': entry.history_present_illness,
            'family_history': entry.family_history,
            'past_history': entry.past_history,
            'subject_id': entry.subject_id,
            'name': entry.name,  # Name from database
            'dob': entry.dob.strftime('%Y-%m-%d') if entry.dob else 'N/A',  # Formatting date of birth
            'patient_sex': entry.patient_sex
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

    if not discharge_arr:
        # No records found, set defaults to indicate non-existent patient
        subject_name = "Non-existent Patient"
        subject_dob = "N/A"
        patient_sex = "Unknown"
    else:
        # Get details from the first record
        subject_name = discharge_arr[0]['name']
        subject_dob = discharge_arr[0]['dob']
        patient_sex = discharge_arr[0]['patient_sex']

    return render_template('index.html', discharge_arr=discharge_arr, radiology_arr=radiology_arr,
                           subject_id=subject_id, subject_name=subject_name,
                           subject_dob=subject_dob, patient_sex=patient_sex)


if __name__ == '__main__':
    app.run(debug=True)

 