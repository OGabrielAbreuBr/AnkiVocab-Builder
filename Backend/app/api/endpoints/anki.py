# app/api/endpoints/anki.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import anyio # Para apagar o ficheiro temporário

from api import deps
from db import crud, models
from services.anki_service import generate_anki_deck_from_db

router = APIRouter(prefix="/anki", tags=["anki"])

@router.get("/export/{deck_id}")
async def export_anki_deck(
    deck_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Gera e envia para download um ficheiro .apkg para um deck específico.
    """
    # 1. Vai buscar o deck à base de dados
    deck = await crud.get_deck_by_id(db, deck_id=deck_id)
    
    # 2. Garante que o deck existe e pertence ao utilizador logado
    if not deck or current_user not in deck.users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck não encontrado ou sem permissão"
        )

    # 3. Chama o serviço para gerar o ficheiro .apkg
    apkg_path = generate_anki_deck_from_db(deck_obj=deck)
    
    filename = f"{deck.name.replace(' ', '_')}.apkg"

    # 4. Usa StreamingResponse para enviar o ficheiro e depois apagá-lo
    async def file_iterator(path):
        async with await anyio.open_file(path, mode='rb') as f:
            while chunk := await f.read(1024 * 64):
                yield chunk
        # Apaga o ficheiro temporário depois de ser enviado
        await anyio.Path(path).unlink()

    return StreamingResponse(
        file_iterator(apkg_path),
        media_type="application/vnd.android.package-archive",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
