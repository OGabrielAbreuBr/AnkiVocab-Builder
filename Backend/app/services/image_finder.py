from sqlalchemy.ext.asyncio import AsyncSession
from db.crud import get_image_src_by_word

async def encontrar_imagem(palavra: str, db: AsyncSession) -> str:
    """
    Consulta o banco e retorna o nome do arquivo de imagem
    associado a 'palavra', ou '' se não existir.
    """
    return await get_image_src_by_word(db, palavra)
