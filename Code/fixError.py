import os
import re

# Configuração: Defina o diretório onde estão as imagens
pasta_imagens = r"C:\Users\gabri\Documents\DATA\AnkiCards\Vocabulary1\midias"

# Percorrer todos os arquivos na pasta
for nome_arquivo in os.listdir(pasta_imagens):
    caminho_antigo = os.path.join(pasta_imagens, nome_arquivo)

    # Verifica se é um arquivo (e não uma pasta)
    if not os.path.isfile(caminho_antigo):
        continue

    # Obter o nome do arquivo sem o diretório
    nome, extensao = os.path.splitext(nome_arquivo)

    # Criar o novo nome (converter para minúsculas e substituir espaços por "_")
    nome_corrigido = re.sub(r'\s+', '_', nome).lower()  # Substituir espaços por "_"
    novo_nome = f"{nome_corrigido}{extensao}"

    # Criar o novo caminho
    caminho_novo = os.path.join(pasta_imagens, novo_nome)

    # Se o nome já estiver correto, pular a renomeação
    if caminho_novo == caminho_antigo:
        continue

    # Renomear o arquivo
    try:
        os.rename(caminho_antigo, caminho_novo)
        print(f"Renomeado: {nome_arquivo} -> {novo_nome}")
    except Exception as e:
        print(f"Erro ao renomear {nome_arquivo}: {e}")

print("Processamento concluído. Todos os arquivos foram corrigidos!")
