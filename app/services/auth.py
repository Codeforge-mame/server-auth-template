from app.repo.auth import AuthRepository
from app.schames.auth import UserCreate, UserLogin, UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.dependancies.security import Security
from app.services.redis import RedisCacheService

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AuthRepository(db)
        self.security = Security()
        self.redis_cache = RedisCacheService()

    async def create_users(self, user: UserCreate) -> UserResponse:
        existing_user = await self.repo.get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        db_user = {
            "username": user.username,
            "email": user.email,
            "password": self.security.hash_password(user.password)
        }

        return await self.repo.create_user(db_user)

    async def login(self, user: UserLogin) -> dict:
        existing_user = await self.repo.get_user_by_email(user.email)
        if not existing_user:
            raise HTTPException(status_code=400, detail="User not found")
        if not self.security.verify_password(user.password, existing_user.password):
            raise HTTPException(status_code=400, detail="Invalid password")

        ## create tokens
        access_token = self.security.create_access_token(data={"sub": str(existing_user.id)})
        refresh_token = self.security.create_refresh_token(data={"sub": str(existing_user.id)})

        ## store refresh token in redis
        await self.redis_cache.set_object(f"refresh_token:{existing_user.id}", refresh_token, 60 * 60 * 60 * 24 * 7)  # 7 days expiration
        
        ## return tokens
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    async def refresh_token(self, token: str) -> dict:
        if not token:
            raise HTTPException(status_code=401, detail=f"Not Authenticated")
        payload = self.security.verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail=f"Not Authenticated")

        ## redis recicle refresh token logic
        ## first check if the token is in redis
        cached_token = await self.redis_cache.get_object(f"refresh_token:{user_id}")
        if not cached_token or cached_token != token:
            raise HTTPException(status_code=401, detail=f"Not Authenticated")

        ## invalidate the token in redis
        await self.redis_cache.invalidate(f"refresh_token:{user_id}")

        ## generate new tokens
        access_token = self.security.create_access_token({"sub": user_id})
        ref_token = self.security.create_refresh_token({"sub": user_id})

        ## store the new refresh token in redis
        await self.redis_cache.set_object(f"refresh_token:{user_id}", ref_token, 60 * 60 * 24 * 7)  # 7 days expiration

        ## return tokens to set new cookies
        return {
            "access_token": access_token,
            "refresh_token": ref_token
        }
 
    async def logout(self, token: str) -> dict:
        if not token:
            raise HTTPException(status_code=401, detail=f"Not Authenticated")
        payload = self.security.verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail=f"Not Authenticated")

        ## invalidate the token in redis
        await self.redis_cache.invalidate(f"refresh_token:{user_id}")

        return {
            "msg": "User successfully logged out"
        }