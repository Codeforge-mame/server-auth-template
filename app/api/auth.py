from fastapi import APIRouter, Depends, Request, Response
from app.services.auth import AuthService
from app.schames.auth import UserCreate, UserLogin, UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_async_db
from app.dependancies.get_current_user import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    service = AuthService(db)
    return await service.create_users(user)

@router.post("/login", response_model=dict)
async def login(user: UserLogin, db: AsyncSession = Depends(get_async_db), response: Response = None):
    service = AuthService(db)
    tokens = await service.login(user)

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7  # 7 days
    )

    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=900
    )

    return {
        "msg": "User successfuly logged in"
    }

@router.post("/logout", response_model=dict)
async def logout(response: Response, request: Request, db: AsyncSession = Depends(get_async_db)):
    try:
        service = AuthService(db)
        token = request.cookies.get("refresh_token")

        response.delete_cookie(key="refresh_token")
        response.delete_cookie(key="access_token")
    
        return await service.logout(token)
    except Exception as e:
        return {
            "msg": f"Error logging out: {str(e)}"
        }

@router.post("/refresh", response_model=dict)
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_async_db)):
    refres_token = request.cookies.get("refresh_token")
    service = AuthService(db)
    tokens = await service.refresh_token(refres_token)

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7  # 7 days
    )

    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=900
    )

    return {
        "msg": "User refershed successfuly"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: UserResponse = Depends(get_current_user)):
    return current_user
