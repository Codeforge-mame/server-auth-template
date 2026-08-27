from app.models.user import User
from app.schames.auth import UserCreate, UserLogin, UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_email(self, email: str) -> UserResponse:
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_user(self, user: UserCreate)-> UserResponse:
        ## add user
        db_user = User(
            username=user["username"],
            email=user["email"],
            password=user["password"]
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user