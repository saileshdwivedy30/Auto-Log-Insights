from elasticsearch import Elasticsearch
import requests
from requests.auth import HTTPBasicAuth

import warnings
from urllib3.exceptions import InsecureRequestWarning
from elasticsearch.exceptions import NotFoundError, ElasticsearchException


# Suppress SSL warnings
warnings.simplefilter('ignore', InsecureRequestWarning)

class ESClient:
    def __init__(self): 
        self.host = "https://34.57.62.89:9200"
        self.superuser = ("elastic","shamal")
        self.es = Elasticsearch(
            hosts=[self.host],  # Elasticsearch external IP
            http_auth= self.superuser,
            verify_certs=False,
            timeout=30,
            max_retries=10,
            retry_on_timeout=True
        )
        try:
            info= self.es.info()
            print("connected to elastic search", info)
        except Exception as e:
            print("Error:", e)
        self.connect_kibana()
        
    def connect_kibana(self):
        self.KIBANA_HOST = "http://localhost:5601"
    
    def check_user(self, username):
        # Username to check
        try:
            # Check if the user exists
            response = self.es.transport.perform_request("GET", f"/_security/user/{username}")
            print(f"User '{username}' exists. Details:")
            print(response)
            return username, response[username]["metadata"]["pw"]
        except NotFoundError:
            print(f"User '{username}' does not exist.")
            return ()
        except ElasticsearchException as e:
            print(f"Error checking user existence: {e}")

    def create_role(self, un):
        self.es.indices.create(index=f"{un}-logs", ignore=400)
        role_body = {
            "indices": [
                {
                    "names": [f"{un}-logs"],  # Limit access to indices matching this pattern
                    "privileges": ["read","write", "view_index_metadata"],
                } 
            ],
            "applications": [
                {
                    "application": "kibana-.kibana",
                    "privileges": ["read"],
                    "resources": ["*"]  # Can be restricted to specific space (e.g.,)
                }
                    # Allow only read privileges
                    # "query": "{\"term\": {\"user_id\": \""+un+"\"}}"  # Optional: Apply a document-level security query
                    ]
        }
        self.es.security.put_role(name=f"{un}_project_role", body=role_body)
        print(f"Role created: {un}_project_role")
        self.create_index_pattern(index_name = f"{un}-logs")
              
    def create_index_pattern(self,index_name):
        kibana_url = self.KIBANA_HOST+"/api/saved_objects/index-pattern"

        # Index pattern data
        data = {
            "attributes": {
                "title": index_name,
                "timeFieldName": "@timestamp"
            }
        }

        # Headers for the request
        headers = {
            "kbn-xsrf": "true",
            "Content-Type": "application/json"
        }

        # Authentication (replace with your credentials)
        auth = HTTPBasicAuth(*self.superuser)

        # Send the POST request
        response = requests.post(kibana_url, json=data, headers=headers, auth=auth)

        # Print the response
        if response.status_code == 200 or response.status_code == 201:
            print("Index pattern created successfully:", response.json())
        else:
            print(f"Failed to create index pattern. Status Code: {response.status_code}")
            print(response.text)

    # Create a user and assign the restricted role
    def create_user(self,un,pw):
        user_body = {
            "password": pw,        # User password
            "roles": [f"{un}_project_role"],    # Assign the restricted role
            "full_name": un,
            "metadata": {
                "pw":pw
            }
        }
        self.es.security.put_user(username=un, body=user_body)
        print(f"User created: {un}")

    def registerUser(self,un,pw):
        self.create_role(un)
        self.create_user(un,pw)

    def loginUser(self, un, pw):

        try: 
            response = requests.get(
            "http://localhost:5601/api/security/v1/me",
            auth=HTTPBasicAuth(un, pw)
        )

            # Check if login was successful
            if response.status_code == 200:
                print("Authentication successful", response.text)
                id = self.get_index_pattern_id(un,pw)
                return self.get_kibana_url(un,id)   
            else:
                print(f"Authentication failed: {response.status_code}")
        except Exception as e:
            print("ERROR: ",e)
        return -1

    def get_kibana_url(self, un,id,):
        # /?_a=(index:'{un}-index')
        filters=f"?_g=(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-30d,to:now))&_a=(columns:!(message),filters:!(),index:'{id}',interval:auto,query:(language:kuery,query:''),sort:!())"
        return f"http://localhost:5601/app/discover#/"+filters
    
    def get_index_pattern_id(self,un,pw):
        headers = {"kbn-xsrf": "true"}  # Required header for Kibana API

        # Index pxattern to search for
        pattern_name = f"{un}-logs"

        auth = HTTPBasicAuth(un,pw)
        # API endpoint to find index patterns
        url = self.KIBANA_HOST+"/api/saved_objects/_find?type=index-pattern&search_fields=title&search="+pattern_name

        # Send the request
        response = requests.get(url, headers=headers, auth=auth)

        if response.status_code == 200:
            data = response.json()
            # Check if the index pattern exists
            # print(data)
            if data['saved_objects']:
                # Extract the ID for the matching pattern
                index_pattern = data['saved_objects'][0]  # Assuming the first match is the desired one
                index_pattern_id = index_pattern['id']
                print(f"Index Pattern ID for '{pattern_name}': {index_pattern_id}")
                return index_pattern_id
            else:
                print(f"No index pattern found for '{pattern_name}'")
                return -1
        else:
            print(f"Failed to fetch index patterns. Status Code: {response.status_code}")
            print(response.text)
            return -1

    


if __name__=="__main__":
    pass
    