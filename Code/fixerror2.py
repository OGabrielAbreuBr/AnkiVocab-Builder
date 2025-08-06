import os
import pandas as pd

def remover_audios_vazios(csv_path, media_dir):
    """
    Lê o CSV e, para cada linha, verifica se Meaning/Example são 'NaN' ou vazios.
    Se estiverem vazios, remove os arquivos de áudio correspondentes no 'media_dir'.
    """

    df = pd.read_csv(csv_path, encoding='utf-8')

    for idx, row in df.iterrows():
        # Checa se a Meaning está "NaN" ou vazia
        meaning = str(row.get("Meaning", "")).strip()
        audio_meaning = str(row.get("AudioMeaning", "")).strip()
        if not meaning or meaning.lower() == "nan":
            # Se tiver um arquivo de áudio configurado
            if audio_meaning:
                path_meaning = os.path.join(media_dir, audio_meaning)
                if os.path.exists(path_meaning):
                    print(f"Removendo áudio de Meaning (vazio/NaN): {path_meaning}")
                    os.remove(path_meaning)

        # Checa se a Example está "NaN" ou vazia
        example = str(row.get("Example", "")).strip()
        audio_example = str(row.get("AudioExample", "")).strip()
        if not example or example.lower() == "nan":
            # Se tiver um arquivo de áudio configurado
            if audio_example:
                path_example = os.path.join(media_dir, audio_example)
                if os.path.exists(path_example):
                    print(f"Removendo áudio de Example (vazio/NaN): {path_example}")
                    os.remove(path_example)

if __name__ == "__main__":
    csv_arquivo = r"C:\Users\gabri\Documents\DATA\AnkiCards\csv_final_completo.csv"
    pasta_midias = r"C:\Users\gabri\Documents\DATA\AnkiCards\Vocabulary1\midias"

    remover_audios_vazios(csv_arquivo, pasta_midias)
