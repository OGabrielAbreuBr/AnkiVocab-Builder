# app/services/phonetics_service.py
import eng_to_ipa as ipa

def transcribe_phonetics(word: str) -> str:
    """
    Gera a transcrição fonética (IPA) para uma palavra em inglês.
    Não interage com a base de dados.
    """
    try:
        # A biblioteca pode devolver múltiplas transcrições, pegamos na primeira.
        phonetic = ipa.convert(str(word))
        return phonetic.strip()
    except Exception:
        # Retorna vazio se a conversão falhar
        return ""