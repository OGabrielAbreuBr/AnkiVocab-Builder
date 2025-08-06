# app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext

from core.config import settings

# Contexto para hashing de senhas, usando o algoritmo bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """
    Cria um token de acesso JWT.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Token expira em 15 minutos por padrão
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se uma senha em texto plano corresponde a uma senha criptografada.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Gera o hash de uma senha.
    """
    return pwd_context.hash(password)