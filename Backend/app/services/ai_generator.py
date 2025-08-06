# services/ai_generator.py

from clients.gemini_client import GeminiClient

def gerar_meaning_example(palavra: str) -> tuple[str,str]:
    return GeminiClient.get_meaning_and_example(palavra)

def gerar_cefr(palavra: str) -> str:
    return GeminiClient.get_cefr_level(palavra)
