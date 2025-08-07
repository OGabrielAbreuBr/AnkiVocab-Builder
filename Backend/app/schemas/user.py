# app/schemas/user.py
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List
from .language import LanguageOut

# Propriedades recebidas ao criar um novo usuário.
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str

# Propriedades retornadas pela API. Retirar senha pela segurança
class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: EmailStr

    languages: List[LanguageOut] = []

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None

class UserLanguagesUpdate(BaseModel):
    language_ids: List[int]

