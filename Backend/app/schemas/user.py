# app/schemas/user.py
from pydantic import BaseModel, EmailStr, ConfigDict

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

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None

