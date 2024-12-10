from flask import Flask, request, jsonify
from redis import Redis
from rq import Queue
import requests
from elasticsearch import Elasticsearch
import jwt
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

from tasks import background_task

app = Flask(__name__)

# Logstash endpoint
LOGSTASH_URL = "http://34.72.223.230:5044"

# Connect to Redis
redis_conn = Redis(host='localhost', port=6379, decode_responses=True)

# Set up RQ Queue
queue = Queue(connection=redis_conn)


#=========================================== CODE TO TEST REDIS Queue =================================

# Route to add tasks to the queue
@app.route('/add-task', methods=['POST'])
def add_task():
    data = request.get_json()
    delay = data.get('delay', 5)  # Default delay to 5 seconds if not provided

    # Enqueue task
    job = queue.enqueue(background_task, delay)
    return jsonify({"job_id": job.get_id(), "status": job.get_status()}), 202

# Route to check task status
@app.route('/task-status/<job_id>', methods=['GET'])
def task_status(job_id):
    job = queue.fetch_job(job_id)
    if job is None:
        return jsonify({"error": "Job not found"}), 404

    return jsonify({"job_id": job_id, "status": job.get_status(), "result": job.result}), 200


#========================================= END CODE TO TEST REDIS QUEUE ===============================

#========================================== CODE FOR USER SIGN/LOG IN ===========================================
# Elasticsearch setup
es = Elasticsearch(
    hosts=["https://34.57.62.89:9200"],  # Replace with your Elasticsearch host
    http_auth=("elastic", "shamal"),
    verify_certs=False,
    #headers={"Accept": "application/vnd.elasticsearch+json; compatible-with=7"},
    timeout=30,
    max_retries=10,
    retry_on_timeout=True
)

# Secret key for JWT
SECRET_KEY = "shamal-testing-some-key"

# User Profiles index
USER_PROFILES_INDEX = "user_profiles"

# Registration endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Check if username exists
    # it says to use username.keyword
    query = {"query": {"term": {"username.keyword": username}}}

    existing_user = es.search(index=USER_PROFILES_INDEX, body=query)
    if existing_user["hits"]["total"]["value"] > 0:
        return jsonify({"error": "Username already exists"}), 409

    hashed_password = generate_password_hash(password)
    es.index(index=USER_PROFILES_INDEX, id=username, body={"username": username, "password": hashed_password})

    # Create user-specific index
    es.indices.create(index=f"{username}-logs", ignore=400)
    return jsonify({"message": "User registered successfully"}), 201

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = es.get(index=USER_PROFILES_INDEX, id=username, ignore=404)
    if not user or not user.get("found"):
        return jsonify({"error": "Invalid username or password"}), 401

    user_data = user["_source"]
    if not check_password_hash(user_data["password"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    token = jwt.encode({"username": username}, SECRET_KEY, algorithm="HS256").decode('utf-8')
    return jsonify({"token": token}), 200

#========================================== END CODE FOR USER SIGN/LOG IN ===========================================

@app.route('/upload', methods=['POST'])
def upload_logs():
    # Extract logs array from the incoming JSON payload
    logs = request.json.get('logs', [])

    # Forward each log to Logstash in the required format
    for log in logs:
        # Ensure the log is formatted correctly for Logstash
        if "message" in log:
            response = requests.post(LOGSTASH_URL, json={"message": log["message"]})
            if response.status_code != 200:
                return jsonify({"error": "Failed to forward logs to Logstash"}), 500
        else:
            return jsonify({"error": "Invalid log format"}), 400

    return jsonify({"message": "Logs forwarded to Logstash successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
