from rq import Worker, Queue
from redis import Redis
import boto3
import requests
from elasticsearch import Elasticsearch
import logging
import json
from tasks import process_log
import time

# =========== CODE FOR WORKER =============

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# S3 Configuration
s3 = boto3.client('s3')
S3_BUCKET_NAME = "logs-bucket-dcsc"

# Elasticsearch Configuration
#es = Elasticsearch(hosts=["http://34.57.62.89:9200"])

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

# AI Service Configuration
AI_SERVICE_URL = "http://34.45.138.21:6000/summarize"

# Redis Connection
redis_conn = Redis(host='localhost', port=6379)   # localhost for now, will need to change if moved to new VM.

def background_task(n):
    time.sleep(n)
    return f"Task completed in {n} seconds!"

def process_log(s3_key, username, log_id):
    print(f"Processing log with S3 key: {s3_key}, Username: {username}, Log ID: {log_id}")
    """
    Processes a log by fetching it from S3, sending it to Logstash,
    retrieving parsed data from Elasticsearch, sending it to AI service,
    and storing the result back in Elasticsearch.
    """
    try:
        # Step 1: Fetch the log from S3
        logging.info(f"Fetching log {log_id} for user {username} from S3.")
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        log_content = response['Body'].read().decode('utf-8')


        # Step 2: Send the log to Logstash for parsing
        logging.info(f"Sending log {log_id} to Logstash for parsing.")
        logstash_payload = {
            "log": log_content,
            "username": username,
            "log_id": log_id
        }
        logstash_response = requests.post(
            "http://34.72.223.230:5044",
            json=logstash_payload
        )
        logstash_response.raise_for_status()

        # Step 3: Fetch the parsed log from Elasticsearch
        logging.info(f"Fetching parsed log {log_id} from Elasticsearch.")
        es_query = {
            "query": {
                "term": {
                    "log_id.keyword": log_id
                }
            }
        }
        logging.info(f"The logid being matched: {log_id}")
        logging.info(f"The query output is: {es_query}")
        time.sleep(10)
        es_response = es.search(index=f"{username}-logs", body=es_query)
        logging.info(f"The es response is: {es_response}")
        if es_response["hits"]["total"]["value"] == 0:
            raise Exception(f"Parsed log {log_id} not found in Elasticsearch.")

        parsed_log = es_response["hits"]["hits"][0]["_source"]

        # Step 4: Send the parsed log to the AI summarization service
        logging.info(f"Sending parsed log {log_id} to AI service for summarization.")
        ai_response = requests.post(
            AI_SERVICE_URL,
            json={"logs": parsed_log}
        )
        ai_response.raise_for_status()
        ai_summary = ai_response.json().get("summary", "No summary generated.")

        # Step 5: Store the AI summary back in Elasticsearch
        logging.info(f"Updating Elasticsearch with AI summary for log {log_id}.")
        es.update(
            index=f"{username}-logs",
            id=es_response["hits"]["hits"][0]["_id"],
            body={
                "doc": {
                    "ai_summary": ai_summary
                }
            }
        )

        logging.info(f"Log {log_id} processed successfully for user {username}.")

    except Exception as e:
        logging.error(f"Error processing log {log_id} for user {username}: {str(e)}")

if __name__ == "__main__":
    """
    Main function to initialize and start the worker.
    """
    try:
        logging.info("Starting worker...")
        queue = Queue("default", connection=redis_conn)
        worker = Worker([queue], connection=redis_conn)  # Listens to the 'default' queue
        worker.work()  # Starts processing jobs from the queue
    except Exception as e:
        logging.error(f"Worker initialization failed: {str(e)}")
