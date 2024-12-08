from elasticsearch import Elasticsearch
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings
warnings.simplefilter('ignore', InsecureRequestWarning)

class ESClient:
    def __init__(self): 

        self.es = Elasticsearch(
            hosts=["https://34.57.62.89:9200"],  # Elasticsearch external IP
            http_auth=("elastic", "shamal"),
            verify_certs=False,
            timeout=30,
            max_retries=10,
            retry_on_timeout=True
        )
        print("\n\n========================\n\n")
        # try:
        info= self.es.info()
        print("\n\n========================\n\n")
        print("check connection", info)
            # response = self.es.transport.perform_request("GET", "/_security/_authenticate")
            # print("Authenticated user info:", response)
        # except Exception as e:
        #     print("Error:", e)
    # Define a restricted role
    def create_role(self, un):
        response = self.es.indices.create(index=f"{un}-logs", ignore=400)
        role_body = {
            "indices": [
                {
                    "names": [f"{un}-logs*"],  # Limit access to indices matching this pattern
                    "privileges": ["read","write", "view_index_metadata"],          # Allow only read privileges
                    # "query": "{\"term\": {\"user_id\": \""+un+"\"}}"  # Optional: Apply a document-level security query
                }
            ]
        }
        self.es.security.put_role(name=f"{un}_project_role", body=role_body)
        print(f"Role created: {un}_project_role")

    # Create a user and assign the restricted role
    def create_user(self,un,pw):
        user_body = {
            "password": pw,        # User password
            "roles": [f"{un}_project_role"],    # Assign the restricted role
            "full_name": un,
            # "email": "user@example.com"
        }
        self.es.security.put_user(username=un, body=user_body)
        print(f"User created: {un}")

    # Create an API key with restricted access
    def create_api_key(self,un):
        api_key_body = {
            "name": f"{un}-api-key",
            "role_descriptors": {
                f"{un}_project_role": {
                    "indices": [
                        {
                            "names": [f"{un}-index-*"],
                            "privileges": ["read", "write"],
                            "query": "{\"term\": {\"status\": \"active\"}}"
                        }
                    ]
                }
            }
        }
        response = self.es.security.create_api_key(body=api_key_body)
        print("API Key created:", response)
        return response["api_key"]

    def registerUser(self,un,pw):
        self.create_role(un)
        self.create_user(un,pw)
        # api_key = self.create_api_key()
        # headers = {
        #     "Authorization": f"ApiKey {api_key}",
        #     "Content-Type": "application/json"
        # }

        # Make a GET request to search the index
    def loginUser(self, un, pw):
        try:
            self.es.options(http_auth=(un, pw))
            resp = self.es.search(index=f"{un}-logs*",)
            print("Search response:", resp)
            return 1
        except Exception as e:
            print("Access error:", e)

    def set_kibana_url(self, un):
        pass
