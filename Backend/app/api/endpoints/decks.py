# app/api/endpoints/decks.py

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from api import deps
from db import crud, models
from schemas.decks import DeckCreate, CardCreate, DeckOut, CardOut, CardUpdate
from services.ai_generator import gerar_meaning_example, gerar_cefr
from services.phonetics_service import transcribe_phonetics
from services.audio_generator import (
    gerar_audio_palavra, 
    gerar_audio_meaning, 
    gerar_audio_example
)

router = APIRouter(prefix="/decks", tags=["decks"])


@router.post("/", response_model=DeckOut, status_code=status.HTTP_201_CREATED)
async def create_deck(
    payload: DeckCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """Cria um novo deck para o utilizador logado."""
    return await crud.create_deck(
        db=db,
        user_id=current_user.id,
        name=payload.name,
        word_lang_id=payload.word_language_id,
        expl_lang_id=payload.explanation_language_id,
        is_public=payload.is_public,
    )


@router.get("/", response_model=List[DeckOut])
async def get_all_decks_for_user(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """Lista todos os decks do utilizador logado."""
    return await crud.get_decks_by_user(db, user_id=current_user.id)


@router.get("/{deck_id}", response_model=DeckOut)
async def get_deck_details(
    deck_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """Retorna os detalhes de um deck específico."""
    deck = await crud.get_deck_by_id(db, deck_id=deck_id)
    if not deck or current_user not in deck.users:
        raise HTTPException(status_code=404, detail="Deck não encontrado ou sem permissão")
    return deck


@router.post("/{deck_id}/cards", response_model=CardOut, status_code=status.HTTP_201_CREATED)
async def add_card(
    deck_id: int,
    payload: CardCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Adiciona um novo card (palavra) a um deck existente de forma robusta.
    """
    # Validação do Deck e Permissão
    deck = await crud.get_deck_by_id(db, deck_id=deck_id)
    if not deck or current_user not in deck.users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Deck não encontrado ou sem permissão"
        )

    # Geração de Dados da Palavra, passando os nomes dos idiomas
    try:
        meaning, example = gerar_meaning_example(
            palavra=payload.word,
            word_language_name=deck.word_language.name,
            explanation_language_name=deck.explanation_language.name
        )
        cefr = gerar_cefr(
            palavra=payload.word,
            word_language_name=deck.word_language.name
        )
        phonetic = transcribe_phonetics(payload.word)
    except Exception as e:
        print(f"ERRO CRÍTICO ao gerar dados da IA para '{payload.word}': {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"O serviço de IA falhou ao processar a palavra. Tente novamente mais tarde."
        )

    if not meaning or not cefr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível gerar os dados essenciais (significado, CEFR) para a palavra."
        )

    # Salvar a Palavra Principal no Banco de Dados
    word_obj = await crud.get_or_create_word(
        db=db,
        text=payload.word,
        meaning=meaning,
        example=example,
        cefr=cefr,
        phonetic=phonetic,
        language_id=deck.language_word_id
    )

    # Geração e Salvamento de Mídia
    audio_word_file = gerar_audio_palavra(payload.word, lang_code=deck.word_language.code)
    audio_meaning_file = gerar_audio_meaning(payload.word, meaning, lang_code=deck.explanation_language.code)
    audio_example_file = gerar_audio_example(payload.word, example, lang_code=deck.word_language.code)
    
    if audio_word_file:
        await crud.create_or_update_audio(db, word_id=word_obj.id, path=audio_word_file, audio_type='word')
    if audio_meaning_file:
        await crud.create_or_update_audio(db, word_id=word_obj.id, path=audio_meaning_file, audio_type='meaning')
    if audio_example_file:
        await crud.create_or_update_audio(db, word_id=word_obj.id, path=audio_example_file, audio_type='example')

    # Ligar a Palavra ao Deck
    return await crud.add_card_to_deck(
        db=db,
        deck_id=deck.id,
        word_id=word_obj.id,
    )


@router.put("/{deck_id}/cards/{card_id}", response_model=CardOut)
async def update_card_in_deck(
    deck_id: int,
    card_id: int,
    card_in: CardUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Atualiza o significado ou exemplo de uma palavra num card e regenera os áudios.
    """
    # 1. Validação para garantir que o utilizador é dono do deck
    deck = await crud.get_deck_by_id(db, deck_id=deck_id)
    if not deck or current_user not in deck.users:
        raise HTTPException(status_code=404, detail="Deck não encontrado")

    card = await db.get(models.DeckWord, card_id)
    if not card or card.deck_id != deck_id:
        raise HTTPException(status_code=404, detail="Card não encontrado neste deck")

    # 2. Atualiza o texto (meaning e example) na tabela 'words'
    updated_word = await crud.update_word(db, word_id=card.word_id, card_in=card_in)
    
    # --- CORREÇÃO PRINCIPAL AQUI ---
    # 3. Regenera os ficheiros de áudio com o novo texto
    if card_in.meaning:
        audio_meaning_file = gerar_audio_meaning(
            palavra=updated_word.text, 
            meaning=card_in.meaning, 
            lang_code=deck.explanation_language.code
        )
        # 4. Salva o novo caminho na tabela 'audio'
        await crud.create_or_update_audio(
            db, word_id=updated_word.id, path=audio_meaning_file, audio_type='meaning'
        )

    if card_in.example:
        audio_example_file = gerar_audio_example(
            palavra=updated_word.text, 
            example=card_in.example, 
            lang_code=deck.word_language.code
        )
        await crud.create_or_update_audio(
            db, word_id=updated_word.id, path=audio_example_file, audio_type='example'
        )
    # --- FIM DA CORREÇÃO ---

    # 5. Recarrega o card para devolver a resposta completa e atualizada
    await db.refresh(card, attribute_names=['word'])
    return card


@router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deck(
    deck_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """Apaga um deck do utilizador logado."""
    deck = await crud.get_deck_by_id(db, deck_id=deck_id)
    if not deck or current_user not in deck.users:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Deck não encontrado")
    
    await crud.delete_deck(db, deck=deck)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{deck_id}/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card_from_deck(
    deck_id: int,
    card_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """Remove um card de um deck."""
    deck = await crud.get_deck_by_id(db, deck_id=deck_id)
    if not deck or current_user not in deck.users:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Deck não encontrado")

    deleted_count = await crud.delete_card_from_deck(db, card_id=card_id)
    if deleted_count == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Card não encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
