# Auto Log Insights

Team 15 members: Shamal Shaikh, Sailesh Dwivedy, Ghritachi Mahajani

Demo video link: https://www.youtube.com/watch?v=aOD9OG1qHYc

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

3.  Run the client.py from command-line (Change the JWT token and log file path variables with your file path):
```
 python3 local_client.py
```

4. Deployment setup: Please take a look at this to learn [step-by-step guide](https://docs.google.com/document/d/1ywGi7h7ukjh3HJHiGiw5DCmhydxCjDbr1fN6gwZBR9c/edit?usp=sharing)

## 📂 Repository Structure
```
├── flask_service/               # Flask RESTful API implementation
├── workers_service/           # Redis worker scripts for asynchronous job processing
├── ai_service/        # Integration with LLaMA 3 AI model
├── dashboard_service/         # Kibana dashboard configuration
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

### Worker job:
- Workers service listens to jobs from the queue 
- Then it fetches associated files from S3. 
- This is sent to Logstash that parses them, and stores structured parsed data in Elasticsearch.
- The AI Service gets the parsed logs and sends the relevant parts to the AI service to generate insights.

### AI Service:
- AI service consists of an open-source Llama3-8b model which is being used through Groq inference API.
- It is prompted to give an answer in the form “Analysis: <>, Fixes: <>”.
- The AI Insight is added back to the corresponding document in Elasticsearch.

### Dashboard Service
The dashboard is a kibana service, configured specially to work with our Elasticsearch service. (IP - 34.28.235.62:5601)

## Installation steps
Please see each individual folder

- [Flask Service](/flask_service/README.md)
- [Elasticsearch Service](/elasticsearch-service/README.md)
- [Logstash](/logstash_config/README.md)
- [AI Service](/ai_service/README.md)
- [Dashboard VM](/dashboard_service/)



🤝 Contributors
- [Shamal Shaikh](https://www.linkedin.com/in/shamal-shaikh/)
- Sailesh Dwivedy
- [Ghritachi Mahajani](https://www.linkedin.com/in/ghritachi-mahajani/)
