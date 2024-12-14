# AI Analsys Service setup

This repository contains the implementation of a AI analysis service deployed on Google Cloud Platform (GCP). The service uses a Llama3 (8b) model through Groq inference API

---

## **Overview**

The AI anslysis service:
- Processes input logs via an HTTP POST request.
- Generates a concise analysis using a Llama3 (8b) model through Groq inference API.
- Exposes the service running on a dedicated GCP VM.

---

## **Setup Guide**

### **1. Create the AI VM on GCP**
1. Navigate to **Compute Engine > VM Instances** in the GCP Console.
2. Create a new instance:
   - **Name**: `ai-vm`
   - **Machine Type**: `e2-medium` (or higher if needed).
   - **Boot Disk**: Ubuntu 20.04 LTS with a minimum of 20GB.
   - Expose the Service Externally: Create a firewall rule in GCP to allow traffic on port 6000.

3. SSH into the VM:
   ```bash
   gcloud compute ssh ai-vm
3. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip -y
   pip3 install flask torch
4. Create and run the service:
   ```bash
    python3 ai_service_v1.py
