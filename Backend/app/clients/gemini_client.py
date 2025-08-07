# app/clients/gemini_client.py

import time
import re
from typing import Tuple

from google import genai
from google.genai.types import HttpOptions
from google.api_core.exceptions import ResourceExhausted

from core.config import settings

client = genai.Client(
    http_options=HttpOptions(api_version="v1"),
    api_key=settings.gemini_api_key or "",
)
MODEL = settings.gemini_model_name

class GeminiClient:
    @staticmethod
    def get_meaning_and_example(
        word: str,
        word_language_name: str,      # <-- NOVO PARÂMETRO
        explanation_language_name: str, # <-- NOVO PARÂMETRO
        retries: int = 3,
        delay: int = 60
    ) -> Tuple[str, str]:
        if not settings.gemini_api_key:
            return "", ""
        
        # O prompt agora usa os nomes dos idiomas dinamicamente
        prompt = f"""
You are helping me create vocabulary cards for Anki. For each input word I provide, return the output in exactly two lines:
A simple, clear definition of the word in {explanation_language_name}.
A natural example sentence using the word in context, in its original language ({word_language_name}).

Make sure the output is always in this exact structure—definition on the first line, and example sentence on the second—no extra lines, no extra explanation.

Input word ({word_language_name}): {word}
"""
        for attempt in range(1, retries + 1):
            try:
                resp = client.models.generate_content(
                    model=MODEL,
                    contents=prompt,
                )
                lines = resp.text.strip().splitlines()
                meaning = lines[0].strip() if lines else ""
                example = lines[1].strip() if len(lines) > 1 else ""
                return meaning, example
            except ResourceExhausted:
                if attempt < retries:
                    time.sleep(delay)
                else:
                    raise
        return "", ""

    @staticmethod
    def get_cefr_level(
        word: str,
        word_language_name: str, # <-- NOVO PARÂMETRO
        retries: int = 3,
        delay: int = 60
    ) -> str:
        if not settings.gemini_api_key:
            return ""
        
        # O prompt agora usa o nome do idioma dinamicamente
        prompt = (
            f"What is the CEFR level for the {word_language_name} word '{word}'? "
            f"Respond with only the level (e.g., A1, A2, B2, C1)."
        )
        for attempt in range(1, retries + 1):
            try:
                resp = client.models.generate_content(
                    model=MODEL,
                    contents=prompt,
                )
                response_text = resp.text.strip().upper()
            
                match = re.search(r"\b([A-C][1-2])\b", response_text)
                
                if match:
                    return match.group(1)
                else:
                    print(f"AVISO: Não foi possível extrair o CEFR da resposta para '{word}': {response_text}")
                    return ""
                    
            except ResourceExhausted:
                if attempt < retries:
                    time.sleep(delay)
                else:
                    raise
        return ""
