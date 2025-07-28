from sqlalchemy import Column, Integer, Text, Boolean, DateTime, String
from datetime import datetime
from bot.services.database import Base

class Intent(Base):
    __tablename__ = 'intents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(String(24), nullable=False)
    chat = Column(Text, nullable=False)
    intent = Column(Text)
    response = Column(Text)
    inputToken = Column(Integer)
    outputToken = Column(Integer)
    isValid = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=datetime.now)
