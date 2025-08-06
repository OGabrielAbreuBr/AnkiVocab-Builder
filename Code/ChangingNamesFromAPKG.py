import os
import json

# Caminho do JSON (ajuste se necessário)
caminho_json = r"C:\Users\gabri\Documents\DATA\AnkiCards\Vocabulary1\media.json"

# Pasta onde estão os arquivos numerados (ajuste se necessário)
pasta_origem = r"C:\Users\gabri\Documents\DATA\AnkiCards\Vocabulary1"

# Pasta de destino onde serão movidos/renomeados
pasta_destino = r"C:\Users\gabri\Documents\DATA\AnkiCards\Vocabulary1\midias"

def change_names_from_folder_with_json(caminho_json, pasta_origem, pasta_destino):

    # Cria a pasta de destino caso não exista
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    # Lê o JSON
    with open(caminho_json, "r", encoding="utf-8") as f:
        dados = json.load(f)

    for numero, nome_completo in dados.items():
        # Separa o nome_base (ex: 'audioBackExample_29') e a extensão (ex: '.mp3')
        nome_base, extensao = os.path.splitext(nome_completo)

        # Caminho atual do arquivo (ex: arquivos/1)
        arquivo_origem = os.path.join(pasta_origem, numero)

        # Caminho final do arquivo (ex: saida/audioBackExample_29.mp3)
        arquivo_destino = os.path.join(pasta_destino, nome_base + extensao)

        if os.path.exists(arquivo_origem):
            os.rename(arquivo_origem, arquivo_destino)
            print(f"Movido e renomeado: {arquivo_origem} -> {arquivo_destino}")
        else:
            print(f"Arquivo não encontrado: {arquivo_origem}")
