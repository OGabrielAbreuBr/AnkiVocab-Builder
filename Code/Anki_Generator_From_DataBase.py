import pandas as pd
import os
import genanki

# Ajuste esses caminhos conforme necessário
csv_file = r"C:\Users\gabri\Documents\DATA\AnkiCards\teste_DB\palavras_filtradas1000.csv"  # CSV com as informações das palavras
media_dir = r"C:\Users\gabri\Documents\DATA\AnkiCards\DB\4000 Essential English Words\midias"  # Pasta onde estão os arquivos de mídia

def generate_anki_from_database(csv_file, media_dir):
    # Verificar se o CSV existe
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Arquivo CSV '{csv_file}' não foi encontrado!")

    # Ler a base de dados
    df = pd.read_csv(csv_file)

    # Criar um novo deck Anki
    anki_deck = genanki.Deck(
        2059400110,  # ID do deck (pode alterar se desejar)
        'Vocabulário com Mídia'
    )

    # Modelo do Anki (mantendo o mesmo estilo)
    anki_model = genanki.Model(
        1607392319,  # ID do modelo (pode alterar se desejar)
        'Modelo de Vocabulário',
        fields=[
            {'name': 'Palavra'},
            {'name': 'Pronuncia'},
            {'name': 'Meaning'},
            {'name': 'Example'},
            {'name': 'ÁudioFrente'},
            {'name': 'ÁudioVersoMeaning'},
            {'name': 'ÁudioVersoExample'},
            {'name': 'Imagem'}
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '''
<div class="card-container">
    <div class="header">Vocabulary Expander</div>
    <div class="word">{{Palavra}}</div>
    <hr class="divider">
    <div class="audio-button">{{ÁudioFrente}}</div>
    <hr class="divider">
    <div class="pronunciation">{{Pronuncia}}</div>
</div>
                ''',
                'afmt': '''
<hr id="answer">
<div class="word">{{Palavra}}</div>
<hr class="divider">
<div class="image">{{Imagem}}</div>
<hr class="divider">
<div class="meaning-text">Meaning: {{Meaning}}</div>
<hr class="divider">
<div class="example-text">→ Example: {{Example}}</div>
<hr class="divider">
<div class="audio-container">
    <div class="audio-button">{{ÁudioVersoMeaning}}</div>
    <div class="audio-button">{{ÁudioVersoExample}}</div>
</div>
                ''',
            },
        ],
        css='''
.card-container {
    background-color: #1e1e1e;
    color: #ffffff;
    font-family: Arial, sans-serif;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
}
.header {
    font-size: 22px;
    margin-bottom: 15px;
    color: #00ffff;
    text-align: left;
}
.word {
    font-size: 32px;
    font-weight: bold;
    color: #ff66cc;
    margin-bottom: 10px;
    text-align: center;
}
.divider {
    border: none;
    border-top: 1px solid #cccccc;
    margin: 10px 0;
}


.image{
    margin: center;
    text-align: center;
}
.image img {
    margin: 10px 0;
    text-align: center;
    width: 256px;  /* Largura da imagem */
    height: 256px; /* Altura da imagem */
    border-radius: 8px; /* Bordas arredondadas */
    object-fit: cover; /* Garante que a imagem preencha o espaço sem distorção */
   
}
.audio-button {
    font-size: 22px;
    margin: 10px 0;
    text-align: center;
    cursor: pointer;
}
.audio-container {
    display: flex;
    justify-content: center;
    gap: 16px;
    margin: 10px 0;
}
.pronunciation {
    font-size: 24px;
    color: #ff66cc;
    margin-top: 10px;
}
.meaning-text {
    font-size: 18px;
    color: #0AAAAA;
    margin-top: 10px;
    text-align: left;
}
.example-text {
    font-size: 18px;
    font-style: italic;
    color: #95F8FA;
    margin-top: 10px;
    text-align: left;
}
hr#answer {
    margin-top: 20px;
    margin-bottom: 20px;
    border: 1px solid #ffffff;
}
        '''
    )

    # Lista para armazenar os arquivos de mídia
    media_files = []

    # Processa cada linha do CSV
    for index, row in df.iterrows():
        # Extrair campos de texto
        palavra = str(row["Palavra"]).strip() if pd.notnull(row["Palavra"]) else ""
        palavra = palavra.capitalize()
        pronuncia = str(row["Pronuncia"]).strip() if pd.notnull(row["Pronuncia"]) else ""
        Meaning = str(row["Meaning"]).strip() if pd.notnull(row["Meaning"]) else ""
        Example = str(row["Example"]).strip() if pd.notnull(row["Example"]) else ""

        # Pega o nome do arquivo de áudio e gera caminho completo,
        # mas no HTML usaremos somente o nome (basename).
        audio_palavra_raw = str(row["AudioPalavra"]).strip() if pd.notnull(row["AudioPalavra"]) else ""
        audio_palavra_nome = os.path.basename(audio_palavra_raw)  # só o nome do arquivo
        caminho_audio = os.path.join(media_dir, audio_palavra_nome) if audio_palavra_nome else ""

        audio_meaning_raw = str(row["AudioMeaning"]).strip() if pd.notnull(row["AudioMeaning"]) else ""
        audio_meaning_nome = os.path.basename(audio_meaning_raw)
        caminho_audio_meaning = os.path.join(media_dir, audio_meaning_nome) if audio_meaning_nome else ""

        audio_example_raw = str(row["AudioExample"]).strip() if pd.notnull(row["AudioExample"]) else ""
        audio_example_nome = os.path.basename(audio_example_raw)
        caminho_audio_example = os.path.join(media_dir, audio_example_nome) if audio_example_nome else ""

        # Para a imagem, mesma lógica: usamos basename para inserir no HTML.
        imagem_raw = str(row["Imagem"]).strip() if pd.notnull(row["Imagem"]) else ""
        imagem_nome = os.path.basename(imagem_raw)
        caminho_imagem = os.path.join(media_dir, imagem_nome) if imagem_nome else ""

        # Verifica se os arquivos de áudio/imagem existem
        # Se não existirem, "limpamos" o caminho para não adicioná-los.
        if caminho_audio and not os.path.exists(caminho_audio):
            print(f"⚠️ Aviso: O arquivo de áudio '{caminho_audio}' não foi encontrado. Pulando esta mídia.")
            caminho_audio = ""
            audio_palavra_nome = ""

        if caminho_audio_meaning and not os.path.exists(caminho_audio_meaning):
            print(f"⚠️ Aviso: O arquivo de áudio do Meaning '{caminho_audio_meaning}' não foi encontrado.")
            caminho_audio_meaning = ""
            audio_meaning_nome = ""

        if caminho_audio_example and not os.path.exists(caminho_audio_example):
            print(f"⚠️ Aviso: O arquivo de áudio do Example '{caminho_audio_example}' não foi encontrado.")
            caminho_audio_example = ""
            audio_example_nome = ""

        if caminho_imagem and not os.path.exists(caminho_imagem):
            print(f"⚠️ Aviso: O arquivo de imagem '{caminho_imagem}' não foi encontrado.")
            caminho_imagem = ""
            imagem_nome = ""

        # Adicionar somente os caminhos não vazios à lista de mídia
        if caminho_audio:
            media_files.append(caminho_audio)
        if caminho_audio_meaning:
            media_files.append(caminho_audio_meaning)
        if caminho_audio_example:
            media_files.append(caminho_audio_example)
        if caminho_imagem:
            media_files.append(caminho_imagem)

        # O campo "ÁudioFrente" deve usar [sound:nome_do_arquivo].
        # O campo "Imagem" deve usar <img src="nome_do_arquivo">.
        note = genanki.Note(
            model=anki_model,
            fields=[
                palavra,
                pronuncia,
                Meaning,
                Example,
                f"[sound:{audio_palavra_nome}]" if audio_palavra_nome else "",
                f"[sound:{audio_meaning_nome}]" if audio_meaning_nome else "",
                f"[sound:{audio_example_nome}]" if audio_example_nome else "",
                f"<img src='{imagem_nome}'>" if imagem_nome else ""
            ]
        )

        # Adicionar a nota ao deck
        anki_deck.add_note(note)

    # Criar pacote Anki
    anki_package = genanki.Package(anki_deck)
    anki_package.media_files = media_files
    anki_package.write_to_file('Vocabulary_Media_Anki.apkg')

    print("\n✅ O deck 'Vocabulary_Media_Anki.apkg' foi gerado com sucesso!")

if __name__ == "__main__":
    generate_anki_from_database(csv_file, media_dir)
