#!/usr/bin/env python3
# Windows: Just use `python start_server.py`
"""
NAPILIHAN SYSTEM - Fixed Server Startup Script
"""

import os
import sys
import subprocess
import time
import signal

def signal_handler(sig, frame):
    print('\nShutting down servers...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print("=== NAPILIHAN SYSTEM (Fixed) ===")
print("Backend: http://127.0.0.1:5000")
print("Frontend: http://localhost:8080")
print()

# Start backend (non-blocking)
print("Starting backend...")
backend = subprocess.Popen([sys.executable, "Backend/app.py"])
time.sleep(3)
print(f"Backend PID: {backend.pid}")

# Start frontend (non-blocking)
print("Starting frontend...")
frontend = subprocess.Popen([sys.executable, "-m", "http.server", "8080", "-d", "Frontend"])
print(f"Frontend PID: {frontend.pid}")

print("\nBoth servers running! Press Ctrl+C to stop.")
print("Login: http://localhost:8080/pages/login.html (admin/admin123)")
print("Admin Email: johncarloaganan26@gmail.com")

try:
    backend.wait()
except KeyboardInterrupt:
    frontend.terminate()
    backend.terminate()
    print("\n👋 Servers stopped.")
