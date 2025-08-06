# app/schemas/decks.py
from pydantic import BaseModel, ConfigDict, computed_field
from typing import List, Optional

# Importe os seus outros schemas necessários
from .word import WordOut
from .user import UserOut
from .language import LanguageOut

# UserDecks (M:N)

class UserInDeck(BaseModel):
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)

# --- Schemas de Deck ---

class DeckCreate(BaseModel):
    name: str
    word_language_id: int
    explanation_language_id: int
    is_public: bool = False

# Schemas de create Card
class CardCreate(BaseModel):
    word: str

# --- Schemas de Output ---

class CardOut(BaseModel):
    id: int
    deck_id: int
    word_id: int
    word: WordOut

    model_config = ConfigDict(from_attributes=True)

class DeckOut(BaseModel):
    id: int
    name: str
    is_public: bool
    word_language: LanguageOut
    explanation_language: LanguageOut
    users: List[UserInDeck] = []
    
    # Este é o atributo que vem do seu modelo SQLAlchemy
    deck_words: List[CardOut] = []

    # Criamos um campo 'cards' no JSON de saída que usa os dados de 'deck_words'.
    @computed_field
    @property
    def cards(self) -> List[CardOut]:
        return self.deck_words

    model_config = ConfigDict(from_attributes=True)

class CardUpdate(BaseModel):
    meaning: str | None = None
    example: str | None = None

