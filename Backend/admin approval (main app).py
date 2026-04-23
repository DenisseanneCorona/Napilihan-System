from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import re
from datetime import datetime
from models import db, User, UserStatus
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
mail = Mail(app)

# Create admin user on first run
def create_admin():
    with app.app_context():
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='johncarloaganan26@gmail.com',
                is_admin=True,
                status=UserStatus.ACTIVE
            )
            admin.set_password('admin123')  # Change this in production
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username=admin, password=admin123")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()
    create_admin()

# Validation functions
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    return True, ""

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        
        # Validation
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        if not validate_email(email):
            flash('Invalid email format', 'error')
            return render_template('register.html')
        
        is_valid, msg = validate_password(password)
        if not is_valid:
            flash(msg, 'error')
            return render_template('register.html')
        
        # Create pending user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Waiting for admin approval.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember_me = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if user.status != UserStatus.ACTIVE:
                flash('Account is not yet approved. Please wait for admin approval.', 'error')
                return render_template('login.html')
            
            login_user(user, remember=remember_me)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    return render_template('admin_dashboard.html')

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    pending_users = User.query.filter_by(status=UserStatus.PENDING)\
        .order_by(User.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    all_users = User.query.order_by(User.created_at.desc()).all()
    
    return render_template('admin_users.html', 
                         pending_users=pending_users, 
                         all_users=all_users)

@app.route('/admin/approve/<int:user_id>', methods=['POST'])
@login_required
def approve_user(user_id):
    if not current_user.is_admin:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    if user.status != UserStatus.PENDING:
        flash('User is not in pending status', 'error')
        return redirect(url_for('admin_users'))
    
    notes = request.form.get('notes', '')
    user.status = UserStatus.ACTIVE
    user.approved_at = datetime.utcnow()
    user.admin_notes = notes
    db.session.commit()
    
    # Send approval email
    send_approval_email(user)
    flash(f'User {user.username} approved successfully', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/reject/<int:user_id>', methods=['POST'])
@login_required
def reject_user(user_id):
    if not current_user.is_admin:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    if user.status != UserStatus.PENDING:
        flash('User is not in pending status', 'error')
        return redirect(url_for('admin_users'))
    
    notes = request.form.get('notes', '')
    user.status = UserStatus.REJECTED
    user.admin_notes = notes
    db.session.commit()
    
    # Send rejection email
    send_rejection_email(user)
    flash(f'User {user.username} rejected', 'success')
    return redirect(url_for('admin_users'))

def send_approval_email(user):
    msg = Message('Account Approved!',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.email])
    msg.body = f"""
    Hello {user.username},

    Your account has been approved! You can now log in to your account.

    Login: {url_for('login', _external=True)}
    Username: {user.username}

    Admin notes: {user.admin_notes or 'None'}

    Best regards,
    Admin Team
    """
    mail.send(msg)

def send_rejection_email(user):
    msg = Message('Account Registration Rejected',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.email])
    msg.body = f"""
    Hello {user.username},

    We regret to inform you that your account registration has been rejected.

    Reason: {user.admin_notes or 'Not specified'}

    You can register again with a different username/email if needed.

    Best regards,
    Admin Team
    """
    mail.send(msg)

if __name__ == '__main__':
    app.run(debug=True) #for main app