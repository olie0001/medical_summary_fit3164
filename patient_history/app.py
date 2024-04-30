from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from transformers import pipeline  # Import pipeline for easy use of T5
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

# Initialize the summarization pipeline with the T5 model pre-trained for medical summarization
summarizer = pipeline("summarization", model="Falconsai/medical_summarization", tokenizer="t5-large")

def extract_sections(note):
    sections = {}
    lines = note.split('\n')
    current_header = None
    content = []
    for line in lines:
        line = line.strip()
        if re.match(r'^[A-Z][\w\s-]*(?::)\s*$', line):
            if current_header is not None:
                sections[current_header] = ' '.join(content)
                print(f"Extracted section '{current_header}': {sections[current_header][:100]}...")  # Detailed section print
            current_header = line.rstrip(':')
            content = []
        else:
            content.append(line)
    if current_header is not None:
        sections[current_header] = ' '.join(content)
        print(f"Extracted section '{current_header}': {sections[current_header][:100]}...")  # Detailed section print
    return sections

def clean_text(text):
    text = re.sub(r'_{2,}|={2,}|-{2,}', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def summarize_section(text):
    cleaned_text = clean_text(text)
    tokens = cleaned_text.split()
    token_length = len(tokens)

    # Adjusting the threshold for short texts dynamically
    if token_length < 30:  # Lowered threshold to consider shorter texts
        print(f"Skipping summarization for short text: {cleaned_text[:60]}")
        return cleaned_text

    try:
        # Dynamically setting max_length based on input length
        summary = summarizer(
            cleaned_text,
            max_length=max(60, int(token_length * 1.5)),  # Ensure at least 50 tokens as max_length
            min_length=10,  # Minimum length of summary
            truncation=True
        )[0]['summary_text']
        print(f"Summarized text for '{cleaned_text[:30]}...': {summary[:100]}")
        return summary
    except Exception as e:
        print(f"Error during summarization: {str(e)}")
        return cleaned_text  # Fallback to original text on error


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    subject_id = request.form['subject_id']
    discharge_entries = DischargeData.query.filter_by(subject_id=subject_id).all()
    discharge_arr = []
    if not discharge_entries:
        return render_template('index.html', discharge_arr=[], no_data="No records found for ID: " + subject_id)

    for entry in discharge_entries:
        sections = extract_sections(entry.text)
        summarized_sections = {header: summarize_section(content) for header, content in sections.items()}
        entry_data = {
            'note_id': entry.note_id,
            'storetime': entry.storetime.strftime("%Y-%m-%d %H:%M:%S"),
            'text': "\n\n".join(f"{header}:\n{content}" for header, content in summarized_sections.items()),
            'subject_id': subject_id
        }
        discharge_arr.append(entry_data)

    return render_template('index.html', discharge_arr=discharge_arr)

if __name__ == '__main__':
    app.run(debug=True)
