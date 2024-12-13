# Auto Log Insighy

## Overview

This project aims to assist users to analyze the logs and common errors made during development. It is built on top of the ELK (Elasticsearch-Logstash-Kibana) stack, by generating AI insights on the logs for greater insight into the logs.

This helps in creating trends and report for teams to make the dev process more efficient.

## Contents

1. [System Description](#system-description)
2. [Installation](#installation-steps)
    - [Dashboard Service](#dashboard)


## System Description
![Architecture](/architecture.png)
1. API gateway
Accepts .txt, .csv files and puts them in a temporary folder on the server.

2. Client
Sends all the files in its log folder to the server.

## Installation steps
You require the following softwares:
- Kibana version: 7.10.2 in tune with the Elasticsearch version.
### Dashboard
The dashboard is a kibana service, configured specially to work with our Elasticsearch service. Follow these steps to set up Kibana. 
1. Create a google cloud VM node of type e2-medium with default settings.
2. Once created, SSH into the machine, and run the [setup-script](#dashboard_service\kibana_setup.sh) to install Kibana on the VM.
3. Modify the file "/etc/kibana/kibana.yml" as given in [kibana.yml](#dashboard_service\kibana.yaml). Add the missing fields: ES IP address and built-in user password.
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
6. Add a network tag "allow-kibana" to your VM.




