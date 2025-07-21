from app import db
from datetime import datetime
import uuid

class Cashflow(db.Model):
    __tablename__ = 'cashflow'
    
    id = db.Column(db.String(24), primary_key=True, default=lambda: str(uuid.uuid4()).replace('-', '')[:24])
    userId = db.Column(db.String(24), db.ForeignKey('users.id'), nullable=False)
    walletId = db.Column(db.String(24), db.ForeignKey('wallets.id'), nullable=False)
    transactionDate = db.Column(db.DateTime, nullable=False)
    activityName = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    categoryId = db.Column(db.Integer)
    quantity = db.Column(db.Numeric(15, 4), default=1.00)
    unit = db.Column(db.String(50), default='unit')
    flowType = db.Column(db.Enum('income', 'expense', 'transfer', name='flow_type'), nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    price = db.Column(db.Numeric(15, 2), default=0.00)
    total = db.Column(db.Numeric(15, 2), default=0.00)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Cashflow {self.activityName}>'