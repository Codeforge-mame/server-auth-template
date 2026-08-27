# app/models/__init__.py
from app.core.db import Base
from app.models.user import User

__all__ = ["Base", "User"]
