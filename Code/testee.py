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
        palavra = linha[0].strip()
        
        # Atualiza o campo AudioPalavra
        pasta_audio = linha[1].rsplit("\\", 1)[0]
        linha[1] = f"{pasta_audio}\\{palavra}.mp3"
        
        # Atualiza o campo Imagem
        pasta_imagem = linha[3].rsplit("\\", 1)[0]
        linha[3] = f"{pasta_imagem}\\{palavra}.jpg"
        
        # Atualiza o campo AudioMeaning
        pasta_audio_meaning = linha[6].rsplit("\\", 1)[0]
        linha[6] = f"{pasta_audio_meaning}\\{palavra}_meaning.mp3"
        
        # Atualiza o campo AudioExample
        pasta_audio_example = linha[7].rsplit("\\", 1)[0]
        linha[7] = f"{pasta_audio_example}\\{palavra}_example.mp3"

    # Sobrescreve o CSV com os novos dados
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(linhas)

# Exemplo de uso:
altera_csv("4000 Essential English Words\db.csv")
