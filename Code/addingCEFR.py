import pandas as pd

def atualizar_cefr(target_csv, lookup_csv, target_col='Palavra', output_csv=None):
    """
    Atualiza (sobrescreve) a coluna 'CEFR' no CSV alvo utilizando os dados do CSV de referência.
    
    Parâmetros:
      - target_csv: Caminho para o CSV alvo que será atualizado.
      - lookup_csv: Caminho para o CSV de referência contendo as colunas 'Palavra' e 'CEFR'.
      - target_col: Nome da coluna que contém as palavras (default: 'Palavra').
      - output_csv: Se fornecido, salva o CSV atualizado neste caminho.
      
    Retorna:
      - Um DataFrame com a coluna 'CEFR' atualizada (sobrescrita) a partir do CSV de referência.
    """
    # Carrega o CSV de referência com as colunas 'Palavra' e 'CEFR'
    df_lookup = pd.read_csv(lookup_csv, encoding='utf-8')
    
    # Carrega o CSV alvo
    df_target = pd.read_csv(target_csv, encoding='utf-8')
    
    # Remove a coluna 'CEFR' do CSV alvo se ela já existir, para sobrescrever com os novos valores
    if 'CEFR' in df_target.columns:
        df_target.drop(columns=['CEFR'], inplace=True)
    
    # Realiza o merge (junção) dos DataFrames com base na coluna 'Palavra'
    df_atualizado = df_target.merge(df_lookup[[target_col, 'CEFR']], on=target_col, how='left')
    
    # Se um caminho para output for fornecido, salva o DataFrame atualizado em um novo CSV
    if output_csv:
        df_atualizado.to_csv(output_csv, index=False, encoding='utf-8')
        print(f"Arquivo atualizado salvo em: {output_csv}")
    
    return df_atualizado

if __name__ == "__main__":
    # Exemplo de uso:
    # CSV de referência: 'lookup_cefr.csv' (contém as colunas 'Palavra' e 'CEFR')
    # CSV alvo: 'vocabulario.csv' (contém pelo menos a coluna 'Palavra')
    lookup_csv_path = r"C:\Users\gabri\Documents\DATA\AnkiCards\Code\ENGLISH_CERF_WORDS.csv"
    target_csv_path = r"C:\Users\gabri\Documents\DATA\AnkiCards\csv_final_completo copy.csv"
    output_csv_path = r"C:\Users\gabri\Documents\DATA\AnkiCards\csv_final_completo copy.csv"
    
    df_resultado = atualizar_cefr(target_csv_path, lookup_csv_path, output_csv=output_csv_path)
    print("Atualização concluída. Exemplo de linhas do CSV atualizado:")
    print(df_resultado.head())
