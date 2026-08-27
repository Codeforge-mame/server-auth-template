from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
import uuid
from enum import Enum


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[Role] = mapped_column(default=Role.USER)

    chats: Mapped[list["Chat"]] = relationship("Chat", back_populates="user", cascade="all, delete-orphan")