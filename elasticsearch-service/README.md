
# Elasticsearch Setup

## **1. Set Up Elasticsearch VM**

### **Create a Compute Engine Instance**
1. Create a new VM with the following specifications:
   - **Name**: `elasticsearch-vm`
   - **Machine type**: `e2-medium`
   - **Boot disk**: Ubuntu 20.04 LTS.

---

## **2. Install Elasticsearch**

### **Install Java**
1. SSH into the VM:
   ```bash
   gcloud compute ssh elasticsearch-vm
   ```
2. Update the system and install Java:
   ```bash
   sudo apt update
   sudo apt install openjdk-11-jdk -y
   ```

### **Install Elasticsearch**
1. Download and install Elasticsearch:
   ```bash
   wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.10.2-amd64.deb
   sudo dpkg -i elasticsearch-7.10.2-amd64.deb
   ```
2. Enable and start the Elasticsearch service:
   ```bash
   sudo systemctl enable elasticsearch
   sudo systemctl start elasticsearch
   ```
3. Verify Elasticsearch is running locally:
   ```bash
   curl http://localhost:9200
   ```
   - You should see a JSON response indicating Elasticsearch is running.

---

## **3. Configure External Access**

### **Edit Elasticsearch Configuration**
1. Open the Elasticsearch configuration file:
   ```bash
   sudo nano /etc/elasticsearch/elasticsearch.yml
   ```
2. Add the following lines to configure network and discovery settings:
   ```yaml
   network.host: 0.0.0.0
   http.port: 9200
   discovery.seed_hosts: []
   cluster.initial_master_nodes: ["elasticsearch-vm"]
   node.name: "elasticsearch-vm"
   ```

4. Restart Elasticsearch to apply the changes:
   ```bash
   sudo systemctl restart elasticsearch
   ```

5. Check if Elasticsearch is running successfully:
   ```bash
   sudo systemctl status elasticsearch
   ```

---

## **4. Configure Firewall Rules**

### **Allow External Traffic**
1. Create a firewall rule to allow traffic on port `9200`:
   ```bash
   gcloud compute firewall-rules create allow-elasticsearch \
       --direction=INGRESS \
       --priority=1000 \
       --network=default \
       --action=ALLOW \
       --rules=tcp:9200 \
       --source-ranges=0.0.0.0/0 \
       --target-tags=elasticsearch
   ```
