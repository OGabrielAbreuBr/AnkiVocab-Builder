import os
import pandas as pd
import genanki
from tempfile import NamedTemporaryFile
from core.config import settings

def generate_anki_deck_from_csv(csv_path: str, media_dir: str, deck_name: str,
                                deck_id: int, model_id: int) -> str:
    """
    Gera um arquivo .apkg a partir de um CSV e retorna o caminho
    para o arquivo temporário gerado.
    """
    # 1. Carrega CSV
    df = pd.read_csv(csv_path)

    # 2. Cria deck e modelo
    deck = genanki.Deck(deck_id, deck_name)
    model = genanki.Model(
        model_id,
        'Modelo de Vocabulário',
        fields=[{'name': f} for f in (
            'Palavra','Pronuncia','Meaning','Example',
            'ÁudioFrente','ÁudioVersoMeaning','ÁudioVersoExample','Imagem'
        )],
        templates=[{
            'name': 'Card 1',
            'qfmt': settings.anki_qfmt,   # opcional: mova seus templates pra config
            'afmt': settings.anki_afmt,
        }],
        css=settings.anki_css
    )

    media_files = []

    # 3. Processa linhas
    for _, row in df.iterrows():
        # extrai e normaliza campos como no seu script
        word = str(row["Palavra"]).capitalize().strip() if pd.notnull(row["Palavra"]) else ""
        pron = str(row["Pronuncia"]).strip() if pd.notnull(row["Pronuncia"]) else ""
        mean = str(row["Meaning"]).strip() if pd.notnull(row["Meaning"]) else ""
        examp = str(row["Example"]).strip() if pd.notnull(row["Example"]) else ""

        def _get_media(field):
            raw = str(row[field]).strip() if pd.notnull(row[field]) else ""
            name = os.path.basename(raw)
            path = os.path.join(media_dir, name) if name else ""
            if path and os.path.exists(path):
                media_files.append(path)
                return name
            return ""

        audio_f = _get_media("AudioPalavra")
        audio_m = _get_media("AudioMeaning")
        audio_e = _get_media("AudioExample")
        img    = _get_media("Imagem")

        note = genanki.Note(
            model=model,
            fields=[
                word, pron, mean, examp,
                f"[sound:{audio_f}]" if audio_f else "",
                f"[sound:{audio_m}]" if audio_m else "",
                f"[sound:{audio_e}]" if audio_e else "",
                f"<img src='{img}'>"     if img    else ""
            ]
        )
        deck.add_note(note)

    # 4. Escreve em arquivo temporário
    tmp = NamedTemporaryFile(suffix=".apkg", delete=False)
    pkg = genanki.Package(deck)
    pkg.media_files = media_files
    pkg.write_to_file(tmp.name)
    tmp.close()
    return tmp.name
