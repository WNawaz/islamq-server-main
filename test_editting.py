import requests

url = "http://localhost:4000/updateContentTitle"

payload = {
    "id": 123,
    "editedTitle": "New Title",
    "language": "english"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())
