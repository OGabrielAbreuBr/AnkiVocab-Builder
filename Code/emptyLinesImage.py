import pandas as pd

def contar_imagens_vazias(csv_file, coluna='Imagem'):
    # Lê o CSV
    df = pd.read_csv(csv_file, encoding='utf-8')
    
    # Conta as linhas onde a coluna está vazia ou apenas com espaços
    linhas_vazias = df[coluna].apply(lambda x: pd.isna(x) or str(x).strip() == "").sum()
    
    print(f"Quantidade de linhas com a coluna '{coluna}' vazia: {linhas_vazias}")
    return linhas_vazias

if __name__ == "__main__":
    # Substitua 'seuarquivo.csv' pelo caminho do seu CSV
    csv_file = r"C:\Users\gabri\Documents\DATA\AnkiCards\csv_final_completo.csv"
    contar_imagens_vazias(csv_file)
