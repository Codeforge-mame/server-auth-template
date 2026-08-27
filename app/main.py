from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

## routes
from app.api import auth

## models
import app.models

app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Chatbot SaaS API"}

@app.get("/get-cookies")
def get_cookies(request: Request): # Crucial: Rename from 'req' to 'request'
    # Use standard dictionary extraction safely
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")

    # Pro-tip: Implement a quick sanity fallback validation if cookies are missing
    if not access_token or not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Authentication cookies are missing or expired"
        )

    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }   