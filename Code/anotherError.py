# import pandas as pd

# # # Carregando os CSVs
# primeiro = r'C:\Users\gabri\Documents\DATA\AnkiCards\csv_final_completo.csv'
# csv1 = pd.read_csv(primeiro)
# segundo = 'resultado_filtrado.csv'
# csv2 = pd.read_csv(segundo)

# # Removendo valores faltantes na coluna do segundo csv para comparação correta
# palavras_csv2 = csv2['Palavra'].dropna().unique()

# # Filtrando o primeiro csv para manter apenas linhas cuja coluna 'palavra' esteja presente no segundo csv
# resultado = csv1[csv1['Palavra'].isin(palavras_csv2)]

# # Salvar o resultado em um novo CSV
# resultado.to_csv('resultado.csv', index=False)

# # # Carregar o CSV
# # df = pd.read_csv('resultado.csv')

# # # Remover linhas onde a coluna 'Example' está vazia (NaN ou em branco)
# # df_filtrado = df[df['Example'].notna() != True]

# # # Salvar o CSV filtrado
# # df_filtrado.to_csv('resultado_filtrado.csv', index=False)


# print("Arquivo 'resultado.csv' criado com sucesso.")
# import pandas as pd

# # Ler os CSVs originais
# primeiro = r'C:\Users\gabri\Documents\DATA\AnkiCards\csv_final_completo.csv'
# df1 = pd.read_csv(primeiro)

# segundo = r'C:\Users\gabri\Documents\DATA\AnkiCards\Inputcsvs\DB_Vocabulary1 copy.csv'
# df2 = pd.read_csv(segundo)

# # Filtrar CSV1: coluna 'Example' NÃO vazia
# df1_filtrado = df1[df1['Example'].notna() & (df1['Example'].astype(str).str.strip() != '')]

# # Filtrar CSV2: coluna 'Example' VAZIA
# df2_filtrado = df2[df2['Example'].isna() | (df2['Example'].astype(str).str.strip() == '')]

# # Identificar palavras em comum com base na coluna 'Palavra'
# palavras_em_comum = set(df1_filtrado['Palavra']).intersection(df2_filtrado['Palavra'])

# # Filtrar df1_filtrado mantendo TODAS as colunas para as palavras em comum
# df_resultado_final = df1_filtrado[df1_filtrado['Palavra'].isin(palavras_em_comum)]

# # Salvar o DataFrame filtrado completo em CSV
# df_resultado_final.to_csv('palavras_em_comum_completo.csv', index=False)

# # Exibir resultado (opcional)
# print(df_resultado_final)

import os
import pandas as pd
from gtts import gTTS
import time

# Função para criar áudio
from gtts import gTTS, gTTSError
import time
import re

def sanitize_filename(filename):
    # Remove caracteres inválidos no Windows
    return re.sub(r'[*?:"<>|]', '_', filename)

def create_audio(text, filename, retries=3, delay=5):
    if pd.isna(text) or not str(text).strip():
        print(f"[AVISO] Texto inválido/vazio, áudio não gerado: '{filename}'")
        return False

    filename = sanitize_filename(filename)
    directory = os.path.dirname(filename)
    os.makedirs(directory, exist_ok=True)

    for attempt in range(1, retries + 1):
        try:
            print(f"   > [AUDIO] Gerando áudio: '{filename}' (Tentativa {attempt}/{retries})")
            tts = gTTS(text=text, lang='en')
            tts.save(filename)
            print(f"     > [SUCESSO] Áudio salvo: '{filename}'")
            return True
        except gTTSError as e:
            print(f"[ERRO] Tentativa {attempt} falhou: {e}")
            if attempt < retries:
                print(f"Aguardando {delay}s antes de tentar novamente...")
                time.sleep(delay)
            else:
                print("[FALHA] Todas as tentativas falharam.")
    return False

# Variáveis
media_dir = r'C:\Users\gabri\Documents\DATA\AnkiCards\Vocabulary1\midias'
csv_path = 'palavras_em_comum_completo.csv'  # CSV gerado anteriormente

print(f"[INICIANDO] Carregando CSV: '{csv_path}'")
# Ler o CSV filtrado
df = pd.read_csv(csv_path)
print(f"[INFO] Total de palavras encontradas no CSV: {len(df)}")

# Iterar sobre as linhas do DataFrame e gerar os áudios
for idx, row in df.iterrows():
    word_fmt = str(row['Palavra']).replace(' ', '_').replace('/', '_').lower()
    print(f"\n[PROCESSANDO] Palavra ({idx+1}/{len(df)}): '{word_fmt}'")

    # Caminhos dos áudios
    audio_meaning_path = os.path.join(media_dir, f"{word_fmt}_meaning.mp3")
    audio_example_path = os.path.join(media_dir, f"{word_fmt}_example.mp3")

    # Gerar áudio para Meaning (sobrescreve se já existir)
    meaning = row.get('Meaning', '')
    if pd.notnull(meaning) and meaning.strip():
        print(f"[MEANING] Texto encontrado, gerando áudio...")
        create_audio(meaning, audio_meaning_path)
    else:
        print(f"[AVISO] Meaning vazio ou nulo para '{word_fmt}', áudio não gerado.")

    # Gerar áudio para Example (sobrescreve se já existir)
    example = row.get('Example', '')
    if pd.notnull(example) and example.strip():
        print(f"[EXAMPLE] Texto encontrado, gerando áudio...")
        create_audio(example, audio_example_path)
    else:
        print(f"[AVISO] Example vazio ou nulo para '{word_fmt}', áudio não gerado.")

print("\n[FINALIZADO] Processo de geração de áudios concluído!")
