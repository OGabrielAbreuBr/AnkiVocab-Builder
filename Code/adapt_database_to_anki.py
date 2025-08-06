import pandas as pd
import os
import re
from gtts import gTTS
import eng_to_ipa as ipa

def create_audio(text, filename):
    """
    Cria o áudio usando gTTS.
    Se o texto estiver vazio, a criação é pulada.
    """
    if not text or str(text).strip() == "":
        print(f"Texto vazio para {filename}, pulando criação de áudio.")
        return
    print(f"Criando áudio para texto: '{str(text)[:30]}...' em: {filename}")
    tts = gTTS(text=str(text), lang='en', slow=False)
    tts.save(filename)
    print(f"Áudio salvo em: {filename}")

def transcrever_fonetica(texto):
    """
    Transcreve o texto para representação fonética usando eng_to_ipa.
    Se o texto estiver vazio, retorna uma string vazia.
    """
    if not texto or str(texto).strip() == "":
        print("Texto vazio para transcrição fonética, retornando string vazia.")
        return ""
    texto = str(texto)
    pronuncia = ipa.convert(texto)
    print(f"Transcrição fonética gerada para '{texto}': {pronuncia}")
    return pronuncia

def sanitize_filename(filename):
    """
    Sanitiza o nome, removendo espaços no início/fim, substituindo espaços internos por underlines 
    e removendo caracteres inválidos para nomes de arquivos.
    """
    filename = filename.strip().replace(" ", "_")
    return re.sub(r'[\\/:*?"<>|]', '_', filename)

def adapt_csv(csv_file_path, media_dir, reference_csv=r"C:\Users\gabri\Documents\DATA\AnkiCards\db.csv"):
    """
    Adapta o CSV principal para que possua as mesmas colunas do CSV de referência e,
    para cada linha em que a coluna "Pronuncia" esteja vazia, gera:
      - O áudio da palavra em {Palavra}.mp3
      - O áudio do significado em {Palavra}_meaning.mp3
      - O áudio do exemplo em {Palavra}_example.mp3
      - A transcrição fonética na coluna "Pronuncia"

    Os caminhos dos áudios gerados são atualizados no CSV.
    Mensagens são impressas para acompanhamento.
    """
    print("Carregando CSV principal e CSV de referência...")
    df = pd.read_csv(csv_file_path)
    df_ref = pd.read_csv(reference_csv)
    required_columns = df_ref.columns.tolist()
    
    # Adiciona colunas ausentes com valores nulos e reordena
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    df = df[required_columns]
    
    os.makedirs(media_dir, exist_ok=True)
    print(f"Diretório de mídia garantido: {media_dir}")
    
    def process_media_files(palavra, meaning, example, media_dir, existing_pronuncia=None):
        media = {}
        # Converte para string e sanitiza o nome da palavra
        palavra = "" if pd.isna(palavra) else str(palavra)
        meaning = "" if pd.isna(meaning) else str(meaning)
        example = "" if pd.isna(example) else str(example)
        palavra_formatada = sanitize_filename(palavra)
        print(f"Processando arquivos para a palavra: '{palavra}' (sanitizado: '{palavra_formatada}')")
        
        # Áudio da palavra: {palavra}.mp3
        audio_palavra = f"{palavra_formatada}.mp3"
        audio_palavra_path = os.path.join(media_dir, audio_palavra)
        if not audio_palavra or audio_palavra.strip() == "":
            media["AudioPalavra"] = ""
        else:
            if not os.path.exists(audio_palavra_path):
                create_audio(palavra, audio_palavra_path)
            else:
                print(f"Áudio já existe: {audio_palavra_path}")
            media["AudioPalavra"] = audio_palavra_path
        
        # Áudio do significado: {palavra}_meaning.mp3
        audio_meaning = f"{palavra_formatada}_meaning.mp3"
        audio_meaning_path = os.path.join(media_dir, audio_meaning)
        if not meaning or meaning.strip() == "":
            media["AudioMeaning"] = ""
        else:
            if not os.path.exists(audio_meaning_path):
                create_audio(meaning, audio_meaning_path)
            else:
                print(f"Áudio já existe: {audio_meaning_path}")
            media["AudioMeaning"] = audio_meaning_path
        
        # Áudio do exemplo: {palavra}_example.mp3
        audio_example = f"{palavra_formatada}_example.mp3"
        audio_example_path = os.path.join(media_dir, audio_example)
        if not example or example.strip() == "":
            media["AudioExample"] = ""
        else:
            if not os.path.exists(audio_example_path):
                create_audio(example, audio_example_path)
            else:
                print(f"Áudio já existe: {audio_example_path}")
            media["AudioExample"] = audio_example_path
        
        # Transcrição fonética: gera se não existir
        if existing_pronuncia is None or pd.isna(existing_pronuncia) or str(existing_pronuncia).strip() == "":
            pronuncia = transcrever_fonetica(palavra)
        else:
            pronuncia = existing_pronuncia
        return media, pronuncia

    print("Iniciando processamento de cada linha do CSV...")
    for index, row in df.iterrows():
        if pd.isna(row["Pronuncia"]) or row["Pronuncia"].strip() == "":
            print(f"Processando linha {index} - Palavra: '{row['Palavra']}'")
            media_files, pronuncia = process_media_files(
                palavra=row["Palavra"],
                meaning=row["Meaning"],
                example=row["Example"],
                media_dir=media_dir,
                existing_pronuncia=row.get("Pronuncia")
            )
            df.at[index, "Pronuncia"] = pronuncia
            df.at[index, "AudioPalavra"] = media_files["AudioPalavra"]
            df.at[index, "AudioMeaning"] = media_files["AudioMeaning"]
            df.at[index, "AudioExample"] = media_files["AudioExample"]
        else:
            print(f"Linha {index} já possui transcrição: '{row['Pronuncia']}'")
    
    df.to_csv(csv_file_path, index=False)
    print("Processamento concluído. CSV atualizado e arquivos de mídia gerados (se aplicável).")
    return df

if __name__ == "__main__":
    csv_path = r"C:\Users\gabri\Documents\DATA\AnkiCards\DB_Vocabulary1 copy.csv"
    media_directory = r"C:\Users\gabri\Documents\DATA\AnkiCards\Vocabulary1\midias"
    
    df_updated = adapt_csv(csv_path, media_directory)
