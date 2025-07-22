from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from bot.services.database import Base 


class Chat(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chatId = Column(Integer, ForeignKey('intents.id'), nullable=False)
    role = Column(String(50), nullable=False)  # contoh: "user", "assistant"
    message = Column(Text, nullable=False)
    isValid = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=datetime.now)
