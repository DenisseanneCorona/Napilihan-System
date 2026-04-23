import sqlite3
import bcrypt
import os
import smtplib
from dotenv import load_dotenv
load_dotenv()
from email.message import EmailMessage
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

class LoginSystem:
    def __init__(self, db_name="users.db"):
        self.db_name = db_name
        self.pending_otp = {}
        self.init_db()

    def generate_login_challenge(self, username, fullname, role, otp_code):
        challenge_id = os.urandom(24).hex()
        self.pending_otp[challenge_id] = {
            "username": username,
            "fullname": fullname,
            "role": role,
            "otp_code": otp_code,
            "expires_at": int(datetime.now().timestamp()) + 300,
        }
        return challenge_id

    def generate_email_otp(self):
        return f"{int.from_bytes(os.urandom(3), 'big') % 1000000:06d}"

    def send_email_otp(self, recipient, otp_code):
        mail_server = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
        mail_port = int(os.environ.get("MAIL_PORT", "587"))
        mail_use_tls = (os.environ.get("MAIL_USE_TLS", "true").lower() != "false")
        mail_username = os.environ.get("MAIL_USERNAME")
        mail_password = os.environ.get("MAIL_PASSWORD")
        mail_sender = os.environ.get("MAIL_SENDER") or mail_username

        if not mail_username or not mail_password or not mail_sender:
            return False, "Email OTP is not fully configured. Set MAIL_USERNAME, MAIL_PASSWORD, and MAIL_SENDER."

        message = EmailMessage()
        message["Subject"] = "NAgCO Login OTP"
        message["From"] = mail_sender
        message["To"] = recipient
        message.set_content(
            f"Your NAgCO login verification code is {otp_code}. It expires in 5 minutes."
        )

        with smtplib.SMTP(mail_server, mail_port, timeout=20) as server:
            if mail_use_tls:
                server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(message)
        return True, "OTP sent."

    def send_approval_email(self, recipient, fullname):
        mail_server = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
        mail_port = int(os.environ.get("MAIL_PORT", "587"))
        mail_use_tls = (os.environ.get("MAIL_USE_TLS", "true").lower() != "false")
        mail_username = os.environ.get("MAIL_USERNAME")
        mail_password = os.environ.get("MAIL_PASSWORD")
        mail_sender = os.environ.get("MAIL_SENDER") or mail_username

        if not mail_username or not mail_password or not mail_sender:
            return False, "Email not configured."

        message = EmailMessage()
        message["Subject"] = "NAgCO Account Approved!"
        message["From"] = mail_sender
        message["To"] = recipient
        message.set_content(
            f"Dear {fullname},\n\n"
            f"Congratulations! Your NAgCO (Napilihan Agriculture Cooperative) membership account has been approved.\n\n"
            f"You can now log in to the system at http://localhost:8080/pages/login.html\n"
            f"Use your username and password to access your member dashboard.\n\n"
            f"Welcome to the cooperative!\n\n"
            f"Best regards,\nNAgCO Management"
        )

        try:
            with smtplib.SMTP(mail_server, mail_port, timeout=20) as server:
                if mail_use_tls:
                    server.starttls()
                server.login(mail_username, mail_password)
                server.send_message(message)
            return True, "Approval email sent."
        except Exception as e:
            print(f"Failed to send approval email to {recipient}: {e}")
            return False, str(e)

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_username TEXT NOT NULL,
                loan_type TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                months INTEGER NOT NULL,
                date_created TEXT NOT NULL,
                due_date TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monthly_collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT UNIQUE NOT NULL,
                total_collection REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'Completed',
                date_created TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loan_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                loan_name TEXT NOT NULL,
                max_amount REAL NOT NULL,
                interest_rate REAL NOT NULL,
                service_fee_rate REAL NOT NULL,
                term_months INTEGER NOT NULL,
                penalty_rate REAL NOT NULL,
                cbu REAL NOT NULL DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                loan_id INTEGER NOT NULL,
                amount_paid REAL NOT NULL,
                payment_date TEXT NOT NULL,
                FOREIGN KEY (loan_id) REFERENCES loans(id)
            )
        ''')
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [row[1] for row in cursor.fetchall()]
        if "fullname" not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN fullname TEXT")
        if "status" not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN status TEXT NOT NULL DEFAULT 'approved'")
        if "role" not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'member'")
        if "two_factor_enabled" not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN two_factor_enabled INTEGER NOT NULL DEFAULT 0")
        if "two_factor_secret" not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN two_factor_secret TEXT")
        if "email" not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
        cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
        if not cursor.fetchone():
            password_hash = bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, fullname, email, status, role, two_factor_enabled, two_factor_secret)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                ("admin", password_hash, "System Administrator", "admin@example.com", "approved", "admin", 1, None),
            )
        else:
            cursor.execute(
                """
                UPDATE users
                SET role = 'admin',
                    two_factor_enabled = 1,
                    email = 'admin@example.com'
                WHERE username = 'admin'
                """,
            )
        cursor.execute("SELECT COUNT(*) FROM loan_types")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                """
                INSERT INTO loan_types
                (code, loan_name, max_amount, interest_rate, service_fee_rate, term_months, penalty_rate, cbu)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    ("APL", "Agricultural Production Loan", 5000, 0.02, 0.02, 4, 0.03, 100),
                    ("MPL", "Multi-Purpose Loan", 4000, 0.02, 0.02, 4, 0.03, 100),
                    ("EHL", "Emergency Health Loan", 5000, 0.02, 0.02, 2, 0.03, 0),
                    ("EPL", "Emergency Personal Loan", 3000, 0.02, 0.02, 2, 0.03, 0),
                ],
            )
        conn.commit()
        conn.close()

    def sign_up(self, username, password, fullname="", email=""):
        valid, msg = self.validate_input(username, password)
        if not valid:
            return False, msg
        if self.username_exists(username):
            status = self.get_user_status(username)
            if status == "pending":
                return False, "Account already registered and waiting for admin approval."
            if status == "approved":
                return False, "Account already registered. Please log in."
            return False, "Username already exists."
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, fullname, email, status, role)
                VALUES (?, ?, ?, ?, 'pending', 'member')
                """,
                (username, password_hash.decode('utf-8'), fullname, email),
            )
            conn.commit()
            conn.close()
            return True, "Registration submitted. Wait for admin approval."
        except Exception as e:
            return False, f"Error: {str(e)}"

    def login(self, username, password):
        valid, msg = self.validate_input(username, password)
        if not valid:
            return False, msg
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT password_hash, fullname, status, role, email, username
            FROM users
            WHERE username = ? OR email = ?
            """,
            (username, username),
        )
        result = cursor.fetchone()
        conn.close()
        if not result:
            return False, "User not found."
        if result[2] != "approved":
            return False, "Wait for admin approval."
        try:
            password_hash = result[0].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), password_hash):
                db_username = result[5]
                fullname = result[1] or db_username
                role = result[3] or "member"
                email = result[4]
                if not email:
                    return False, "Email address required for OTP verification. Please contact admin to update your profile."
                try:
                    otp_code = self.generate_email_otp()
                    sent, send_message = self.send_email_otp(email, otp_code)
                    if not sent:
                        print(f"OTP send failed for {email}: {send_message}. Skipping OTP.")
                        return True, {
                            "message": "Login successful (OTP skipped due to config).",
                            "username": db_username,
                            "fullname": fullname,
                            "status": result[2],
                            "role": role,
                            "requires_otp": False,
                        }
                except Exception as e:
                    print(f"Email error: {e}")
                    return True, {
                        "message": "Login successful (email config issue).",
                        "username": db_username,
                        "fullname": fullname,
                        "status": result[2],
                        "role": role,
                        "requires_otp": False,
                    }
                challenge_id = self.generate_login_challenge(db_username, fullname, role, otp_code)
                return True, {
                    "message": "Email OTP required.",
                    "username": db_username,
                    "fullname": fullname,
                    "status": result[2],
                    "role": role,
                    "requires_otp": True,
                    "challenge_id": challenge_id,
                }
            else:
                return False, "Incorrect password."
        except Exception as e:
            return False, f"Error: {str(e)}"

    def verify_login_challenge(self, challenge_id, code):
        challenge = self.pending_otp.get((challenge_id or "").strip())
        if not challenge:
            return False, "Invalid or expired verification request."
        if int(datetime.now().timestamp()) > challenge["expires_at"]:
            self.pending_otp.pop(challenge_id, None)
            return False, "Verification request expired. Please log in again."
        if (code or "").strip() != challenge["otp_code"]:
            return False, "Invalid OTP code."
        self.pending_otp.pop(challenge_id, None)
        return True, {
            "message": "Login successful.",
            "username": challenge["username"],
            "fullname": challenge["fullname"],
            "role": challenge["role"],
        }

    def list_users(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, username, COALESCE(fullname, username) AS fullname, email, status, role
            FROM users
            ORDER BY id DESC
            """
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_user_status(self, username, status):
        if status not in ("approved", "pending"):
            return False, "Invalid status."
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT email, fullname FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return False, "User not found."
        email, fullname = user
        cursor.execute("UPDATE users SET status = ? WHERE username = ?", (status, username))
        conn.commit()
        changed = cursor.rowcount
        conn.close()
        if changed == 0:
            return False, "User not found."
        # Send approval email if status is approved
        if status == "approved" and email:
            self.send_approval_email(email, fullname or username)
        return True, "User status updated."

    def update_user_role(self, username, role):
        if role not in ("admin", "member"):
            return False, "Invalid role."
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET role = ? WHERE username = ?", (role, username))
        conn.commit()
        changed = cursor.rowcount
        conn.close()
        if changed == 0:
            return False, "User not found."
        return True, "Role updated."

    def delete_user_by_username(self, username):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        changed = cursor.rowcount
        conn.close()
        if changed == 0:
            return False, "User not found."
        return True, "User deleted."

    def username_exists(self, username):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def get_user_status(self, username):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return row[0]

    def validate_input(self, username, password):
        if not username or not password:
            return False, "Username and password are required."
        if len(username) < 3:
            return False, "Username must be at least 3 characters."
        if len(username) > 50:
            return False, "Username must not exceed 50 characters."
        if len(password) < 6:
            return False, "Password must be at least 6 characters."
        return True, "Input valid."

    def change_password(self, username, old_password, new_password):
        if not self.validate_input(username, new_password):
            return False, "Invalid new password."
        success, msg = self.login(username, old_password)
        if not success:
            return False, "Current password incorrect."
        try:
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?",
                           (password_hash.decode('utf-8'), username))
            conn.commit()
            conn.close()
            return True, "Password changed successfully."
        except Exception as e:
            return False, f"Error: {str(e)}"

    def delete_account(self, username, password):
        success, msg = self.login(username, password)
        if not success:
            return False, "Incorrect password."
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            return True, "Account deleted."
        except Exception as e:
            return False, f"Error: {str(e)}"

    def create_loan(self, member_username, loan_type, amount, months, date_created):
        member_username = (member_username or "").strip().lower()
        loan_type = (loan_type or "").strip().upper()
        loan_type_data = self.get_loan_type(loan_type)
        if not member_username or not loan_type or amount <= 0:
            return False, "Invalid loan data."
        if not loan_type_data:
            return False, "Invalid loan type."
        if amount > float(loan_type_data["max_amount"]):
            return False, f"Maximum amount for {loan_type} is {loan_type_data['max_amount']}."
        months = int(loan_type_data["term_months"])
        if not date_created:
            date_created = datetime.now().strftime("%Y-%m-%d")
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO loans (member_username, loan_type, amount, status, months, date_created)
                VALUES (?, ?, ?, 'Pending', ?, ?)
                """,
                (member_username, loan_type, amount, months, date_created),
            )
            conn.commit()
            loan_id = cursor.lastrowid
            conn.close()
            return True, loan_id
        except Exception as e:
            return False, f"Error: {str(e)}"

    def list_loans(self, member_username=None):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if member_username:
            cursor.execute(
                """
                SELECT id, member_username, loan_type, amount, status, months, date_created, due_date
                FROM loans
                WHERE member_username = ?
                ORDER BY id DESC
                """,
                (member_username,),
            )
        else:
            cursor.execute(
                """
                SELECT id, member_username, loan_type, amount, status, months, date_created, due_date
                FROM loans
                ORDER BY id DESC
                """
            )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def list_loan_types(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT code, loan_name, max_amount, interest_rate, service_fee_rate, term_months, penalty_rate, cbu
            FROM loan_types
            ORDER BY id ASC
            """
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_loan_type(self, code):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT code, loan_name, max_amount, interest_rate, service_fee_rate, term_months, penalty_rate, cbu
            FROM loan_types
            WHERE code = ?
            """,
            ((code or "").strip().upper(),),
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_loan_status(self, loan_id, status, due_date=None):
        if status not in ("Approved", "Rejected"):
            return False, "Invalid status."
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, status FROM loans WHERE id = ?", (loan_id,))
        existing = cursor.fetchone()
        if not existing:
            conn.close()
            return False, "Loan not found."
        if existing["status"] != "Pending":
            conn.close()
            return False, "Only pending loan requests can be updated."
        if status == "Rejected":
            due_date = None
        cursor.execute(
            "UPDATE loans SET status = ?, due_date = ? WHERE id = ?",
            (status, due_date, loan_id),
        )
        conn.commit()
        conn.close()
        return True, "Loan updated."

    def upsert_monthly_collection(self, month, total_collection, status, date_created):
        month = (month or "").strip()
        status = (status or "").strip()
        if not month or total_collection is None:
            return False, "Invalid monthly collection data."
        try:
            total_collection = float(total_collection)
        except Exception:
            return False, "Invalid total collection value."
        if total_collection < 0:
            return False, "Total collection must be non-negative."

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO monthly_collections (month, total_collection, status, date_created)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(month) DO UPDATE SET
                total_collection = excluded.total_collection,
                status = excluded.status,
                date_created = excluded.date_created
            """,
            (month, total_collection, status, date_created),
        )
        conn.commit()
        conn.close()
        return True, "Monthly collection saved."

    def list_monthly_collections(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT month, total_collection, status, date_created
            FROM monthly_collections
            ORDER BY id DESC
            """
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def create_announcement(self, title, content):
        title = (title or "").strip()
        content = (content or "").strip()
        if not title or not content:
            return False, "Title and content are required."
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO announcements (title, content, created_at) VALUES (?, ?, ?)",
            (title, content, created_at),
        )
        conn.commit()
        conn.close()
        return True, "Announcement posted."

    def list_announcements(self, limit=None):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = """
            SELECT id, title, content, created_at
            FROM announcements
            ORDER BY id DESC
        """
        params = ()
        if limit:
            query += " LIMIT ?"
            params = (int(limit),)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def create_payment(self, loan_id, amount_paid, payment_date=None):
        if not loan_id or amount_paid is None:
            return False, "Loan and amount are required."
        try:
            amount_paid = float(amount_paid)
        except Exception:
            return False, "Invalid payment amount."
        if amount_paid <= 0:
            return False, "Payment amount must be greater than zero."
        payment_date = (payment_date or "").strip() or datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, status
            FROM loans
            WHERE id = ?
            """,
            (loan_id,),
        )
        loan = cursor.fetchone()
        if not loan:
            conn.close()
            return False, "Loan not found."
        if loan["status"] != "Approved":
            conn.close()
            return False, "Only approved loans can receive payments."
        cursor.execute(
            "INSERT INTO payments (loan_id, amount_paid, payment_date) VALUES (?, ?, ?)",
            (loan_id, amount_paid, payment_date),
        )
        conn.commit()
        conn.close()
        return True, "Payment recorded."

    def list_payments(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                payments.id,
                payments.loan_id,
                payments.amount_paid,
                payments.payment_date,
                loans.member_username,
                loans.loan_type
            FROM payments
            JOIN loans ON loans.id = payments.loan_id
            ORDER BY payments.id DESC
            """
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def summarize_payments_by_month(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                substr(payment_date, 1, 7) AS month,
                ROUND(SUM(amount_paid), 2) AS total_collection,
                COUNT(*) AS payment_count
            FROM payments
            GROUP BY substr(payment_date, 1, 7)
            ORDER BY month DESC
            """
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]


app = Flask(__name__)
CORS(app)
system = LoginSystem()


@app.post("/api/signup")
def api_signup():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip().lower()
    fullname = (data.get("fullname") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    success, msg = system.sign_up(username, password, fullname, email)
    if success:
        return jsonify({"success": True, "message": msg}), 201
    return jsonify({"success": False, "message": msg}), 400


@app.post("/api/login")
def api_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip().lower()
    password = data.get("password") or ""
    success, payload = system.login(username, password)
    if success:
        return jsonify({
            "success": True,
            "message": payload["message"],
            "username": username,
            "fullname": payload["fullname"],
            "role": payload["role"],
            "requires_otp": payload.get("requires_otp", False),
            "challenge_id": payload.get("challenge_id"),
        }), 200
    return jsonify({"success": False, "message": payload}), 401


@app.post("/api/login/verify-otp")
def api_login_verify_otp():
    data = request.get_json(silent=True) or {}
    challenge_id = (data.get("challenge_id") or "").strip()
    code = (data.get("code") or "").strip()
    success, payload = system.verify_login_challenge(challenge_id, code)
    if success:
        return jsonify({"success": True, **payload}), 200
    return jsonify({"success": False, "message": payload}), 401


@app.get("/api/users")
def api_list_users():
    users = system.list_users()
    return jsonify({"success": True, "users": users}), 200


@app.patch("/api/users/<username>")
def api_update_user(username):
    data = request.get_json(silent=True) or {}
    status = (data.get("status") or "").strip().lower()
    role = (data.get("role") or "").strip().lower()
    
    if role:
        # Update role
        conn = sqlite3.connect(system.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET role = ? WHERE username = ?", (role, username))
        conn.commit()
        changed = cursor.rowcount
        conn.close()
        if changed == 0:
            return jsonify({"success": False, "message": "User not found."}), 404
        return jsonify({"success": True, "message": "Role updated."}), 200
    
    if status:
        success, msg = system.update_user_status(username, status)
        if success:
            return jsonify({"success": True, "message": msg}), 200
        return jsonify({"success": False, "message": msg}), 400
    
    return jsonify({"success": False, "message": "No update data provided."}), 400


@app.delete("/api/users/<username>")
def api_delete_user(username):
    success, msg = system.delete_user_by_username(username)
    if success:
        return jsonify({"success": True, "message": msg}), 200
    return jsonify({"success": False, "message": msg}), 404


@app.post("/api/loans")
def api_create_loan():
    data = request.get_json(silent=True) or {}
    member_username = (data.get("member_username") or "").strip().lower()
    loan_type = (data.get("loan_type") or "").strip().upper()
    try:
        amount = float(data.get("amount") or 0)
        months = int(data.get("months") or 0)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Invalid loan data."}), 400
    date_created = (data.get("date_created") or "").strip()

    success, result = system.create_loan(member_username, loan_type, amount, months, date_created)
    if success:
        return jsonify({"success": True, "loan_id": result}), 201
    return jsonify({"success": False, "message": result}), 400


@app.get("/api/loans")
def api_list_loans():
    member_username = (request.args.get("member_username") or "").strip()
    loans = system.list_loans(member_username if member_username else None)
    return jsonify({"success": True, "loans": loans}), 200


@app.get("/api/loan-types")
def api_list_loan_types():
    loan_types = system.list_loan_types()
    return jsonify({"success": True, "loan_types": loan_types}), 200


@app.patch("/api/loans/<int:loan_id>")
def api_update_loan(loan_id):
    data = request.get_json(silent=True) or {}
    status = (data.get("status") or "").strip()
    due_date = (data.get("due_date") or None)
    success, msg = system.update_loan_status(loan_id, status, due_date)
    if success:
        return jsonify({"success": True, "message": msg}), 200
    return jsonify({"success": False, "message": msg}), 400


@app.post("/api/reports/monthly")
def api_upsert_monthly():
    data = request.get_json(silent=True) or {}
    month = (data.get("month") or "").strip()
    total_collection = data.get("total_collection")
    status = (data.get("status") or "Completed").strip()
    date_created = (data.get("date_created") or "").strip()
    if not date_created:
        date_created = datetime.now().strftime("%Y-%m-%d")

    success, msg = system.upsert_monthly_collection(month, total_collection, status, date_created)
    if success:
        return jsonify({"success": True, "message": msg}), 200
    return jsonify({"success": False, "message": msg}), 400


@app.get("/api/reports/monthly")
def api_list_monthly():
    rows = system.list_monthly_collections()
    return jsonify({"success": True, "collections": rows}), 200


@app.get("/api/payments")
def api_list_payments():
    payments = system.list_payments()
    return jsonify({"success": True, "payments": payments}), 200


@app.post("/api/payments")
def api_create_payment():
    data = request.get_json(silent=True) or {}
    try:
        loan_id = int(data.get("loan_id") or 0)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Invalid loan selected."}), 400
    amount_paid = data.get("amount_paid")
    payment_date = (data.get("payment_date") or "").strip()
    success, msg = system.create_payment(loan_id, amount_paid, payment_date)
    if success:
        return jsonify({"success": True, "message": msg}), 201
    return jsonify({"success": False, "message": msg}), 400


@app.get("/api/reports/payment-summary")
def api_payment_summary():
    rows = system.summarize_payments_by_month()
    return jsonify({"success": True, "summary": rows}), 200


@app.post("/api/announcements")
def api_create_announcement():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    success, msg = system.create_announcement(title, content)
    if success:
        return jsonify({"success": True, "message": msg}), 201
    return jsonify({"success": False, "message": msg}), 400


@app.get("/api/announcements")
def api_list_announcements():
    limit = request.args.get("limit")
    announcements = system.list_announcements(int(limit) if limit and limit.isdigit() else None)
    return jsonify({"success": True, "announcements": announcements}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
