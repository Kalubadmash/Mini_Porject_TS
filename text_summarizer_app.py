from flask import Flask, render_template, request
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import defaultdict
import heapq

# Download necessary NLTK data files
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

app = Flask(__name__)

def summarize_text(text, summary_length=3):
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
        text = request.form.get("text")
        if text:
            summary = summarize_text(text, summary_length=3)
    return render_template("index1.html", summary=summary)

if __name__ == "__main__":
    app.run(debug=True)
