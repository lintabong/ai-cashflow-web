from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, DateTime, Numeric, Enum, Boolean
)
from sqlalchemy.orm import relationship
from datetime import datetime
from bot.services.database import Base
import enum

class FlowType(enum.Enum):
    income = 'income'
    expense = 'expense'
    transfer = 'transfer'

class Cashflow(Base):
    __tablename__ = 'cashflow'
    
    id = Column(String(24), primary_key=True)
    userId = Column(String(24), ForeignKey('users.id'), nullable=False, index=True)
    walletId = Column(String(24), ForeignKey('wallets.id'), nullable=False, index=True)
    transactionDate = Column(DateTime, nullable=False)
    activityName = Column(String(255), nullable=False)
    description = Column(Text)
    categoryId = Column(Integer)
    quantity = Column(Numeric(15, 4), default=1.00)
    unit = Column(String(50), default='unit')
    flowType = Column(Enum(FlowType), nullable=False)
    isActive = Column(Boolean, default=True)
    price = Column(Numeric(15, 2), default=0.00)
    total = Column(Numeric(15, 2), default=0.00)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', back_populates='cashflows', lazy='selectin')
    wallet = relationship('Wallet', back_populates='cashflows', lazy='selectin')
