from compara_palavras_do_CSV import gerar_csv_comum
from ChangingNamesFromAPKG import change_names_from_folder_with_json
from change_names import change_files_names_in_folder
from Anki_Generator_From_DataBase import generate_anki_from_database
from adapt_database_to_anki import adapt_csv
from change_names import change_files_names_in_folder
from csv_generator_from_dataBase_pure_text import converter_html_para_csv
import pandas as pd
from gtts import gTTS



import os
import pandas as pd
from gtts import gTTS


def create_audio(text, filename):
    """
    Gera um arquivo de áudio .mp3 com o texto fornecido, usando gTTS.
    """
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(filename)

def gerar_audios_example(csv_saida, media_dir):
    """
    Lê o CSV, obtém a coluna 'Example',
    gera arquivos .mp3 com gTTS a partir desses textos,
    e salva na pasta 'media_dir'.
    """
    df = pd.read_csv(csv_saida, encoding='utf-8')

    for index, row in df.iterrows():
        # Garante que existe alguma coisa na coluna Example
        example_text = str(row["Example"]).strip() if pd.notnull(row["Example"]) else ""
        if not example_text:
            continue

        # Cria um nome para o arquivo baseado na coluna "Palavra"
        word = str(row["Palavra"]).strip().lower().replace(" ", "_")
        audio_filename = f"{word}_example.mp3"

        # Caminho completo onde será salvo o arquivo
        full_path = os.path.join(media_dir, audio_filename)

        print(f"Gerando áudio para '{row['Palavra']}': {audio_filename}...")
        create_audio(example_text, full_path)

    print("\nConcluído! Arquivos de áudio gerados na pasta:", media_dir)

def rename_png_files_to_lower(folder_path):
    """
    Percorre a pasta 'folder_path', encontrando arquivos que terminam em .png,
    e renomeia todos para minúsculas (inclusive a extensão).
    """
    for filename in os.listdir(folder_path):
        # Verifica se o arquivo termina com .png (case-insensitive)
        
        if filename.lower().endswith(".png"):
            old_path = os.path.join(folder_path, filename)
            new_filename = filename.lower()  # ex.: "MinhasFOTOS.PnG" -> "minhasfotos.png"
            new_path = os.path.join(folder_path, new_filename)
                    # Só renomeia se o nome realmente mudar
            if old_path != new_path:
                print('oi')
                try:
                    os.rename(old_path, new_path)
                    print(f"Renomeado: {filename} -> {new_filename}")
                except Exception as e:
                    print(f"Erro ao renomear '{filename}': {e}")

   


# Exemplo de uso:
if __name__ == "__main__":
    caminhojson = r'C:\Users\gabri\Documents\DATA\AnkiCards\VocabulárioPersonalizado\media.json'
    caminhoOrigem = r'C:\Users\gabri\Documents\DATA\AnkiCards\VocabulárioPersonalizado'
    media_dir = r'C:\Users\gabri\Documents\DATA\AnkiCards\VocabulárioPersonalizado\midias'
    html_entrada = r"C:\Users\gabri\Documents\DATA\AnkiCards\VocabularioPersonalizado.html"
    csv_saida = "VocabWithAI.csv"

    # gerar_audios_example(csv_saida, media_dir)
    rename_png_files_to_lower(media_dir)
