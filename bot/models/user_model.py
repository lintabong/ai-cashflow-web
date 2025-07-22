from sqlalchemy import Column, String, Text, BigInteger, Numeric, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from bot.services.database import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String(24), primary_key=True)
    name = Column(Text, nullable=False)
    password = Column(Text)
    username = Column(Text, index=True)
    email = Column(Text, index=True)
    phone = Column(Text)
    telegramId = Column(BigInteger, unique=True, index=True, nullable=False)
    balance = Column(Numeric(15, 2), default=0.00)
    isActive = Column(Boolean, default=True, index=True)
    createdAt = Column(DateTime, default=datetime.utcnow)
    lastLogin = Column(DateTime, nullable=True)

    wallets = relationship('Wallet', back_populates='user', lazy='selectin')
    cashflows = relationship('Cashflow', back_populates='user', lazy='selectin')
