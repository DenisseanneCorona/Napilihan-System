import sqlite3
conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute("SELECT username, email, status, role FROM users")
rows = cur.fetchall()
for row in rows:
    print(row)
conn.close()
