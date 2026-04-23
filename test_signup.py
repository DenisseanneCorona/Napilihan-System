import requests
import json

# Test signup
response = requests.post('http://127.0.0.1:5000/api/signup', json={
    'username': 'testuser123',
    'password': 'test123456',
    'fullname': 'Test User',
    'email': 'testuser123@example.com'
})

data = response.json()
print('Signup response:', data)

# Check DB
import sqlite3
conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute("SELECT username, status FROM users WHERE username='testuser123'")
print('DB status:', cur.fetchone())
conn.close()
