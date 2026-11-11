from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="user", cascade="all, delete")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(64), primary_key=True)   # your existing document_id
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    filename = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="documents")
    messages = relationship("ChatMessage", back_populates="document", cascade="all, delete")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    document_id = Column(String(64), ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role = Column(String(20), nullable=False)    # "user" or "assistant"
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)        # [{"page": 3}, ...]
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="messages")