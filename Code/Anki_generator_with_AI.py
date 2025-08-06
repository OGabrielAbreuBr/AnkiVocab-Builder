
# AIzaSyDftyiA6kLbg0iV2AhiRqBjyEsprYou98c - Google API Key
# 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

import pandas as pd
from gtts import gTTS
import os
import shutil
import google.generativeai as genai
import genanki
import epitran
import eng_to_ipa as ipa
import openai
import requests

# Configurar a API Key do Gemini (Google AI)
genai.configure(api_key="AIzaSyDftyiA6kLbg0iV2AhiRqBjyEsprYou98c")  # Substitua pela sua chave da API

openai.api_key = "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"  # Substitua pela sua chave da OpenAI

# Carregar CSV com as palavras
csv_file = "palavras3.csv"  # Nome do arquivo CSV
df = pd.read_csv(csv_file)

# Normaliza os nomes das colunas (remove espaços extras)
df.columns = df.columns.str.strip()

# Configurar o modelo do Gemini
model = genai.GenerativeModel("gemini-2.0-flash")

# Função para obter significado e exemplo do Gemini
def get_meaning_and_example(word):
    prompt = f"""
    Estou criando cards de vocabulário no Anki. Quando eu der uma palavra, gere o significado e um exemplo,
    usando como base o formato abaixo:

    Input: Apart

    Meaning: When people or things are apart, they are not next to each other.
    → Example: They moved apart and then came back together.

    Agora gere para esta palavra:
    Input: {word}

    Apenas retorne a linha Meaning e Example, não se esqueça a seta antes de Example.
    """
    response = model.generate_content(prompt)
    if response and hasattr(response, "text"):
        return response.text.strip()
    else:
        return "Não foi possível obter resposta."

# Função para criar o áudio usando gTTS
def create_audio(text, filename):
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(filename)

# Função para transcrever usando eng_to_ipa
def transcrever_fonetica(texto):
    return ipa.convert(texto)

def format_filename(text):
    return text.strip().replace(" ", "_")  # Substitui espaços por "_" e remove espaço no final

anki_model = genanki.Model(
    1607392319,
    'Modelo de Vocabulário',
    fields=[
        {'name': 'Palavra'},
        {'name': 'Pronúncia'},
        {'name': 'Significado'},
        {'name': 'Exemplo'},
        {'name': 'ÁudioFrente'},
        {'name': 'ÁudioVersoMeaning'},
        {'name': 'ÁudioVersoExample'},
        {'name': 'Imagem'},  # Se quiser manter este campo
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '''
<div class="card-container">
  <!-- Cabeçalho (opcional) -->
  <div class="header">Vocabulary Expander</div>

  <!-- Palavra em destaque -->
  <div class="word">{{Palavra}}</div>

  <hr class="divider">

  <!-- Áudio da frente -->
  <div class="audio-button">{{ÁudioFrente}}</div>

  <hr class="divider">

  <!-- Pronúncia -->
  <div class="pronunciation">{{Pronúncia}}</div>
</div>
            ''',
            'afmt': '''
<hr id="answer">

<!-- Palavra no verso -->
<div class="word">{{Palavra}}</div>

<hr class="divider">

<!-- Campo imagem (opcional) -->
<div class="image">{{Imagem}}</div>

<hr class="divider">

<!-- Significado -->
<div class="meaning-text">{{Significado}}</div>

<hr class="divider">

<!-- Exemplo -->
<div class="example-text">{{Exemplo}}</div>

<hr class="divider">

<!-- Contêiner para agrupar os botões de áudio -->
<div class="audio-container">
  <div class="audio-button">{{ÁudioFrente}}</div>

  <div class="audio-button">{{ÁudioVersoMeaning}}</div>
  <div class="audio-button">{{ÁudioVersoExample}}</div>
</div>
            ''',
        },
    ],
    css='''
/* Container geral */
.card-container {
    background-color: #1e1e1e;
    color: #ffffff;
    font-family: Arial, sans-serif;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
}

/* Cabeçalho */
.header {
    font-size: 22px;
    margin-bottom: 15px;
    color: #00ffff;
    text-align: left;
}

/* Palavra */
.word {
    font-size: 32px;
    font-weight: bold;
    color: #ff66cc;
    margin-bottom: 10px;
    text-align: center;
}

/* Imagem (opcional) */

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


/* Linha divisória */
.divider {
    border: none;
    border-top: 1px solid #cccccc;
    margin: 10px 0;
}

/* Botão/ícone de áudio */
.audio-button {
    font-size: 22px;
    margin: 10px 0;
    text-align: center;
    margin: center;
    cursor: pointer;
}

.audio-container {
    display: flex;
    justify-content: center; /* ou space-around, space-between, etc. */
    align-items: center;
    gap: 16px; /* espaçamento horizontal entre os botões */
    margin: 10px 0;
}

/* Pronúncia */
.pronunciation {
    font-size: 24px;
    color: #ff66cc;
    margin-top: 10px;
}

/* Texto do significado */
.meaning-text {
    font-size: 18px;
    color: #0AAAAA;
    margin-top: 10px;
    text-align: left;
}

/* Texto do exemplo */
.example-text {
    font-size: 18px;
    font-style: italic;
    color: #95F8FA;
    margin-top: 10px;
    text-align: left;
}

/* Linha da resposta do Anki */
hr#answer {
    margin-top: 20px;
    margin-bottom: 20px;
    border: 1px solid #ffffff;
}
    '''
)

def gerar_imagem(descricao, caminho_arquivo):
    try:
        response = openai.images.generate(
            model="dall-e-3",  # Ou "dall-e-3"
            prompt=descricao,
            n=1,
            size="1024x1024",
        )

        # Obter a URL da imagem gerada
        url_imagem = response.data[0].url

        # Baixar a imagem
        imagem_resposta = requests.get(url_imagem, stream=True)
        if imagem_resposta.status_code == 200:
            with open(caminho_arquivo, 'wb') as f:
                for chunk in imagem_resposta:
                    f.write(chunk)
            print(f"Imagem gerada com sucesso: {caminho_arquivo}")
            return caminho_arquivo
        else:
            print(f"Erro ao baixar a imagem para: {descricao}")
            return None
    except Exception as e:
        print(f"Erro ao gerar imagem: {e}")
        return None
    
# Criar um novo deck
anki_deck = genanki.Deck(
    2059400110,
    'Vocabulário Personalizado'
)

# Pasta para armazenar os arquivos de mídia
media_dir = 'anki_media'
os.makedirs(media_dir, exist_ok=True)

# Lista para armazenar os arquivos de mídia
media_files = []

# Processa cada palavra no CSV
for index, row in df.iterrows():
    palavra = row["palavra"].strip()  # Remove espaços extras
    palavra_formatada = format_filename(palavra)

    print(f"Consultando significado para: {palavra}...")
    resposta = get_meaning_and_example(palavra)
    print(resposta)

    try:
        significado = resposta.split('Meaning: ')[1].split('→ Example: ')[0].strip()
        exemplo = resposta.split('→ Example: ')[1].strip()
    except IndexError:
        significado = "Significado não encontrado."
        exemplo = "Exemplo não encontrado."

    # Gerar a imagem com DALL·E
    descricao_imagem = (
        f"""A visually engaging and clear depiction of the word '{palavra}'.
        It should represent: {significado}. 
        Example sentence: '{exemplo}'. 
        The image should emphasize the concept and make it easily understandable.
        Use simple yet detailed visuals, bright colors, and clear composition.
        Avoid excessive abstraction. Focus on clarity and meaning.
        """
    )

    caminho_imagem = os.path.join(media_dir, f"{palavra}.png")

    # Tenta gerar a imagem e verifica se foi gerada corretamente
    imagem_gerada = gerar_imagem(descricao_imagem, caminho_imagem)
    if imagem_gerada:  
        media_files.append(caminho_imagem)  # Adiciona ao pacote de mídia do Anki

    # Gerar a transcrição fonética
    pronuncia = transcrever_fonetica(palavra)

    # Gerar áudios
    audio_front = f"{palavra_formatada}.mp3"
    create_audio(palavra, os.path.join(media_dir, audio_front))
    media_files.append(os.path.join(media_dir, audio_front))

    audio_back_meaning = f"{palavra_formatada}_meaning.mp3"
    create_audio(significado, os.path.join(media_dir, audio_back_meaning))
    media_files.append(os.path.join(media_dir, audio_back_meaning))

    audio_back_example = f"{palavra_formatada}_example.mp3"
    create_audio(exemplo, os.path.join(media_dir, audio_back_example))  
    media_files.append(os.path.join(media_dir, audio_back_example))

    # Criar a nota do Anki (com 7 valores, pois temos 7 campos)
    note = genanki.Note(
        model=anki_model,
        fields=[
            palavra,
            pronuncia,
            "Meaning: " + significado,
            "→ Example: " + exemplo,
            f"[sound:{audio_front}]",
            f"[sound:{audio_back_meaning}]",
            f"[sound:{audio_back_example}]",
            f"<img src='{palavra}.png'>" if imagem_gerada else
            ""  # Caso campo 'Imagem' esteja vazio (caso não tenha imagem)
        ]
    )

    # Adicionar a nota ao deck
    anki_deck.add_note(note)

# Salvar o deck em um arquivo .apkg
anki_package = genanki.Package(anki_deck)
anki_package.media_files = media_files  # Inclui os arquivos de áudio no pacote
anki_package.write_to_file('Vocabulary Expander with AI.apkg')

print("\nO deck 'Vocabulary Expander with AI.apkg' foi gerado com sucesso.")
