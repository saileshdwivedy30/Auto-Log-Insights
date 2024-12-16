## **Flask API Setup**

### **1. Create and Configure VM**
1. **Create a VM on GCP**:
   - **Machine Type**: `e2-small` (or higher if needed).
   - **Boot Disk**: Ubuntu 20.04 LTS as the operating system.
   - Expose the Service Externally: Create a firewall rule in GCP to allow traffic on port 5000.


3. **Update the System**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **Install Python and Dependencies**:
   ```bash
   sudo apt install python3 python3-pip -y
   pip3 install flask elasticsearch requests
   ```

---

### **2. Flask API Setup**
1. **Create the flask api service
2. **Run the Flask Application**:
   ```bash
   python3 new_app.py
   ```

---

### **3. Configure External Access**
1. **Create a Firewall Rule**:
   - Go to **VPC Network > Firewall Rules** in the GCP Console.
   - Add a rule to allow TCP traffic on port `5000` for instances with the network tag `flask-api`.
