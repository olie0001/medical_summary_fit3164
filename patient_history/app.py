from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from transformers import AutoTokenizer, BioGptForCausalLM

# NLP code
def summarise(note):
    # BioGPT
    tokenizer = AutoTokenizer.from_pretrained("microsoft/biogpt")
    model = BioGptForCausalLM.from_pretrained("microsoft/biogpt")

    # Tokenization and summarisation
    inputs = tokenizer.encode("summarize: " + note, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs, max_length=1025, min_length=200, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    return summary

app = Flask(__name__)

# Configure the SQLAlchemy part to connect to the PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ds12@localhost/patient_note'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database connection
db = SQLAlchemy(app)

# Define your database model
class DischargeFirst10(db.Model):
    __tablename__ = 'discharge_first_10'  # Your table name
    note_id = db.Column(db.String(), primary_key=True)  # Assuming note_id is the primary key
    text = db.Column(db.Text)  # Assuming 'text' is the name of the column to retrieve
    charttime = db.Column(db.DateTime)

@app.route('/')
def index():
    # Query the first 'text' entry from the discharge_first_10 table
    note_entry = DischargeFirst10.query.first()
    medical_note = note_entry.text
    # Call the summarisation function 
    note = summarise(medical_note)
    date = note_entry.charttime
    return render_template('index.html', medical_note=note, date=date)

if __name__ == '__main__':
    app.run(debug=True)