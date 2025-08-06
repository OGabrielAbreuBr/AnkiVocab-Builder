# app/db/crud.py

from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.security import get_password_hash
from db.models import (
    User, Language, Word, Audio, Image,
    Deck, DeckWord, UserDeck
)
from schemas.user import UserCreate, UserUpdate
from schemas.decks import CardUpdate


# --- USERS ---

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Retorna um utilizador pelo seu ID, carregando as suas relações."""
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.decks),
            selectinload(User.languages)
        )
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Retorna um utilizador pelo seu email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Retorna um utilizador pelo seu nome de utilizador."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Cria um novo utilizador na base de dados."""
    if await get_user_by_email(db, user_in.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado")
    if await get_user_by_username(db, user_in.username):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Username já em uso")

    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_user(db: AsyncSession, user: User, user_in: UserUpdate) -> User:
    """Atualiza os dados de um utilizador."""
    user_data = user_in.model_dump(exclude_unset=True)
    for field, value in user_data.items():
        setattr(user, field, value)
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# --- LANGUAGES ---

async def get_languages(db: AsyncSession) -> List[Language]:
    """Retorna uma lista de todos os idiomas disponíveis."""
    result = await db.execute(select(Language).order_by(Language.name))
    return result.scalars().all()


# --- WORDS ---

async def get_word_by_text(
    db: AsyncSession,
    text: str,
    language_id: int
) -> Optional[Word]:
    """Retorna a instância Word se existir na base de dados, ou None."""
    stmt = select(Word).where(Word.text == text, Word.language_id == language_id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_or_create_word(
    db: AsyncSession,
    text: str,
    meaning: str,
    example: str,
    cefr: str,
    phonetic: str,
    language_id: int
) -> Word:
    """Busca uma palavra pelo texto. Se não existir, cria um novo registo."""
    word = await get_word_by_text(db, text, language_id)
    if word:
        updated = False
        if not word.meaning and meaning:
            word.meaning = meaning
            updated = True
        if not word.example and example:
            word.example = example
            updated = True
        if not word.cefr and cefr:
            word.cefr = cefr
            updated = True
        if not word.phonetic and phonetic:
            word.phonetic = phonetic
            updated = True
        if updated:
            await db.commit()
            await db.refresh(word)
        return word

    new_word = Word(
        text=text,
        meaning=meaning,
        example=example,
        cefr=cefr,
        phonetic=phonetic,
        language_id=language_id
    )
    db.add(new_word)
    await db.commit()
    await db.refresh(new_word)
    return new_word

async def update_word(db: AsyncSession, word_id: int, card_in: CardUpdate) -> Optional[Word]:
    """Atualiza o significado e o exemplo de uma palavra."""
    word = await db.get(Word, word_id)
    if not word:
        return None
    
    if card_in.meaning is not None:
        word.meaning = card_in.meaning
    if card_in.example is not None:
        word.example = card_in.example
    
    await db.commit()
    await db.refresh(word)
    return word


# --- AUDIO & IMAGE ---

async def create_or_update_audio(
    db: AsyncSession,
    word_id: int,
    path: str,
    audio_type: str, # 'word', 'meaning', ou 'example'
    format: str = "mp3",
    duration: Optional[float] = None
) -> Audio:
    """Cria ou atualiza um registo de áudio específico para uma palavra."""
    # Procura por um áudio existente com base no word_id e no audio_type
    stmt = select(Audio).where(Audio.word_id == word_id, Audio.audio_type == audio_type)
    result = await db.execute(stmt)
    audio = result.scalars().first()
    
    if audio:
        # Atualiza o registo se ele já existir
        audio.path = path
        audio.format = format
        audio.duration_secs = duration
    else:
        # Cria um novo registo se não existir
        audio = Audio(
            word_id=word_id,
            audio_type=audio_type,
            path=path,
            format=format,
            duration_secs=duration
        )
    
    db.add(audio)
    await db.commit()
    await db.refresh(audio)
    return audio

async def create_or_update_image(
    db: AsyncSession,
    word_id: int,
    path: str,
    image_type: str,
    format: str = "jpeg",
    creator: Optional[str] = None
) -> Image:
    """Cria ou atualiza o registo de imagem para uma palavra."""
    image = await db.get(Image, word_id)
    if image:
        image.path, image.image_type, image.format, image.creator = path, image_type, format, creator
    else:
        image = Image(word_id=word_id, path=path, image_type=image_type, format=format, creator=creator)
    
    db.add(image)
    await db.commit()
    await db.refresh(image)
    return image

# --- DECKS ---

async def create_deck(
    db: AsyncSession,
    user_id: int,
    name: str,
    word_lang_id: int,
    expl_lang_id: int,
    is_public: bool = False
) -> Deck:
    """Cria um novo deck."""
    deck = Deck(
        name=name,
        is_public=is_public,
        language_word_id=word_lang_id,
        language_explanation_id=expl_lang_id
    )
    db.add(deck)
    await db.flush()
    db.add(UserDeck(user_id=user_id, deck_id=deck.id))
    await db.commit()
    await db.refresh(deck, attribute_names=["deck_words", "users", "word_language", "explanation_language"])
    return deck

async def get_decks_by_user(db: AsyncSession, user_id: int) -> List[Deck]:
    """Retorna uma lista de todos os decks pertencentes a um utilizador."""
    stmt = (
        select(Deck)
        .join(UserDeck)
        .where(UserDeck.user_id == user_id)
        .options(
            selectinload(Deck.users),
            selectinload(Deck.word_language),
            selectinload(Deck.explanation_language),
            selectinload(Deck.deck_words).selectinload(DeckWord.word).selectinload(Word.audio),
            selectinload(Deck.deck_words).selectinload(DeckWord.word).selectinload(Word.image)
        )
    )
    result = await db.execute(stmt)
    return result.scalars().unique().all()


async def get_deck_by_id(db: AsyncSession, deck_id: int) -> Optional[Deck]:
    """Retorna um deck específico pelo seu ID."""
    stmt = (
        select(Deck)
        .where(Deck.id == deck_id)
        .options(
            selectinload(Deck.users),
            selectinload(Deck.word_language),
            selectinload(Deck.explanation_language),
            selectinload(Deck.deck_words).selectinload(DeckWord.word).selectinload(Word.audio),
            selectinload(Deck.deck_words).selectinload(DeckWord.word).selectinload(Word.image)
        )
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def delete_deck(db: AsyncSession, deck: Deck) -> None:
    """Apaga um deck."""
    await db.delete(deck)
    await db.commit()


async def add_card_to_deck(
    db: AsyncSession,
    deck_id: int,
    word_id: int
) -> DeckWord:
    """Adiciona um novo card (DeckWord) a um deck existente."""
    card = DeckWord(
        deck_id=deck_id,
        word_id=word_id,
    )
    db.add(card)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta palavra já existe neste deck."
        )
    
    stmt = (
        select(DeckWord)
        .where(DeckWord.id == card.id)
        .options(
            selectinload(DeckWord.word).selectinload(Word.audio),
            selectinload(DeckWord.word).selectinload(Word.image)
        )
    )
    result = await db.execute(stmt)
    return result.scalars().one()


async def delete_card_from_deck(db: AsyncSession, card_id: int) -> int:
    """Apaga um card pelo seu ID."""
    card = await db.get(DeckWord, card_id)
    if card:
        await db.delete(card)
        await db.commit()
        return 1
    return 0
