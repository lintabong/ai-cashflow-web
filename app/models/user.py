from app import db
from flask_login import UserMixin
from datetime import datetime
import uuid

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(24), primary_key=True, default=lambda: str(uuid.uuid4()).replace('-', '')[:24])
    name = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text)
    username = db.Column(db.Text)
    email = db.Column(db.Text)
    phone = db.Column(db.Text)
    telegramId = db.Column(db.BigInteger, unique=True, nullable=False)
    balance = db.Column(db.Numeric(15, 2), default=0.00)
    isActive = db.Column(db.Boolean, default=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    lastLogin = db.Column(db.DateTime)
    
    # Relationships
    wallets = db.relationship('Wallet', backref='user', lazy=True)
    cashflows = db.relationship('Cashflow', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def check_password(self, password):
        # Simple password check - in production, use proper hashing
        return self.password == password
    
    def set_password(self, password):
        # Simple password setting - in production, use proper hashing
        self.password = password