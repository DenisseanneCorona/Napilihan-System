import requests
import json

response = requests.post(
    "http://127.0.0.1:5000/api/signup",
    json={
        "username": "apiuser_test",
        "password": "test12345",
        "fullname": "API Test User",
        "email": "apitest@example.com"
    }
)
print(response.status_code)
print(response.json())
