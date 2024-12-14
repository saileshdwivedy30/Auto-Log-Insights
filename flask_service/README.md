## **Flask API Setup**

### **1. Create and Configure VM**
1. **Create a VM on GCP**:
   - Use **Ubuntu 20.04 LTS** as the operating system.
   - Assign a network tag (e.g., `flask-api`).

2. **Update the System**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **Install Python and Dependencies**:
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
