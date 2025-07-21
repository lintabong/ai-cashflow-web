from app import db
from datetime import datetime
import uuid

class Wallet(db.Model):
    __tablename__ = 'wallets'
    
    id = db.Column(db.String(24), primary_key=True, default=lambda: str(uuid.uuid4()).replace('-', '')[:24])
    userId = db.Column(db.String(24), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    balance = db.Column(db.Numeric(15, 2), default=0.00)
    isActive = db.Column(db.Boolean, default=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cashflows = db.relationship('Cashflow', backref='wallet', lazy=True)
    
    def __repr__(self):
        return f'<Wallet {self.name}>'