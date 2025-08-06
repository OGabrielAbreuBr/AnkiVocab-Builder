# app/services/audio_generator.py
import os
from gtts import gTTS
import pandas as pd
from core.config import settings
from utils.helpers import sanitize_filename

# A função interna agora recebe o lang_code
def gerar_audio_texto(texto: str, nome_arquivo: str, lang_code: str) -> str:
    """
    Gera mp3 via gTTS em media_dir/nome_arquivo.
    Retorna o nome do arquivo (basename) ou "" se texto vazio.
    """
    if pd.isnull(texto) or not str(texto).strip():
        return ""
    path = os.path.join(settings.media_dir, nome_arquivo)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Usa o lang_code recebido, com 'en' como fallback seguro.
    tts = gTTS(text=str(texto).strip(), lang=lang_code or 'en')
    tts.save(path)
    return nome_arquivo

# As funções públicas agora aceitam e passam o lang_code
def gerar_audio_palavra(palavra: str, lang_code: str) -> str:
    base = sanitize_filename(palavra.replace(" ", "_").lower())
    return gerar_audio_texto(palavra, f"{base}.mp3", lang_code)

def gerar_audio_meaning(palavra: str, meaning: str, lang_code: str) -> str:
    base = sanitize_filename(palavra.replace(" ", "_").lower())
    return gerar_audio_texto(meaning, f"{base}_meaning.mp3", lang_code)

def gerar_audio_example(palavra: str, example: str, lang_code: str) -> str:
    base = sanitize_filename(palavra.replace(" ", "_").lower())
    return gerar_audio_texto(example, f"{base}_example.mp3", lang_code)
