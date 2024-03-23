from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

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

@app.route('/')
def index():
    # Query the first 'text' entry from the discharge_first_10 table
    note_entry = DischargeFirst10.query.first()
    medical_note = note_entry.text 
    return render_template('index.html', medical_note=medical_note)

if __name__ == '__main__':
    app.run(debug=True)