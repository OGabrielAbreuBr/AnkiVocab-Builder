# app/api/endpoints/languages.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from api import deps
from db import crud
from schemas.language import LanguageOut

router = APIRouter(prefix="/languages", tags=["languages"])

@router.get("/", response_model=List[LanguageOut])
async def read_languages(db: AsyncSession = Depends(deps.get_db)):
    """
    Obtém uma lista de todos os idiomas disponíveis.
    """
    return await crud.get_languages(db)