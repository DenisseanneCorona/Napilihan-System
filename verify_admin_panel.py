import urllib.request
import json

# Create a new user
print("Creating new user...")
data = json.dumps({
    "username": "freshuser123",
    "password": "test12345",
    "fullname": "Fresh User",
    "email": "fresh@example.com"
}).encode()
req = urllib.request.Request(
    "http://127.0.0.1:5000/api/signup",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST"
)
with urllib.request.urlopen(req) as r:
    print("Signup:", json.loads(r.read().decode()))

# Fetch users list
print("\nFetching users list...")
with urllib.request.urlopen("http://127.0.0.1:5000/api/users") as r:
    result = json.loads(r.read().decode())
    for u in result.get("users", []):
        print(f"{u['username']:20} | {u['status']}")
