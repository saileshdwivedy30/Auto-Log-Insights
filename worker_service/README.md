
# Worker Deployment Guide

## 1. Create and Configure a VM

### Create a Virtual Machine
- **Platform**: Google Cloud Platform (GCP) or equivalent.  
- **Machine Type**: `e2-small` (or higher based on workload).  
- **Boot Disk**: Ubuntu 20.04 LTS.  
- **Expose External Access**: Create a firewall rule to allow traffic on port **6379** (Redis).  

### Update and Upgrade the System
```
sudo apt update && sudo apt upgrade -y
```

### Install Required Packages
Install Python, Pip, and Redis:
```
sudo apt install python3 python3-pip redis-server -y
```

---

## 2. Install Python Dependencies
Install the required Python libraries for the worker:
```
pip3 install rq redis boto3 requests elasticsearch logging
```

---

## 3. Set Up Redis
Start the Redis server and enable it to run at boot:
```
sudo systemctl start redis
sudo systemctl enable redis
```

Test Redis to ensure it is working:
```
redis-cli ping
```
You should see a response: `PONG`.

---

## 4. Configure Worker Environment

### Update Configuration Variables in `worker.py`
Modify the following variables as per your setup:
- **S3_BUCKET_NAME**: Replace with your actual S3 bucket name.
- **Elasticsearch Host**: Update the `hosts` and `http_auth` fields for your Elasticsearch instance.
- **AI_SERVICE_URL**: Provide the correct endpoint for your AI service.
- **Redis Connection**: If the Redis server is hosted on another VM, update the `host` in `Redis(host='localhost', port=6379)`.

---

## 5. Run the Worker Script
Start the worker to process jobs from the Redis queue:
```
python3 worker.py
```
