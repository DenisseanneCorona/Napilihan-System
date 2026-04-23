# NAgCO Loan Management System (Napilihan)

## Quick Start
```
cd "c:/Users/grace/Documents/NAPILIHAN SYSTEM"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit with Gmail creds
python start_server.py
```
- Backend API: http://127.0.0.1:5000/api
- Frontend: http://localhost:8080/pages/login.html
- Admin: admin / admin123

## Features
- Member signup (admin approval)
- Loans (APL/MPL/EHL/EPL)
- Admin dashboard, reports, payments
- Email OTP 2FA
- SQLite DB (users.db)

## Architecture
- Backend/app.py: Flask API (/api/*)
- Frontend/: Static HTML/JS
- start_server.py: Launches both

See TODO.md for completion status.

