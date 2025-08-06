import os
import csv
import re
import csv

def altera_csv(file_path):
    # Lê todo o conteúdo do CSV
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        linhas = list(reader)

    # Itera sobre as linhas (exceto o cabeçalho)
    for i, linha in enumerate(linhas):
        if i == 0:  # pula o cabeçalho
            continue

        # Verifica se a linha tem pelo menos 6 colunas
        if len(linha) < 6:
            print(f"Linha {i} não possui colunas suficientes: {linha}")
            continue

        palavra = linha[0].strip()

        # Atualiza o campo AudioPalavra
        if linha[5]:
            pasta_audio = os.path.dirname(linha[5])
            linha[5] = os.path.join(pasta_audio, f"{palavra}.mp3")
        else:
            print(f"Linha {i} tem campo 'AudioPalavra' vazio.")

        # Atualiza o campo Imagem
        if linha[4]:
            pasta_imagem = os.path.dirname(linha[4])
            linha[4] = os.path.join(pasta_imagem, f"{palavra}.jpg")
        else:
            print(f"Linha {i} tem campo 'Imagem' vazio.")

    # Sobrescreve o CSV com os novos dados
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(linhas)

# Nome do arquivo CSV
csv_filename = r"C:\Users\gabri\Documents\DATA\AnkiCards\DB_Vocabulary1.csv"

# Pasta base onde estão os arquivos (ajuste conforme necessário)
base_folder = r'C:\Users\gabri\Documents\DATA\AnkiCards\Vocabulary1\midias'  # ex.: "C:/Projetos/Midias"

# Colunas do CSV que contém os caminhos dos arquivos de mídia
media_columns = ["Imagem", "AudioPalavra"]

with open(csv_filename, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        palavra = row["Palavra"]
        for col in media_columns:
            # O CSV informa o caminho relativo do arquivo, por exemplo: midias_extraidas\01_0001.mp3
            relative_path = row[col]
            # Obtemos apenas o nome do arquivo para montar o caminho completo
            filename = os.path.basename(relative_path)
            # Monta o caminho completo do arquivo na pasta de mídias
            old_path = os.path.join(base_folder, filename)
            
            if os.path.exists(old_path):
                # Separa o diretório e o nome do arquivo
                # Separa o diretório e o nome do arquivo
                dir_path, old_filename = os.path.split(old_path)
                # Pega a extensão do arquivo
                extensao = os.path.splitext(old_filename)[1]
                # Novo nome: palavra + extensão original
                new_filename = f"{palavra}{extensao}"
                new_path = os.path.join(dir_path, new_filename)
                try:
                    os.rename(old_path, new_path)
                    print(f"Renomeado: {old_path} -> {new_path}")
                except Exception as e:
                    print(f"Erro ao renomear {old_path}: {e}")


altera_csv(csv_filename)