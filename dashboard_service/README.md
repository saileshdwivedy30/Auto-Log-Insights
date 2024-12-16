Kibana Version: 7.10.2 in tune with the Elasticsearch version.

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