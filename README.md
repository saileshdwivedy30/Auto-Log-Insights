# Auto Log Insights

## Overview

This project aims to assist users to analyze the logs and common errors made during development. It is built on top of the ELK (Elasticsearch-Logstash-Kibana) stack, by adding AI-generated insights on the logs.

This helps in creating trends and report for teams to make the dev process more efficient.

## Contents

1. [System Description](#system-description)
2. [Installation](#installation-steps)
    - [Dashboard Service](#dashboard)


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


## Installation steps
You require the following softwares:
- Kibana version: 7.10.2 in tune with the Elasticsearch version.
### Dashboard Service
The dashboard is a kibana service, configured specially to work with our Elasticsearch service. Follow these steps to set up Kibana. 
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


Demo video link: https://www.youtube.com/watch?v=aOD9OG1qHYc



