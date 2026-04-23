#!/usr/bin/env python3
"""
Email OTP Setup Script
This script helps configure the email settings for the OTP system.
"""

import os
import sys
from dotenv import load_dotenv

def create_env_file():
    """Create a .env file with email configuration template"""
    env_content = """# Email Configuration for OTP
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_SENDER=your-email@gmail.com

# Database Configuration (optional)
DB_NAME=users.db
"""
    
    env_file = ".env"
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"Created {env_file} file")
        print("Please edit the .env file with your email configuration:")
        print("- Set MAIL_USERNAME to your Gmail address")
        print("- Set MAIL_PASSWORD to your Gmail app password")
        print("- Set MAIL_SENDER to your Gmail address")
        print("\nTo get a Gmail app password:")
        print("1. Go to Google Account settings")
        print("2. Enable 2-Step Verification")
        print("3. Go to Security -> App passwords")
        print("4. Generate a new app password")
        return True
    else:
        print(f"{env_file} file already exists")
        return False

def test_email_config():
    """Test if email environment variables are set"""
    load_dotenv()
    required_vars = ['MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_SENDER']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var) or os.environ.get(var) == f"your-email@gmail.com" or os.environ.get(var) == "your-app-password":
            missing_vars.append(var)
    
    if missing_vars:
        print("Missing or unset environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        print("\nPlease set these environment variables or update the .env file")
        return False
    else:
        print("Email configuration is properly set")
        return True

def main():
    print("=== NAgCO Email OTP Setup ===")
    print()
    
    # Create .env file if it doesn't exist
    if create_env_file():
        print()
        print("After configuring the .env file, run this script again to test the configuration.")
        return
    
    # Test email configuration
    if test_email_config():
        print("\nEmail OTP is ready to use!")
        print("Restart the backend server to apply the changes.")
    else:
        print("\nPlease complete the email configuration before using OTP.")

if __name__ == "__main__":
    main()
