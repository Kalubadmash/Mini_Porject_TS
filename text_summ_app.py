from flask import Flask, render_template, request
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import defaultdict
import heapq
import os
from werkzeug.utils import secure_filename
from docx import Document
import pandas as pd

# Download necessary NLTK data files
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'docx', 'xlsx', 'txt'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_file(file_path):
    """Extract text from uploaded files."""
    file_extension = file_path.rsplit('.', 1)[1].lower()
    text = ""

    if file_extension == "docx":
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    elif file_extension == "xlsx":
        df = pd.read_excel(file_path)
        text = "\n".join(df.astype(str).stack().tolist())
    elif file_extension == "txt":
        with open(file_path, 'r') as file:
            text = file.read()
    return text

def summarize_text(text, summary_length):
    """Summarize the text."""
    # Tokenize text into sentences
    sentences = sent_tokenize(text)

    # Tokenize words and remove stopwords
    stop_words = set(stopwords.words("english"))
    word_frequencies = defaultdict(int)
    for word in word_tokenize(text):
        if word.lower() not in stop_words and word.isalpha():
            word_frequencies[word.lower()] += 1

    # Normalize word frequencies
    max_frequency = max(word_frequencies.values(), default=1)  # Avoid division by zero
    for word in word_frequencies:
        word_frequencies[word] = word_frequencies[word] / max_frequency

    # Score sentences based on word frequencies
    sentence_scores = defaultdict(int)
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in word_frequencies:
                sentence_scores[sentence] += word_frequencies[word]

    # Extract top N sentences
    summary_sentences = heapq.nlargest(summary_length, sentence_scores, key=sentence_scores.get)
    summary = " ".join(summary_sentences)
    return summary

@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    if request.method == "POST":
        text = request.form.get("text", "")
        summary_length_option = request.form.get("length", "medium")
        uploaded_file = request.files.get("file")

        # Map user selection to number of sentences
        length_map = {"short": 2, "medium": 4, "long": 6}
        summary_length = length_map.get(summary_length_option, 4)

        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)

            text = extract_text_from_file(file_path)

        if text:
            summary = summarize_text(text, summary_length)

    return render_template("index3.html", summary=summary)
print("python-docx is installed and working correctly!")
if __name__ == "__main__":
    app.run(debug=True)
