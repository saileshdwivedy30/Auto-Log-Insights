# Logstash Setup

### **1. Create a Compute Engine VM**
- **Name**: `logstash-vm`
- **OS**: Ubuntu 20.04 LTS
- **Instance Type**: `e2-small`

---

### **2. Install Logstash**
1. Add the Elastic APT repository:
   ```bash
   wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
   echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-7.x.list
   sudo apt update
   ```

2. Install Logstash:
   ```bash
   sudo apt install logstash -y
   ```

3. Enable and start Logstash:
   ```bash
   sudo systemctl enable logstash
   sudo systemctl start logstash
   ```

---

### **3. Configure Logstash**
1. Create a configuration file for Logstash:
   ```bash
   sudo nano /etc/logstash/conf.d/logstash.conf
   ```

2. Restart Logstash to apply the configuration:
   ```bash
   sudo systemctl restart logstash
   ```
