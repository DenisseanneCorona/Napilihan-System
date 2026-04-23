import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Check if user exists
cursor.execute("SELECT username, role FROM users WHERE email = ?", ('johncarloaganan26@gmail.com',))
result = cursor.fetchone()

if result:
    username, current_role = result
    print(f"Found user: {username}, current role: {current_role}")
    cursor.execute("UPDATE users SET role = 'admin' WHERE email = ?", ('johncarloaganan26@gmail.com',))
    conn.commit()
    print("Role updated to 'admin'")
else:
    print("User with that email not found.")
    # Optionally create user?
    # cursor.execute("INSERT INTO users (username, password_hash, fullname, email, role) VALUES (?, ?, ?, ?, ?)",
    #                ('johncarlo', bcrypt.hashpw('temp123'.encode(), bcrypt.gensalt()).decode(), 'John Carlo', 'johncarloaganan26@gmail.com', 'admin'))
    # conn.commit()
    # print("Created new admin user: johncarlo / temp123")

conn.close()
