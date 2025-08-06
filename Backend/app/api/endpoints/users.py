# app/api/endpoints/users.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps
from db import crud, models
from schemas.user import UserCreate, UserOut, UserUpdate
from db.models import User

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_new_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Cria um novo usuário.
    """
    new_user = await crud.create_user(db, user_in=user_in)

    return new_user

@router.get("/me", response_model=UserOut)
async def read_users_me(
    current_user: User = Depends(deps.get_current_user)
):
    """
    Retorna os dados do usuário logado.
    """
    return current_user

@router.put("/me", response_model=UserOut)
async def update_user_me(
    user_in: UserUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """Atualiza o perfil do utilizador logado."""
    return await crud.update_user(db, user=current_user, user_in=user_in)