import pandas as pd
import glob
import os

# Nome do arquivo atual (exemplo: palavras3.csv)
file_atual = "palavras3.csv"

# Extrair o índice do arquivo atual (número no nome do arquivo)
indice_atual = int(''.join(filter(str.isdigit, file_atual)))

# Listar todos os arquivos CSV no diretório
todos_arquivos = glob.glob("palavras*.csv")

# Função para extrair o número do nome do arquivo com segurança
def extract_number(filename):
    num_str = ''.join(filter(str.isdigit, filename))
    return int(num_str) if num_str else None  # Retorna None se não houver número

# Filtrar apenas os arquivos com índice menor que o atual
arquivos_anteriores = [
    f for f in todos_arquivos if f != file_atual and extract_number(f) is not None and extract_number(f) < indice_atual
]

# Carregar as palavras dos arquivos anteriores e armazenar em um conjunto
set_palavras_anteriores = set()
for arquivo in arquivos_anteriores:
    df_temp = pd.read_csv(arquivo, header=None, names=['Palavras'])
    set_palavras_anteriores.update(df_temp['Palavras'].str.lower().str.strip())

# Carregar o arquivo atual
df_atual = pd.read_csv(file_atual, header=None, names=['Palavras'])

# Criar um conjunto com as palavras do arquivo atual (para verificar repetições internas)
set_palavras_atual = set(df_atual['Palavras'].str.lower().str.strip())

# Identificar palavras repetidas dentro do próprio arquivo atual
repetidas_atual = df_atual[df_atual.duplicated(subset=['Palavras'], keep=False)]

# Identificar palavras que já existem nos arquivos anteriores
palavras_proibidas = set_palavras_atual.intersection(set_palavras_anteriores)

# Filtrar o arquivo atual removendo palavras duplicadas (internas e das anteriores)
df_filtrado = df_atual[~df_atual['Palavras'].str.lower().str.strip().isin(set_palavras_anteriores)]

# Salvar o novo arquivo filtrado
file_filtrado = file_atual  # Sobrescreve o arquivo original
df_filtrado.to_csv(file_filtrado, index=False, header=False)

# Exibir resultados
print(f"\nArquivos verificados antes de {file_atual}: {arquivos_anteriores}")

print("\nPalavras repetidas dentro do próprio arquivo atual:")
print(repetidas_atual)

print("\nPalavras removidas porque já existiam nos arquivos anteriores:")
print(palavras_proibidas)

print(f"\nNovo arquivo filtrado salvo como: {file_filtrado}")
