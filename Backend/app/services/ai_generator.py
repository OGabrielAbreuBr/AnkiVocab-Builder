# app/services/ai_generator.py

from clients.gemini_client import GeminiClient

def gerar_meaning_example(
    palavra: str, 
    word_language_name: str, 
    explanation_language_name: str
) -> tuple[str,str]:
    """
    Delega a geração de significado e exemplo para o cliente Gemini,
    passando os nomes dos idiomas.
    """
    return GeminiClient.get_meaning_and_example(
        word=palavra,
        word_language_name=word_language_name,
        explanation_language_name=explanation_language_name
    )

def gerar_cefr(palavra: str, word_language_name: str) -> str:
    """
    Delega a geração do nível CEFR para o cliente Gemini,
    passando o nome do idioma da palavra.
    """
    return GeminiClient.get_cefr_level(
        word=palavra,
        word_language_name=word_language_name
    )
