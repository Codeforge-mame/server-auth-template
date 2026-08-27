from pydantic import BaseModel, ConfigDict, EmailStr
import uuid


class UserLogin(BaseModel):
    email: EmailStr
    password: str   


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    is_active: bool
    role: str

    model_config = ConfigDict(from_attributes=True)