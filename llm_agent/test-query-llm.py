import requests
import json

params = {"query": "What is the default batch size for map_batches?"}
response = requests.post("http://127.0.0.1:8000/query", params=params)
#print(response.json())
print(response.status_code)
print(response.content)
