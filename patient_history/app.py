from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from transformers import AutoTokenizer, BertLMHeadModel
import re

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

def summarise(note):
    model_name = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"
    model = BertLMHeadModel.from_pretrained(model_name, is_decoder=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    inputs = tokenizer.encode("summarize: " + note, return_tensors="pt", max_length=512, truncation=True)
    summary_ids = model.generate(inputs, max_length=513, min_length=50, num_beams=4, early_stopping=True)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

def chief_complaint(note):
    complaint = re.search(r'chief complaint\s*:\s*(.*?)(major surgical|history of present illness|$)', note, re.IGNORECASE)
    if complaint:
        return complaint.group(1).strip()
    else:
        return None

@app.route('/', methods=['GET'])
def index():
    # This route now only handles GET requests and shows an empty search form
    return render_template('index.html', discharge_arr=[])

@app.route('/search', methods=['POST'])
def search():
    subject_id = request.form['subject_id']
    discharge_entries = DischargeData.query.filter_by(subject_id=subject_id).all()
    discharge_arr = []

    if not discharge_entries:
        # Pass a message if no entries are found
        return render_template('index.html', discharge_arr=[], no_data="No records found", subject_id=subject_id)

    for entry in discharge_entries:
        unsummarised_note = entry.text
        summarised_note = summarise(unsummarised_note)
        complaint = chief_complaint(summarised_note)
        entry_data = {
            'note_id': entry.note_id,
            'storetime': entry.storetime,
            'complaint': complaint,
            'text': summarised_note,
            'subject_id': subject_id  
        }
        discharge_arr.append(entry_data)

    return render_template('index.html', discharge_arr=discharge_arr, subject_id=subject_id)

if __name__ == '__main__':
    app.run(debug=True)
