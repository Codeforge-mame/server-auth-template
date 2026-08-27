from app.dependancies.security import Security
from fastapi import Depends, HTTPException, status, Request, Depends
from app.repo.auth import AuthRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_async_db


async def get_current_user(request: Request, db: AsyncSession = Depends(get_async_db)):
    security = Security()
    token = request.cookies.get("access_token")

    payload = security.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    try:
        repo = AuthRepository(db)
        print(payload.get("sub"))
        user = await repo.get_user_by_id(payload.get("sub"))
        if not user:
            raise HTTPException(status_code=404, detail="user can't find")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"server error {str(e)}")

async def get_admin(db: AsyncSession = Depends(get_async_db)):
    payload = get_current_user()
    if not payload:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    user_id = payload.get("sub")
    try:
        repo = AuthRepository(db)
        user = await repo.get_user_by_id(user_id=user_id)
        if user.role != "admin":
            raise HTTPException(status_code=403, detail=f"Forbidden to this perssion")
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"authentication error {str(e)}")    
