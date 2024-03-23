from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # Simple text for the medical note
    medical_note = "This is a medical note."
    return render_template('index.html', medical_note=medical_note)

if __name__ == '__main__':
    app.run(debug=True)