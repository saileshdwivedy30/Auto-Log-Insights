from flask import Flask, request, jsonify
from redis import Redis
from rq import Queue
import boto3
import requests
from requests.auth import HTTPBasicAuth
from elasticsearch import Elasticsearch
import jwt
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from worker import background_task
from worker import process_log
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Logstash endpoint
LOGSTASH_URL = "http://34.72.223.230:5044"

# Connect to Redis
redis_conn = Redis(host='localhost', port=6379, decode_responses=True)

# Set up RQ Queue
queue = Queue(connection=redis_conn)

# Set up S3
s3 = boto3.client('s3')
S3_BUCKET_NAME = "logs-bucket-dcsc"

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
    hosts=["https://34.57.62.89:9200"],  # Elasticsearch host
    http_auth=("elastic", "shamal"),
    verify_certs=False,
    #headers={"Accept": "application/vnd.elasticsearch+json; compatible-with=7"},
    timeout=30,
    max_retries=10,
    retry_on_timeout=True
)
KIBANA_HOST = "http://34.28.235.62:5601" # will change once vm is up

def create_role(un):
    es.indices.create(index=f"{un}-logs", ignore=400)
    role_body = {
        "indices": [
            {
                "names": [f"{un}-logs"],  # Limit access to indices matching this pattern
                "privileges": ["read","write", "view_index_metadata"],
            } 
        ],
        "applications" : [
        {
            "application" : "kibana-.kibana",
            "privileges" : [
            "feature_discover.read",
            "feature_dashboard.read",
            "feature_visualize.read"
            ],
            "resources" : [
            f"space:{un}-space"
            ]
        }
    ],
    "run_as" : [ ],
    }
    es.security.put_role(name=f"{un}_role", body=role_body)
    print(f"Role created: {un}_role")

def create_index_pattern(index_name, space):
    kibana_url = KIBANA_HOST+f"/s/{space}/api/saved_objects/index-pattern"

    # Index pattern data
    data = {
        "attributes": {
            "title": index_name,
            "timeFieldName": "@timestamp"
        }
    }

    # Headers for the request
    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }

    # Authentication (replace with your credentials)
    auth = HTTPBasicAuth('elastic','shamal')

    # Send the POST request
    response = requests.post(kibana_url, json=data, headers=headers, auth=auth)

    # Print the response
    if response.status_code == 200 or response.status_code == 201:
        print("Index pattern created successfully:", response.json())
        response = response.json()
        return response["id"]
    else:
        print(f"Failed to create index pattern. Status Code: {response.status_code}")
        print(response.text)  

def create_user_space(un):
    HEADERS = {
            "kbn-xsrf": "true",
            "Content-Type": "application/json"
        }
    AUTH = HTTPBasicAuth('elastic', 'shamal')
    space_name = f"{un}-space"
    space_body = { 
            "id": space_name,
            "name": space_name,
            "description": f"Space for {space_name} user",
    }
    
    response = requests.post(f"{KIBANA_HOST}/api/spaces/space", json=space_body, headers=HEADERS, auth=AUTH)
    print(response.text)
    if response.status_code == 200:
        print(f"Space '{space_name}' created successfully.")
        index_pattern = create_index_pattern(index_name = f"{un}-logs", space=space_name)
        space_id = response.json()['id']

        config_data = {
            'attributes': {
                'defaultIndex': index_pattern,
                'defaultRoute': f"/app/discover#/?_g=(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-1y,to:now))&_a=(columns:!(ai_summary,event),filters:!(),index:'{index_pattern}',interval:auto,query:(language:kuery,query:''),sort:!())",
            },
        }
        print(f'{KIBANA_HOST}/s/{un}-space/api/saved_objects/config/7.10.2')
        response = requests.post(
            f'{KIBANA_HOST}/s/{un}-space/api/saved_objects/config/7.10.2',
            headers=HEADERS,
            json=config_data,
            auth=AUTH,
        )
        if response.status_code == 200:
            print(f"Default index pattern for '{space_name}' set successfully.")
        else:
                print(f"Error setting default index pattern for '{space_name}': {response.status_code} : {response.text}")
    else:
        print(f"Error creating space '{space_name}': {response.status_code}")
# Create a user and assign the restricted role
def create_user(un,pw):
    user_body = {
        "password": pw,        # User password
        "roles": [f"{un}_role"],    # Assign the restricted role
        "full_name": un,
    }
    es.security.put_user(username=un, body=user_body)
    print(f"User created: {un}")

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

    # Removed hashing of password: hashed_password = generate_password_hash(password)
    es.index(index=USER_PROFILES_INDEX, id=username, body={"username": username, "password": password})

    # Create user-specific index
    es.indices.create(index=f"{username}-logs", ignore=400)
    # Create a role for that user to only allow access to user-specific index and kibana discover page
    create_role(username)
    # Create index pattern to make the logs of user-index visible on discover page
    create_user_space(username)
    # Create actual Elastic Search user with restricted privileges
    create_user(username,password)
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
    if user_data["password"]!=password:
        return jsonify({"error": "Invalid username or password"}), 401

    token = jwt.encode({"username": username}, SECRET_KEY, algorithm="HS256").decode('utf-8')
    return jsonify({"token": token}), 200

#========================================== END CODE FOR USER SIGN/LOG IN ===========================================

#========================================== CODE FOR UPLOAD =========================================================

@app.route('/upload', methods=['POST'])
def upload_log():
    try:
        # Validate JWT token and extract username
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        try:
            token = auth_header.split(" ")[1]
            user_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            username = user_data.get("username")
            if not username:
                return jsonify({"error": "Invalid token: username missing"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"error": f"Authorization error: {str(e)}"}), 401

        # Validate the uploaded file
        if 'logfile' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        
        file = request.files['logfile']
        if file.filename == '':
            return jsonify({"error": "No file selected for uploading"}), 400

        # Read and process the file content
        try:
            log_content = file.read()
            # Ensure content is in bytes
            if not isinstance(log_content, bytes):
                log_content = log_content.encode("utf-8")
        except Exception as file_error:
            return jsonify({"error": f"Failed to process log file: {str(file_error)}"}), 400

        # Generate unique log ID and define S3 key
        log_id = str(uuid.uuid4())  # Unique log ID
        s3_key = f"{username}/{log_id}.log"  # Store logs in user specific folders

        # Upload the file to S3
        try:
            s3.put_object(Bucket=S3_BUCKET_NAME, Key=s3_key, Body=log_content)
        except Exception as s3_error:
            return jsonify({"error": f"Failed to upload log to S3: {str(s3_error)}"}), 500

        # Add the S3 key, username, and log ID to Redis queue for further processing
        try:
            queue.enqueue(process_log, s3_key, username, log_id)
        except Exception as queue_error:
            return jsonify({"error": f"Failed to enqueue log for processing: {str(queue_error)}"}), 500

        logging.info(f"Log uploaded successfully: User: {username}, Log ID: {log_id}")

        return jsonify({"message": "Log uploaded successfully", "log_id": log_id}), 200

    except Exception as e:
        logging.error(f"Unexpected error during upload: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
