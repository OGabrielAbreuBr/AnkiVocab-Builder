import pandas as pd
import os

# Caminho do arquivo CSV original
file_path = 'ENGLISH_CERF_WORDS.csv'

# Carregar o CSV
df = pd.read_csv(file_path)

# Criar diretório de saída
output_dir = 'cefr_levels'
os.makedirs(output_dir, exist_ok=True)

# Gerar CSV para cada nível CEFR
for level in df['CEFR'].unique():
    # Filtrar palavras pelo nível atual
    level_df = df[df['CEFR'] == level]
    
    # Nome do arquivo CSV para o nível atual
    csv_filename = f'{output_dir}/words_{level}.csv'
    
    # Salvar CSV
    level_df.to_csv(csv_filename, index=False)

print("Arquivos CSV gerados com sucesso!")
