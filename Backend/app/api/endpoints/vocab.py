# app/api/endpoints/vocab.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db
from db import crud
from services.ai_generator import gerar_meaning_example, gerar_cefr
from services.phonetics_service import transcribe_phonetics
from schemas.vocab import VocabOut

router = APIRouter(prefix="/vocabulary", tags=["vocabulary"])


@router.get("/{word}", response_model=VocabOut)
async def read_vocabulary(
    word: str,
    language_id: int = Query(..., description="ID do idioma para esta palavra"),
    db: AsyncSession = Depends(get_db),
):
    """
    Gera meaning/example/cefr/phonetic, persiste em `words` e retorna tudo.
    """
    try:
        meaning, example = gerar_meaning_example(word)
        cefr = gerar_cefr(word)
        
        phonetic = transcribe_phonetics(word)

        # persiste com todos os campos obrigatórios
        await crud.get_or_create_word(
            db=db,
            text=word,
            meaning=meaning,
            example=example,
            cefr=cefr,
            phonetic=phonetic,
            language_id=language_id,
        )

        return VocabOut(
            word=word,
            meaning=meaning,
            example=example,
            cefr=cefr,
            phonetic=phonetic,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
