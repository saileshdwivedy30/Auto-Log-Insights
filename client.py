import os
import requests
import jsonpickle

hostname = "localhost"
port = "5000"
domain = f"{hostname}:{port}"
endpoint = "apiv1/generate-insight"
url = f'http://{domain}/{endpoint}'

log_dir = "logs"

for file in os.listdir(log_dir):
    files = {'file': open(os.path.join(log_dir,file), 'rb')}
    response = requests.post(url, files=files)
    message = jsonpickle.decode(response.text)
    if True:
        # decode response
        print("Response is", response)
        print(message)