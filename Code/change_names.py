import os
import csv

def change_files_names_in_folder(csv_filename, media_dir):
    """
    1) Lê cada linha do CSV.
    2) Para cada uma das colunas de mídia (AudioPalavra, AudioMeaning, AudioExample, Imagem):
       - Extrai só o nome do arquivo (basename).
       - Define um novo nome baseado em 'palavra' (com espaços trocados por '_').
       - Renomeia o arquivo fisicamente na pasta 'media_dir'.
       - Atualiza o CSV para o novo nome.
    3) Reescreve o CSV, mantendo o resto igual.
    """

    media_columns = ["AudioPalavra", "AudioMeaning", "AudioExample", "Imagem"]

    with open(csv_filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    for row in rows:
        # Substituir espaços por underscores e converter para minúsculo
        palavra = row["Palavra"].strip().lower().replace(" ", "_")

        for col in media_columns:
            media_path = row[col].strip()
            if not media_path:
                continue

            # Extrai nome do arquivo e extensão
            filename = os.path.basename(media_path)
            ext = os.path.splitext(filename)[1]

            # Define o novo nome dependendo da coluna
            if col == "AudioMeaning":
                new_filename = f"{palavra}_meaning{ext}"
            elif col == "AudioExample":
                new_filename = f"{palavra}_example{ext}"
            else:
                # Para AudioPalavra ou Imagem
                new_filename = f"{palavra}{ext}"

            old_path = os.path.join(media_dir, filename)
            new_path = os.path.join(media_dir, new_filename)

            if os.path.exists(old_path):
                try:
                    os.rename(old_path, new_path)
                    print(f"Renomeado: {old_path} -> {new_path}")
                except Exception as e:
                    print(f"Erro ao renomear {old_path}: {e}")
            else:
                print(f"Arquivo não encontrado: {old_path}")

            # Atualiza o CSV
            row[col] = new_filename

    # Salva o CSV de volta
    fieldnames = rows[0].keys()
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    csv_file = r"C:\Users\gabri\Documents\DATA\AnkiCards\Vocabulary1\VocabWithAI.csv"
    media_dir = r"C:\Users\gabri\Documents\DATA\AnkiCards\Vocabulary1\midias"

    change_files_names_in_folder(csv_file, media_dir)

if __name__ == "__main__":
    main()
