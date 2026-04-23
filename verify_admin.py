import sqlite3
conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute("SELECT username, email, role FROM users WHERE email='johncarloaganan26@gmail.com'")
print(cur.fetchone())
conn.close()
