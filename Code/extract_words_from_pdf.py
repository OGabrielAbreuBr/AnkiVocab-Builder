import PyPDF2
import re
import pandas as pd

def extract_clean_words(pdf_path, start_page, end_page):
    words = []
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(start_page - 1, end_page):
            text = reader.pages[page_num].extract_text()

            # Remover rodapés e cabeçalhos conhecidos
            text = re.sub(r'©Cambridge University Press & Assessment \d{4}', '', text)
            text = re.sub(r'Page \d+ of \d+', '', text)
            text = re.sub(r'A2 Key and A2 Key for Schools', '', text)

            # Remover títulos das seções (Ex.: "Places: Countryside")
            text = re.sub(r'[A-Za-z]+:\s[A-Za-z]+', '', text)

            # Remover parênteses e conteúdo interno
            text = re.sub(r'\([^)]*\)', '', text)

            # Remover hífens e quebras de linha
            text = text.replace('-\n', '').replace('\n', ' ')

            # Capturar somente palavras com mais de uma letra
            page_words = re.findall(r'\b[a-zA-Z]{2,}\b', text)

            words.extend(page_words)

    return words


def remover_palavras_repetidas(csv_entrada, csv_saida):
    # Carregar o CSV original
    df = pd.read_csv(csv_entrada)

    # Remover duplicatas mantendo apenas a primeira ocorrência
    df_sem_duplicatas = df.drop_duplicates(subset=['palavra'])

    # Salvar o resultado em um novo CSV
    df_sem_duplicatas.to_csv(csv_saida, index=False)
    
    print(f"Palavras repetidas removidas. Novo CSV salvo em {csv_saida}")

if __name__ == '__main__':
    # Executando a função
    pdf_path = r'C:\Users\gabri\Documents\DATA\AnkiCards\DB\506886-a2-key-2020-vocabulary-list.pdf'
    words = extract_clean_words(pdf_path, start_page=4, end_page=22)

    # Exportar para CSV
    df = pd.DataFrame(words, columns=['palavra'])
    df.to_csv('palavras_filtradasA2.csv', index=False)

    print("Arquivo CSV criado com sucesso!")

    remover_palavras_repetidas('palavras_filtradasA2.csv', 'palavras_filtradasA2.csv')
