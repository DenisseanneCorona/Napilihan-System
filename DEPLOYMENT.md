# NAPILIHAN SYSTEM - Deployment Guide

## System Requirements

### Backend Requirements
- Python 3.8 or higher
- pip package manager
- SQLite (comes with Python)

### Frontend Requirements
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Web server (Apache, Nginx, or Python's built-in server)

## Installation Steps

### 1. Backend Setup

#### 1.1 Install Python Dependencies
```bash
cd "c:/xampp/htdocs/NAPILIHAN SYSTEM"
pip install -r requirements.txt
```

#### 1.2 Configure Email Settings
```bash
# Copy the example environment file
copy .env.example .env

# Edit .env file with your email settings
notepad .env
```

Edit the `.env` file:
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_SENDER=your-email@gmail.com
DB_NAME=users.db
```

#### 1.3 Run Email Setup Script
```bash
python setup_email.py
```

#### 1.4 Start Backend Server
```bash
cd Backend
python "login & signup.py"
```

The backend will run on `http://127.0.0.1:5000`

### 2. Frontend Setup

#### 2.1 Using XAMPP (Recommended for Windows)
1. Start XAMPP Control Panel
2. Start Apache server
3. Access via: `http://localhost/NAPILIHAN%20SYSTEM/Frontend/pages/login.html`

#### 2.2 Using Python's Built-in Server
```bash
cd Frontend
python -m http.server 8080
```
Access via: `http://localhost:8080/pages/login.html`

#### 2.3 Using Node.js (if available)
```bash
cd Frontend
npx serve -s . -p 8080
```

## Production Deployment

### Option 1: XAMPP Deployment (Windows)

1. **Install XAMPP**
   - Download from https://www.apachefriends.org/
   - Install with default settings

2. **Copy Files**
   - Copy entire `NAPILIHAN SYSTEM` folder to `c:/xampp/htdocs/`

3. **Configure Apache**
   - Start Apache from XAMPP Control Panel
   - Access: `http://localhost/NAPILIHAN%20SYSTEM/Frontend/pages/login.html`

4. **Run Backend**
   - Open Command Prompt
   - Navigate to backend folder
   - Run: `python "login & signup.py"`

### Option 2: Linux Server Deployment

1. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip sqlite3 nginx
   ```

2. **Setup Application**
   ```bash
   sudo mkdir /var/www/napilihan
   sudo cp -r NAPILIHAN\ SYSTEM/* /var/www/napilihan/
   sudo chown -R www-data:www-data /var/www/napilihan
   ```

3. **Install Python Dependencies**
   ```bash
   cd /var/www/napilihan
   pip3 install -r requirements.txt
   ```

4. **Configure Nginx**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           root /var/www/napilihan/Frontend;
           index login.html;
       }
       
       location /api {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **Setup Systemd Service**
   ```bash
   sudo nano /etc/systemd/system/napilihan.service
   ```

   ```ini
   [Unit]
   Description=NAPILIHAN System Backend
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/napilihan/Backend
   ExecStart=/usr/bin/python3 "login & signup.py"
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   sudo systemctl enable napilihan
   sudo systemctl start napilihan
   ```

## Configuration

### Email Configuration
1. Enable 2-Step Verification on your Gmail account
2. Generate App Password:
   - Go to Google Account Settings
   - Security → 2-Step Verification → App passwords
   - Generate new app password
3. Use app password in `MAIL_PASSWORD` field

### Database Configuration
- Default database: `users.db` (SQLite)
- Location: Backend folder
- Auto-creates tables on first run

### Admin Access
- Username: `admin`
- Password: `admin123`
- Email: `admin@example.com` (change this in production)

## Security Considerations

1. **Change Default Credentials**
   - Update admin password
   - Configure proper email for admin

2. **Environment Variables**
   - Never commit `.env` file to version control
   - Use strong passwords for email

3. **HTTPS in Production**
   - Configure SSL certificates
   - Update API base URL in frontend

4. **Database Security**
   - Set proper file permissions
   - Regular backups

## Troubleshooting

### Common Issues

1. **Email OTP Not Working**
   - Check email configuration in `.env`
   - Verify Gmail app password
   - Check firewall settings

2. **CORS Errors**
   - Ensure backend is running
   - Check API base URL in frontend

3. **Database Issues**
   - Check file permissions
   - Ensure SQLite is installed

4. **Port Conflicts**
   - Change backend port if 5000 is occupied
   - Update frontend API URL accordingly

### Logs
- Backend logs: Console output
- Frontend logs: Browser Developer Tools (F12)

## Maintenance

1. **Regular Updates**
   - Update Python packages
   - Monitor security advisories

2. **Backups**
   - Backup database regularly
   - Backup configuration files

3. **Monitoring**
   - Monitor server resources
   - Check email deliverability

## Support

For issues:
1. Check logs
2. Verify configuration
3. Test with default settings
4. Contact system administrator
