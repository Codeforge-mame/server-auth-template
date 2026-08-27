from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
import uuid
from sqlalchemy import ForeignKey


class Chat(Base):
    __tablename__ = "chats"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)

    user = relationship("User", back_populates="chats")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="chat", cascade="all, delete-orphan")