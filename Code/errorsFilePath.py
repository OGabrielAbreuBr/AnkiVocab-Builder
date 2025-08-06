import pandas as pd
import os

# Caminho do seu arquivo de entrada (CSV) 
input_csv = r"C:\Users\gabri\Documents\DATA\AnkiCards\db.csv"
# Caminho do CSV de saída
output_csv = "output.csv"

# Carrega o CSV, assumindo que não há cabeçalho (header=None).
# Se houver cabeçalho, adapte conforme necessário (header=0, names=[...], etc.).
df = pd.read_csv(input_csv, header=None, encoding='utf-8')

# Supondo que cada linha está no formato:
# 0: Palavra
# 1: Caminho do áudio (palavra)
# 2: Pronuncia
# 3: Caminho da imagem
# 4: Meaning
# 5: Example
# 6: Caminho do áudio (Meaning)
# 7: Caminho do áudio (Example)
#
# Caso sua estrutura seja diferente, ajuste o índice das colunas abaixo.

colunas_midias = [1, 3, 6, 7]  # ÍNDICES das colunas onde queremos extrair apenas o nome do arquivo

for col in colunas_midias:
    # Aplica 'os.path.basename' para extrair somente o nome do arquivo
    df[col] = df[col].apply(
        lambda x: os.path.basename(x) if pd.notnull(x) else x
    )

# Salva em outro CSV, sem cabeçalho e sem índice
df.to_csv(output_csv, header=False, index=False, encoding='utf-8')
