from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
import uuid
from enum import Enum
from sqlalchemy import ForeignKey


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(Base):
    __tablename__ = "messages"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chats.id"), nullable=False)
    role: Mapped[MessageRole] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    
    chat = relationship("Chat", back_populates="messages")