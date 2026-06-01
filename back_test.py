import requests

# 1. Define the API endpoint URL
api_url = "http://localhost:8000/"

# 2. Create the data payload (must match your FastAPI Pydantic model)
payload = {
    "voltage": 3.3
}

# 3. Send the POST request
requests.get(api_url+"sva/3.3")
response = requests.get(api_url+"rva")

# 4. Check the result
if response.status_code == 200:
    print("Success:", response.json())
else:
    print("Error:", response.text)