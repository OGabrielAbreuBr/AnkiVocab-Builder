# app/db/seed.py
import asyncio
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import SessionLocal, engine, Base
from db.models import Language

# Lista de idiomas que queremos garantir que existam
INITIAL_LANGUAGES = [
    {'code': 'en', 'name': 'Inglês'},
    {'code': 'pt', 'name': 'Português'},
    {'code': 'es', 'name': 'Espanhol'},
    # {'code': 'fr', 'name': 'Francês'},
    # {'code': 'de', 'name': 'Alemão'},
    # {'code': 'it', 'name': 'Italiano'},
    # {'code': 'jp', 'name': 'Japonês'},
]

async def seed_languages(db: AsyncSession):
    print("A verificar e a semear idiomas...")
    for lang_data in INITIAL_LANGUAGES:
        # Verifica se o idioma já existe pelo código
        result = await db.execute(select(Language).filter_by(code=lang_data['code']))
        existing_language = result.scalars().first()

        if not existing_language:
            # Se não existir, cria
            print(f"A criar idioma: {lang_data['name']}")
            db_lang = Language(code=lang_data['code'], name=lang_data['name'])
            db.add(db_lang)
        else:
            print(f"Idioma '{lang_data['name']}' já existe.")
    
    await db.commit()
    print("Semeação de idiomas concluída.")

async def main():
    print("A inicializar a base de dados para a semeação...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        await seed_languages(session)

if __name__ == "__main__":
    asyncio.run(main())