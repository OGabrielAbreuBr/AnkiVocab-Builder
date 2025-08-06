# app/api/endpoints/login.py

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps
from core.security import create_access_token, verify_password
from db import crud
from schemas.token import Token 

router = APIRouter(tags=["login"])

# Tempo de expiração do token de acesso
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/token", response_model=Token)
async def login_for_access_token(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Autentica o usuário e retorna um token de acesso.
    """
    user = await crud.get_user_by_email(db, email=form_data.username) # FastAPI usa 'username' para o email/login
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}