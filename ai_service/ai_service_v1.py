from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)
summarizer = pipeline("summarization", model="t5-small")

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.json  # Input payload
        #log_texts = data.get("logs")  # Extract the 'log' field from the payload
        log_texts = data.get("logs", {}).get("log", "")  # Look for 'logs' and extract 'log'

        if not log_texts:
            return jsonify({"error": "Missing 'log' in the input payload"}), 400

        # Ensure log_texts is a string or list of strings
        if isinstance(log_texts, dict):
            log_texts = log_texts.get("logs", "")

        if not isinstance(log_texts, (str, list)):
            return jsonify({"error": "'log' should be a string or a list of strings"}), 400

        # Generate the summary
        summary = summarizer(log_texts, max_length=100, min_length=25, do_sample=False)
        return jsonify({"summary": summary[0]["summary_text"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
