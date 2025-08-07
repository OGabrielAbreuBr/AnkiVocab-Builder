# app/services/anki_service.py
import os
import genanki
from tempfile import NamedTemporaryFile
from pathlib import Path

from core.config import settings
from db.models import Deck, Word, Audio, Image

def generate_anki_deck_from_db(deck_obj: Deck) -> str:
    """
    Gera um ficheiro .apkg a partir de um objeto Deck da base de dados e
    retorna o caminho para o ficheiro temporário gerado.
    """
    # Cria o deck e o modelo do Anki
    anki_deck = genanki.Deck(
        deck_id=deck_obj.id + 1_000_000, # Adiciona um offset para evitar conflitos com IDs existentes
        name=deck_obj.name
    )
    
    anki_css = """
    .card {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-size: 22px;
        text-align: center;
        color: #2d3748; /* cinza-800 */
        background-color: #f9fafb; /* cinza-50 */
        padding: 20px;
        border-radius: 12px;
    }
    h1 {
        font-size: 48px;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .phonetic {
        font-size: 20px;
        color: #718096; /* cinza-500 */
        margin-bottom: 20px;
    }
    hr#answer {
        border-top: 1px solid #e2e8f0; /* cinza-200 */
    }
    .meaning, .example {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        margin-top: 10px;
    }
    .meaning {
        font-weight: 600;
    }
    .example {
        font-style: italic;
        color: #4a5568; /* cinza-700 */
    }
    .cefr {
        font-size: 14px;
        font-weight: bold;
        color: #ffffff;
        background-color: #4299e1; /* azul-500 */
        padding: 4px 10px;
        border-radius: 9999px;
        display: inline-block;
        margin-top: 20px;
    }
    .image img {
        max-width: 80%;
        max-height: 250px;
        display: block;
        margin: 20px auto 0;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    /* Estilo para os botões de áudio */
    .audio-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        cursor: pointer;
    }
    """

    anki_model = genanki.Model(
        model_id=settings.ANKI_MODEL_ID,
        name='Vocabulary Expander Model',
        fields=[
            {'name': 'Word'},
            {'name': 'Meaning'},
            {'name': 'Example'},
            {'name': 'Phonetic'},
            {'name': 'CEFR'},
            {'name': 'AudioWord'},
            {'name': 'AudioMeaning'},
            {'name': 'AudioExample'},
            {'name': 'Image'},
        ],
        templates=[{
            'name': 'Card 1',
            'qfmt': '<h1>{{Word}}</h1><div class="phonetic">{{Phonetic}}</div><div class="audio-button">{{AudioWord}}</div>',
            'afmt': '{{FrontSide}}\n\n<hr id="answer">\n\n<div class="meaning"><span>{{Meaning}}</span><span class="audio-button">{{AudioMeaning}}</span></div>\n<div class="example"><span>{{Example}}</span><span class="audio-button">{{AudioExample}}</span></div>\n<div class="cefr">{{CEFR}}</div>\n<div class="image">{{Image}}</div>',
        }],
        css=anki_css
    )

    media_files_to_include = []
    media_dir = Path(settings.media_dir)

    # Processa cada card no deck
    for card in deck_obj.deck_words:
        word: Word = card.word

        def get_audio_field(audio_type: str) -> str:
            audio_obj = next((a for a in word.audio if a.audio_type == audio_type), None)
            audio_path = media_dir / audio_obj.path if audio_obj and audio_obj.path else None
            
            if audio_path and audio_path.exists():
                if str(audio_path) not in media_files_to_include:
                    media_files_to_include.append(str(audio_path))
                return f"[sound:{audio_path.name}]"
            return ""

        audio_word_field = get_audio_field('word')
        audio_meaning_field = get_audio_field('meaning')
        audio_example_field = get_audio_field('example')

        image_obj: Image = word.image
        image_path = media_dir / image_obj.path if image_obj and image_obj.path else None
        
        if image_path and image_path.exists():
            media_files_to_include.append(str(image_path))
            image_field = f'<img src="{image_path.name}">'
        else:
            image_field = ""

        # Cria a nota do Anki com todos os campos
        note = genanki.Note(
            model=anki_model,
            fields=[
                word.text or "",
                word.meaning or "",
                word.example or "",
                f"/{word.phonetic}/" if word.phonetic else "",
                word.cefr or "",
                audio_word_field,
                audio_meaning_field,
                audio_example_field,
                image_field,
            ]
        )
        anki_deck.add_note(note)

    # Escreve o pacote num ficheiro temporário
    tmp = NamedTemporaryFile(suffix=".apkg", delete=False)
    package = genanki.Package(anki_deck)
    package.media_files = media_files_to_include
    package.write_to_file(tmp.name)
    tmp.close()
    
    return tmp.name
