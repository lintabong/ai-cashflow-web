from sqlalchemy import Column, Integer, Text, Boolean, DateTime
from datetime import datetime
from bot.services.database import Base 

class Intent(Base):
    __tablename__ = 'intents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    isValid = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=datetime.now)
