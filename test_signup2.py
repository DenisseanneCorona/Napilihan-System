import urllib.request
import json
import urllib.parse

url = "http://127.0.0.1:5000/api/signup"
data = {
    "username": "apiuser_test2",
    "password": "test12345",
    "fullname": "API Test User 2",
    "email": "apitest2@example.com"
}
headers = {"Content-Type": "application/json"}
req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        print(result)
except Exception as e:
    print(f"Error: {e}")
