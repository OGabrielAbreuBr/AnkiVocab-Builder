from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from db.session import SessionLocal
from core.config import settings
from core import security
from db import crud, models

# Este objeto aponta para a URL de login. Ele é usado para extrair o token.
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/token"
)

# Schema para validar o conteúdo (payload) do token
class TokenPayload(BaseModel):
    sub: int | None = None

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

# --- get_current_user ---
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> models.User:
    """
    Dependência para obter o usuário atual a partir de um token JWT.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodifica o token JWT usando a chave secreta
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        # Valida o payload usando o schema Pydantic
        token_data = TokenPayload(**payload)
    except JWTError:
        raise credentials_exception
    
    # Busca o usuário no banco de dados com o ID do token
    user = await crud.get_user_by_id(db, user_id=token_data.sub)
    if not user:
        raise credentials_exception
        
    return user