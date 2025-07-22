from sqlalchemy import Column, String, Text, ForeignKey, Numeric, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from bot.services.database import Base

class Wallet(Base):
    __tablename__ = 'wallets'

    id = Column(String(24), primary_key=True)
    userId = Column(String(24), ForeignKey('users.id'), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    balance = Column(Numeric(15, 2), default=0.00)
    isActive = Column(Boolean, default=True)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', back_populates='wallets', lazy='selectin')
    cashflows = relationship('Cashflow', back_populates='wallet', lazy='selectin')
