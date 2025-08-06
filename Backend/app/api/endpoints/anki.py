# app/api/endpoints/anki.py

from fastapi import APIRouter
from fastapi.responses import FileResponse
from services.anki_service import generate_anki_deck_from_csv
from core.config import settings

router = APIRouter(prefix="/anki", tags=["anki"])

@router.get("/export")
def export_anki():
    """
    Gera e envia para download um arquivo .apkg via FileResponse.
    """
    apkg_path = generate_anki_deck_from_csv(
        csv_path=settings.anki_csv_path,
        media_dir=settings.anki_media_dir,
        deck_name=settings.anki_deck_name,
        deck_id=settings.anki_deck_id,
        model_id=settings.anki_model_id,
    )
    return FileResponse(
        path=apkg_path,
        filename=f"{settings.anki_deck_name}.apkg",
        media_type="application/vnd.android.package-archive",
    )
