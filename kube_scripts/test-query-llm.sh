URL='http://127.0.0.1:20091/query?query="What is the default batch size for map_batches?"'
#response = requests.post("http://127.0.0.1:20091/query", params=params)


# Set the query parameter
query="What is the default batch size for map_batches?"

# Make a POST request to the query endpoint
curl -X POST $URL \
-H "Content-Type: application/json" 


