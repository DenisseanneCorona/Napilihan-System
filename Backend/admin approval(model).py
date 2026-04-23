from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum

db = SQLAlchemy()

class UserStatus(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    status = db.Column(db.Enum(UserStatus), default=UserStatus.PENDING, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    
    # Admin notes for approval/rejection
    admin_notes = db.Column(db.Text)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_active(self):
        return self.status == UserStatus.ACTIVE
    
    def get_id(self):
        return str(self.id)#Sa model tong lahat na part ng code