# app/schemas/word.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List

# Importe os novos schemas que acabámos de criar
from .audio import AudioOut
from .image import ImageOut

class WordOut(BaseModel):
    id: int
    text: str
    meaning: str
    example: Optional[str] = None
    phonetic: Optional[str] = None
    cefr: Optional[str] = None
    
    # Lista pois cada palavra possui 3 audios
    audio: List[AudioOut] = [] 
    image: Optional[ImageOut] = None

    model_config = ConfigDict(from_attributes=True)

