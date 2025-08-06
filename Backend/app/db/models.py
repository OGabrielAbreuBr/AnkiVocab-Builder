# app/db/models.py
from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    ForeignKey, func, CHAR, Boolean, REAL,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from db.base import Base

class User(Base):
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, index=True)
    first_name      = Column(String(100), nullable=False)
    last_name       = Column(String(255), nullable=False)
    username        = Column(String(255), unique=True, nullable=False)
    email           = Column(String(255), unique=True, nullable=False)
    hashed_password = Column("password_hash", String(255), nullable=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at      = Column(DateTime(timezone=True),
                             server_default=func.now(),
                             onupdate=func.now(),
                             nullable=False)

    # Relação com a tabela de junção (a "fonte da verdade" para escrita)
    user_decks      = relationship("UserDeck",    back_populates="user",     cascade="all, delete-orphan")
    user_languages  = relationship("UserLanguage",back_populates="user",     cascade="all, delete-orphan")

    # Relações de conveniência, apenas para leitura (viewonly=True)
    decks           = relationship("Deck",        secondary="user_decks",    back_populates="users", viewonly=True)
    languages       = relationship("Language",    secondary="user_languages",back_populates="users", viewonly=True)


class Language(Base):
    __tablename__ = "languages"
    id              = Column(Integer, primary_key=True)
    code            = Column(String(10), unique=True, nullable=False)
    name            = Column(String(50), nullable=False)

    user_languages  = relationship("UserLanguage", back_populates="language", cascade="all, delete-orphan")
    users           = relationship("User",         secondary="user_languages", back_populates="languages", viewonly=True)

    decks_word      = relationship("Deck", foreign_keys="[Deck.language_word_id]",        back_populates="word_language")
    decks_expl      = relationship("Deck", foreign_keys="[Deck.language_explanation_id]", back_populates="explanation_language")
    words           = relationship("Word", back_populates="language", cascade="all, delete-orphan")


class UserDeck(Base):
    __tablename__ = "user_decks"
    user_id  = Column(Integer, ForeignKey("users.id",   ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    deck_id  = Column(Integer, ForeignKey("decks.id",   ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)

    user     = relationship("User", back_populates="user_decks")
    deck     = relationship("Deck", back_populates="deck_users")


class UserLanguage(Base):
    __tablename__ = "user_languages"
    user_id     = Column(Integer, ForeignKey("users.id",      ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    language_id = Column(Integer, ForeignKey("languages.id",  ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)

    user        = relationship("User",     back_populates="user_languages")
    language    = relationship("Language", back_populates="user_languages")


class Deck(Base):
    __tablename__ = "decks"
    id                       = Column(Integer, primary_key=True, index=True)
    name                     = Column(String(255), nullable=False)
    is_public                = Column(Boolean,      nullable=False, server_default="false")
    created_at               = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at               = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    language_word_id         = Column(Integer, ForeignKey("languages.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    language_explanation_id  = Column(Integer, ForeignKey("languages.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)

    # existem duas relações para facilitar ir de deck para usuario, se não tivesse eu teria que passar por UserDecks anes de chegar no user
    deck_users   = relationship("UserDeck", back_populates="deck", cascade="all, delete-orphan")
    users        = relationship("User",     secondary="user_decks", back_populates="decks", viewonly=True) 
    
    word_language        = relationship("Language", foreign_keys=[language_word_id],        back_populates="decks_word")
    explanation_language = relationship("Language", foreign_keys=[language_explanation_id], back_populates="decks_expl")

    deck_words   = relationship("DeckWord", back_populates="deck", cascade="all, delete-orphan")


class Word(Base):
    __tablename__ = "words"
    id            = Column(Integer, primary_key=True, index=True)
    text          = Column(String(100), nullable=False)
    meaning       = Column(Text,         nullable=False)
    example       = Column(Text)
    cefr          = Column(CHAR(2),      nullable=False)
    phonetic      = Column(String(50))
    language_id   = Column(Integer, ForeignKey("languages.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at    = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # relações
    language      = relationship("Language", back_populates="words")
    deck_words    = relationship("DeckWord", back_populates="word", cascade="all, delete-orphan")

    audio         = relationship("Audio",    back_populates="word", cascade="all, delete-orphan")
    image         = relationship("Image",    back_populates="word", uselist=False, cascade="all, delete-orphan")


class DeckWord(Base):
    __tablename__ = "deck_words"
    id            = Column(Integer, primary_key=True, index=True)
    deck_id       = Column(Integer, ForeignKey("decks.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    word_id       = Column(Integer, ForeignKey("words.id", ondelete="CASCADE",  onupdate="CASCADE"), nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at    = Column(DateTime(timezone=True),
                           server_default=func.now(),
                           onupdate=func.now(),
                           nullable=False)

    deck          = relationship("Deck", back_populates="deck_words")
    word          = relationship("Word", back_populates="deck_words")
    
    # Unique constraint mantém a unicidade de words em um deck
    __table_args__ = (UniqueConstraint('deck_id', 'word_id', name='_deck_word_uc'),)

class Audio(Base):
    __tablename__ = "audio"
    id            = Column(Integer, primary_key=True, index=True)
    word_id       = Column(Integer, ForeignKey("words.id", ondelete="CASCADE"), nullable=False)
    audio_type    = Column(String(20), nullable=False) # ex: 'word', 'meaning', 'example'

    format        = Column(String(10), nullable=False)
    path          = Column(String(255), nullable=False)
    duration_secs = Column(REAL)

    created_at    = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at    = Column(DateTime(timezone=True),
                           server_default=func.now(),
                           onupdate=func.now(),
                           nullable=False)

    word          = relationship("Word", back_populates="audio")

    __table_args__ = (UniqueConstraint('word_id', 'audio_type', name='_word_audio_type_uc'),)

class Image(Base):
    __tablename__ = "images"
    word_id       = Column(Integer, ForeignKey("words.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)

    image_type    = Column(String(50), nullable=False) # GenAI, User
    path          = Column(String(255), nullable=False)
    format        = Column(String(10), nullable=False)
    creator       = Column(String(255))

    created_at    = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at    = Column(DateTime(timezone=True),
                           server_default=func.now(),
                           onupdate=func.now(),
                           nullable=False)

    word          = relationship("Word", back_populates="image")

