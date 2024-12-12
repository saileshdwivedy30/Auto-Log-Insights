wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list

sudo apt update
sudo apt install kibana=7.10.2
# no auto-upgrade
sudo apt-mark hold kibana

# manual step
# sudo nano /etc/kibana/kibana.yml (add your own content)

sudo systemctl start kibana
sudo systemctl enable kibana

# add firewall rules
