from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
import requests
import uuid
from time import sleep

app = Flask(__name__)

# Elasticsearch configuration
es = Elasticsearch(
    hosts=["http://34.57.62.89:9200"],  # Elasticsearch external IP
    timeout=30,
    max_retries=10,
    retry_on_timeout=True
)

# Logstash configuration
LOGSTASH_URL = "http://34.72.223.230:5044"  # Logstash external IP

# AI Service configuration
AI_SERVICE_URL = "http://34.56.187.96:6000/summarize"  # AI service external IP


@app.route('/upload', methods=['POST'])
def upload_log():
    
    #Upload a single log. The log is forwarded to Logstash, indexed in Elasticsearch, and the _id is returned.
    log = request.json.get('log')  # Expecting {"log": {"message": "..."}}
    if not log or "message" not in log:
        return jsonify({"error": "Invalid log format. Expecting a single log with 'message' field."}), 400

    # Add a unique identifier to the log
    unique_id = str(uuid.uuid4())
    log["unique_id"] = unique_id

    # Forward the log to Logstash
    logstash_response = requests.post(LOGSTASH_URL, json={"message": log["message"],"unique_id": unique_id})
    if logstash_response.status_code != 200:
        return jsonify({"error": "Failed to forward log to Logstash"}), 500

    # Wait briefly to ensure the log is indexed in Elasticsearch
    sleep(2)

    # Query Elasticsearch for the log using the unique identifier
    query = {
        "query": {
            "match": {
                "unique_id": unique_id
            }
        }
    }
    es_response = es.search(index="logs", body=query)
    hits = es_response["hits"]["hits"]

    if hits:
        # Get the _id of the indexed log
        log_id = hits[0]["_id"]
        return jsonify({"message": "Log uploaded successfully", "id": log_id}), 200
    else:
        return jsonify({"error": "Log not found in Elasticsearch"}), 404


@app.route('/analyze/<log_id>', methods=['GET'])
def analyze_log(log_id):
    """
    Analyze a specific log by its Elasticsearch _id. Retrieves the log, sends it to the AI service, and returns insights.
    """
    try:
        # Retrieve the specific log by its _id
        es_response = es.get(index="logs", id=log_id)
        log_content = es_response["_source"]["message"]

        # Send the log content to the AI service for insights
        ai_response = requests.post(AI_SERVICE_URL, json={"logs": log_content})
        summary = ai_response.json().get("summary", "No summary available.")

        return jsonify({"insight": summary}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve log or generate insight: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
