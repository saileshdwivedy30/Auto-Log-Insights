# Auto Log Insights

Team 15 members: Shamal Shaikh, Sailesh Dwivedy, Ghritachi Mahajani

## Overview

This project aims to assist users to analyze the logs and common errors made during development. It is built on top of the ELK (Elasticsearch-Logstash-Kibana) stack, by adding AI-generated insights on the logs.

This helps in creating trends and report for teams to make the dev process more efficient.

## 🧑‍💻 Getting started
1. Clone the Repository
```
    git clone https://github.com/cu-csci-4253-datacenter-fall-2024/finalproject-final-project-team-15.git
    cd finalproject-final-project-team-15
```
2. Install Dependencies:
    Ensure you have Python 3.8+ installed.

3.  Run the client.py from command-line:
```
 python3 local_client.py
```

## 📂 Repository Structure
```
├── api/               # Flask RESTful API implementation
├── workers/           # Redis worker scripts for asynchronous job processing
├── ai_service/        # Integration with LLaMA 3 AI model
├── dashboard/         # Kibana dashboard configuration
├── requirements.txt   # Python dependencies
└── README.md          # This documentation
```

## Contents

1. [System Description](#system-description)
    - [Register](#Register)
    - [Login](#Login)
    - [Upload](#Upload)
    - [Worker](#Worker-job)
    - [AI Service](#ai-service)
    - [Dashboard Service](#dashboard-service)
2. [Installation](#installation-steps)
    - [Dashboard VM](#dashboard-vm)



## System Description
![Architecture](/architecture.jpg)
### Flask REST Service
Implements the /register, /login and /upload REST endpoints.

#### Register
- Creates user credentials in the Elasticsearch system.
- Creates a <b>user-specific index</b> to store user's logs.
- Creates <b>user-specific role</b>  that allows access only to that index and "read" privileges in Kibana to 'discover' and 'dashboard' features. 
- Creates a <b>user-specific space</b>  in Kibana to ensure user can only see their own data on Kibana
- Creates an <b>index pattern</b> in that space (required to see data in Kibana features).

#### Login
- User needs to login to receive a JWT token which can be used for future upload requests. 
- User can now upload logs and receive insight for those.

#### Upload
- Logs are uploaded via the “/upload” endpoint.
- The log file is stored in S3 with a unique key (<username>/<log_id>.log).
- Logs uploaded are sent to Redis message queue using the unique ID, allowing load balancing and async processing of jobs.

#### Worker job:
- Workers service listens to jobs from the queue 
- Then it fetches associated files from S3. 
- This is sent to Logstash that parses them, and stores structured parsed data in Elasticsearch.
- The AI Service gets the parsed logs and sends the relevant parts to the AI service to generate insights.

#### AI Service:
- AI service consists of an open-source Llama3-8b model which is being used through Groq inference API.
- It is prompted to give an answer in the form “Analysis: <>, Fixes: <>”.
- The AI Insight is added back to the corresponding document in Elasticsearch.

### Dashboard Service
The dashboard is a kibana service, configured specially to work with our Elasticsearch service. (IP - 34.28.235.62:5601)

## Installation steps
You require the following softwares:
- Kibana version: 7.10.2 in tune with the Elasticsearch version.

### Dashboard VM
Follow these steps to set up Kibana. 
1. Create a google cloud VM node with following settings:
<b>Name</b>: dashboard-vm
<b>Type</b>: e2-medium <b>Boot disk</b>: Ubuntu 20.04 LTS. <b>Network Tag</b>: “allow-kibana”
 
2. Once created, SSH into the machine, and run the [setup-script](dashboard_service/kibana_setup.sh) to install Kibana on the VM.
3. Modify the file "/etc/kibana/kibana.yml" as given in [kibana.yml](dashboard_service/kibana.yaml). Add the missing fields: ES IP address and built-in user password.
4. Run the following to start and enable kibana service

```
sudo systemctl start kibana
sudo systemctl enable kibana
```
5. Allow external access to your Dashboard service (kibana runs on port 5601 by default) by setting up a firewall rule:
```
gcloud compute firewall-rules create allow-kibana \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:5601 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=allow-kibana
```

🤝 Contributors
- [Shamal Shaikh](https://www.linkedin.com/in/shamal-shaikh/)
- Sailesh Dwivedy
- Ghritachi Mahajani


Demo video link: https://www.youtube.com/watch?v=aOD9OG1qHYc



