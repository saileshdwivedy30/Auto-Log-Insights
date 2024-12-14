from flask import Flask, request, jsonify
import os
from groq import Groq

app = Flask(__name__)

# Initialize the Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/summarize', methods=['POST'])
def ai_analysis():
    try:
        data = request.json  # Input payload

        # Attempt to extract 'log' field from the incoming JSON
        log_texts = None
        if isinstance(data, dict) and "logs" in data:
            # If 'logs' is a dictionary, extract its 'log' field
            if isinstance(data["logs"], dict):
                log_texts = data["logs"].get("log", "")
            # If 'logs' is already a string, use it directly
            elif isinstance(data["logs"], str):
                log_texts = data["logs"]

        if not log_texts:
            return jsonify({"error": "Missing 'log' in the input payload"}), 400

        # Use Groq API to perform AI analysis
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Give your analysis on the following log and suggest how to fix, in 3 lines: {log_texts}",
                }
            ],
            model="llama3-8b-8192",
        )

        # Extract the AI analysis response
        ai_analysis_result = chat_completion.choices[0].message.content

        return jsonify({"summary": ai_analysis_result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
