from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)
summarizer = pipeline("summarization", model="t5-small")

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    log_texts = data.get("logs", "")
    summary = summarizer(log_texts, max_length=100, min_length=25, do_sample=False)[0]['summary_text']
    return jsonify({"summary": summary}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
