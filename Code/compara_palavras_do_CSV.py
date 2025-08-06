import csv

def gerar_csv_comum(csv1_path, csv2_path, output_csv_path):
    # Lê o primeiro CSV e extrai os dados e as palavras da coluna "Palavra"
    with open(csv1_path, newline='', encoding='utf-8') as file1:
        reader1 = csv.DictReader(file1)
        dados1 = list(reader1)
        palavras1 = {row['Palavra'].strip() for row in dados1}

    # Lê o segundo CSV e extrai as palavras da coluna "Palavra"
    with open(csv2_path, newline='', encoding='utf-8') as file2:
        reader2 = csv.DictReader(file2)
        dados2 = list(reader2)
        palavras2 = {row['Palavra'].strip() for row in dados2}

    # Determina as palavras que são comuns a ambos os CSVs
    palavras_comum = palavras1.intersection(palavras2)

    # Filtra as linhas do primeiro CSV onde a coluna "Palavra" está na interseção
    dados_comum = [row for row in dados1 if row['Palavra'].strip() in palavras_comum]

    # Escreve o CSV de saída com as linhas em comum
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=reader1.fieldnames)
        writer.writeheader()
        writer.writerows(dados_comum)

# Exemplo de uso:
gerar_csv_comum(r'C:\Users\gabri\Documents\DATA\AnkiCards\db_atualizado.csv', r'C:\Users\gabri\Documents\DATA\AnkiCards\Inputcsvs\1000words.csv', r'C:\Users\gabri\Documents\DATA\AnkiCards\teste_DB\palavras_filtradas1000.csv')
