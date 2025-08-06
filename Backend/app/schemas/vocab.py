# app/schemas/vocab.py
from pydantic import BaseModel
from typing import Optional

class VocabOut(BaseModel):
    word: str
    meaning: str
    example: str
    cefr: str
    phonetic: Optional[str] = None
