import sqlite3
conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute("SELECT username, email, status, role FROM users ORDER BY id DESC")
print("{:<20} {:<35} {:<10} {:<10}".format("Username", "Email", "Status", "Role"))
print("-" * 80)
for row in cur.fetchall():
    print("{:<20} {:<35} {:<10} {:<10}".format(*row))
conn.close()
