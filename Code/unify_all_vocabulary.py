# AIzaSyDftyiA6kLbg0iV2AhiRqBjyEsprYou98c
# AIzaSyAOvI7lvzRVcNIMx6-WQXPDgxviyeDUiTI
# AIzaSyAOOOO2oc8OlPaMPNLD3Gb-4a40s1aIJW8
# AIzaSyA9eeeBHFOMj2-LG2tCe2PnuTH9LxmlTUc

import os
import time
import re
import pandas as pd
from gtts import gTTS
import eng_to_ipa as ipa
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# Configure sua API key do Google
genai.configure(api_key='')

model = genai.GenerativeModel("gemini-2.0-flash")

media_dir = r'C:\Users\gabri\Documents\DATA\AnkiCards\Vocabulary1\midias'
input_csv_dir = r'C:\Users\gabri\Documents\DATA\AnkiCards\inputcsvs'
output_csv_file = r'C:\Users\gabri\Documents\DATA\AnkiCards\csv_final_completo copy 2.csv'

# -------------------------------------------------------
#                FUNÇÕES AUXILIARES
# -------------------------------------------------------

def sanitize_filename(filename):
    """
    Remove caracteres inválidos de um nome de arquivo,
    substituindo-os por underline.
    """
    return re.sub(r'[\\/:"*?<>|]+', '_', filename)

def get_meaning_and_example(word, retries=3, delay=60):
    prompt = f"""
    Estou criando cards de vocabulário no Anki. Quando eu der uma palavra, gere o significado e um exemplo,
    usando como base o formato abaixo:

    Input: Apart

    Meaning: When people or things are apart, they are not next to each other.
    → Example: They moved apart and then came back together.

    Agora gere para esta palavra:
    Input: {word}

    Apenas retorne Meaning e Example, mantendo o mesmo formato.
    """
    print(f"   > [Gemini] Obtendo Meaning/Example para: '{word}' (tentativas={retries}, delay={delay}s)")
    attempt = 0
    while attempt < retries:
        try:
            response = model.generate_content(prompt)
            if response and hasattr(response, "text"):
                lines = response.text.strip().split('\n')
                meaning = lines[0].replace("Meaning:", "").strip() if len(lines) > 0 else ""
                example = lines[1].replace("→ Example:", "").strip() if len(lines) > 1 else ""
                print(f"   > [Gemini] Sucesso: Meaning='{meaning[:50]}...', Example='{example[:50]}...'")
                return meaning, example
            else:
                print("   > [Gemini] Resposta vazia ou inválida.")
                return "", ""
        except ResourceExhausted:
            attempt += 1
            print(f"   > [Gemini] Quota excedida. Aguardando {delay}s... (tentativa {attempt}/{retries})")
            time.sleep(delay)

    print(f"   > [Gemini] ❌ Tentativas esgotadas para '{word}'. Meaning/Example não obtidos.")
    exit()

def get_cefr_level(word, retries=3, delay=60):
    """
    Obtém o nível CEFR para a palavra utilizando a API da Gemini,
    implementando retries em caso de quota excedida.
    """
    prompt = (
        f"Diga apenas o nível CEFR (A1, A2, B1, B2, C1 ou C2) mais apropriado para a palavra '{word}'. "
        "Não escreva mais nada além do nível."
    )
    config = {"temperature": 0.2, "top_p": 1, "top_k": 1, "max_output_tokens": 10}
    
    print(f"   > [Gemini] Obtendo CEFR para: '{word}'")
    attempt = 0
    while attempt < retries:
        try:
            response = model.generate_content(prompt, generation_config=config)
            text = response.text.strip().upper() if (response and hasattr(response, "text")) else ""
            valid_levels = {"A1", "A2", "B1", "B2", "C1", "C2"}
            if text in valid_levels:
                print(f"   > [Gemini] CEFR para '{word}': {text}")
                return text
            else:
                print(f"   > [Gemini] CEFR inválido ou não retornado para '{word}'.")
                return ""
        except ResourceExhausted:
            attempt += 1
            print(f"   > [Gemini] Quota excedida ao obter CEFR para '{word}'. Aguardando {delay}s... (tentativa {attempt}/{retries})")
            time.sleep(delay)
    print(f"   > [Gemini] ❌ Tentativas esgotadas para '{word}'. CEFR não obtido.")
    exit()


def create_audio(text, filename):
    if pd.isnull(text):
        return ""
    text = str(text).strip()
    if not text:
        return ""
    
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    
    print(f"   > [AUDIO] Gerando áudio: '{filename}' (texto: '{text[:50]}...')")
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    return filename

def transcrever_fonetica(texto):
    if not texto or pd.isnull(texto):
        return ""
    return ipa.convert(str(texto))

def encontrar_imagem(palavra, media_dir):
    formatos = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
    palavra_formatada = str(palavra).replace(" ", "_").lower()
    for ext in formatos:
        filename = f"{palavra_formatada}.{ext}"
        caminho = os.path.join(media_dir, filename)
        if os.path.exists(caminho):
            return filename
    return ""

def contar_campos_preenchidos(row):
    return sum(pd.notna(v) and str(v).strip() != "" for v in row.values)

# -------------------------------------------------------
#           FASE 1: Importar sem IA nem áudio
# -------------------------------------------------------
def fase1_importar_apenas(input_dir, output_csv, colunas):
    """
    1. Carrega ou cria o CSV final,
    2. Lê todos os CSVs do 'input_dir',
       - Para cada linha, retira o caminho completo nas colunas de mídia,
         deixando só o nome do arquivo (ex: 'apart.mp3', 'img.png').
       - Mescla esses dados no consolidado_dict
    3. Salva df_result no 'output_csv' sem gerar IA ou áudios.
    """
    print("\n=== FASE 1: Importar e limpar caminhos de mídia ===")

    if os.path.exists(output_csv):
        df_final = pd.read_csv(output_csv, encoding='utf-8')
        df_final = df_final.drop_duplicates(subset='Palavra', keep='first')
        print(f"   [FASE 1] CSV final encontrado: {output_csv} (duplicatas removidas).")
    else:
        df_final = pd.DataFrame(columns=colunas)
        print("   [FASE 1] Novo CSV final criado (vazio).")

    consolidado_dict = df_final.set_index('Palavra').to_dict(orient='index')
    for palavra, dados in consolidado_dict.items():
        dados['Palavra'] = palavra

    media_cols = ["AudioPalavra", "AudioMeaning", "AudioExample", "Imagem"]

    arquivos = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    print(f"   [FASE 1] Encontrados {len(arquivos)} CSVs em '{input_dir}'.")
    for arquivo in arquivos:
        print(f"\n   [FASE 1] Lendo arquivo: {arquivo}")
        caminho = os.path.join(input_dir, arquivo)
        df_temp = pd.read_csv(caminho, encoding='utf-8')

        df_temp.columns = df_temp.columns.str.strip()

        for idx, row in df_temp.iterrows():
            raw_word = row.get('Palavra', "")
            if pd.isnull(raw_word):
                raw_word = ""
            word = str(raw_word).strip()
            if not word:
                continue

            # Limpar caminhos completos nas colunas de mídia
            for mcol in media_cols:
                val = row.get(mcol, "")
                val = str(val).strip()
                val_basename = os.path.basename(val)
                row[mcol] = val_basename if val_basename else ""

            entry_existente = consolidado_dict.get(word, {})
            filled_existente = sum(bool(str(entry_existente.get(c, '')).strip()) for c in entry_existente)
            filled_novo = contar_campos_preenchidos(row)

            if word in consolidado_dict:
                if filled_novo > filled_existente:
                    consolidado_dict[word] = row.to_dict()
            else:
                consolidado_dict[word] = row.to_dict()

        print(f"   [FASE 1] -> Processado '{arquivo}'. Tamanho parcial do dicionário: {len(consolidado_dict)} palavras.")

    df_result = pd.DataFrame(consolidado_dict.values())
    df_result = df_result[colunas]
    df_result.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"✅ [FASE 1] CSV final salvo em '{output_csv}' com caminho removido das colunas de mídia.")
    return df_result

# -------------------------------------------------------
#           FASE 2: Completar (IA + áudios)
# -------------------------------------------------------
def fase2_gerar_campos_e_audios(df_final, output_csv, media_dir, colunas):
    """
    Executa a Fase 2:
      1. Para cada palavra no DataFrame (df_final), atualiza os campos que estiverem faltando:
         - Se 'Meaning' ou 'Example' estiverem vazios, chama a IA para gerar os dados.
         - Se 'Pronuncia' estiver vazia, gera a transcrição IPA.
         - Se 'CEFR' estiver vazio, consulta a IA para determinar o nível.
         - Gera ou atualiza os áudios correspondentes para 'Palavra', 'Meaning' e 'Example':
              * Se o arquivo de áudio já existir na pasta, atualiza o campo com seu nome.
              * Caso contrário, gera o áudio e atualiza o campo.
         - Verifica se há uma imagem já existente na pasta e atualiza o campo 'Imagem' se encontrado.
      2. Ao final de cada iteração, o CSV é regravado com os dados atualizados.
      3. Utiliza um arquivo externo ("last_index.txt") para retomar a execução a partir do último índice processado.
    """

    print("\n=== FASE 2: Gerar IA, áudios e atualizar mídia onde faltam ===")
    
    # Remove duplicatas na coluna 'Palavra' para garantir índice único
    df_final = df_final.drop_duplicates(subset='Palavra', keep='first')
    consolidado_dict = df_final.set_index('Palavra').to_dict(orient='index')

    total = len(consolidado_dict)
    print(f"   [FASE 2] Total de {total} palavras a processar...")

    # Define o arquivo que guarda o último índice processado
    last_index_file = "last_index.txt"
    start_index = 0
    if os.path.exists(last_index_file):
        try:
            with open(last_index_file, "r") as f:
                start_index = int(f.read().strip())
            print(f"Retomando a partir do índice: {start_index}")
        except Exception as e:
            print(f"Não foi possível ler o índice do arquivo ({e}). Iniciando do índice 0.")
            start_index = 0
    else:
        print("Iniciando a partir do índice 0.")

    # Converte o dicionário em uma lista de itens para iterar de forma ordenada
    items = list(consolidado_dict.items())

    # Itera a partir do índice armazenado
    for idx, (palavra, entry) in enumerate(items, start=0):
        if idx < start_index:
            continue

        if pd.isnull(palavra):
            palavra = ""
        palavra = str(palavra).strip()
        if not palavra:
            # Mesmo se a palavra estiver vazia, atualiza o índice e continua
            with open(last_index_file, "w") as f:
                f.write(str(idx + 1))
            continue

        print(f"\n   [FASE 2] ({idx + 1}/{total}) Processando palavra: '{palavra}'")
        
        # Cria word_fmt a partir da palavra e sanitiza para garantir um nome de arquivo válido
        word_fmt = sanitize_filename(palavra.replace(" ", "_").lower())

        meaning = str(entry.get('Meaning', "")).strip()
        example = str(entry.get('Example', "")).strip()
        pronuncia = str(entry.get('Pronuncia', "")).strip()
        cefr = str(entry.get('CEFR', "")).strip()

        if (not meaning or meaning == 'nan') or (not example or example == 'nan'):
            print("     > Meaning/Example não existentes. Chamando IA...")
            new_m, new_e = get_meaning_and_example(palavra)
            if new_m:
                meaning = new_m
                entry['Meaning'] = meaning
            if new_e:
                example = new_e
                entry['Example'] = example

            # --- ÁUDIO DO MEANING Para novo Meaning e Exaple---
            audio_meaning_name = f"{word_fmt}_meaning.mp3"
            audio_meaning_path = os.path.join(media_dir, audio_meaning_name)
            if meaning:
                create_audio(meaning, audio_meaning_path)
                entry['AudioMeaning'] = audio_meaning_name

            # --- ÁUDIO DO EXAMPLE ---
            audio_example_name = f"{word_fmt}_example.mp3"
            audio_example_path = os.path.join(media_dir, audio_example_name)
            if example:
                create_audio(example, audio_example_path)
                entry['AudioExample'] = audio_example_name
            

        if not pronuncia or pronuncia == '' or pronuncia == 'nan':
            print("     > Pronúncia vazia, gerando IPA...")
            prn = transcrever_fonetica(palavra)
            entry['Pronuncia'] = prn
            print(f"     > Pronúncia: {prn}")

        if not cefr or cefr == '' or cefr == 'nan':
            print("     > CEFR vazio, consultando IA...")
            niv = get_cefr_level(palavra)
            if niv:
                entry['CEFR'] = niv
                print(f"     > CEFR: {niv}")

        # --- ÁUDIO DA PALAVRA ---
        audio_palavra_name = f"{word_fmt}.mp3"
        audio_palavra_path = os.path.join(media_dir, audio_palavra_name)
        if palavra:
            if os.path.exists(audio_palavra_path):
                entry['AudioPalavra'] = audio_palavra_name
                print(f"     > Áudio da palavra existente: {audio_palavra_name}")
            else:
                created = create_audio(palavra, audio_palavra_path)
                if created:
                    entry['AudioPalavra'] = audio_palavra_name

        # --- ÁUDIO DO MEANING ---
        audio_meaning_name = f"{word_fmt}_meaning.mp3"
        audio_meaning_path = os.path.join(media_dir, audio_meaning_name)
        if meaning:
            if os.path.exists(audio_meaning_path):
                entry['AudioMeaning'] = audio_meaning_name
                print(f"     > Áudio do Meaning existente: {audio_meaning_name}")
            else:
                create_audio(meaning, audio_meaning_path)
                entry['AudioMeaning'] = audio_meaning_name

        # --- ÁUDIO DO EXAMPLE ---
        audio_example_name = f"{word_fmt}_example.mp3"
        audio_example_path = os.path.join(media_dir, audio_example_name)
        if example:
            if os.path.exists(audio_example_path):
                entry['AudioExample'] = audio_example_name
                print(f"     > Áudio do Example existente: {audio_example_name}")
            else:
                create_audio(example, audio_example_path)
                entry['AudioExample'] = audio_example_name

        # --- IMAGEM ---
        imagem_atual = str(entry.get('Imagem', "")).strip()
        if imagem_atual:
            base_img = os.path.basename(imagem_atual)
            if base_img != imagem_atual:
                entry['Imagem'] = base_img
        else:
            print("     > Nenhuma imagem setada, procurando no disco...")
            found_img = encontrar_imagem(palavra, media_dir)
            if found_img:
                entry['Imagem'] = found_img
                print(f"     > Imagem encontrada: {found_img}")

        entry['Palavra'] = palavra
        consolidado_dict[palavra] = entry

        # Atualiza o CSV após cada iteração
        lista_registros = [{'Palavra': chave, **dados} for chave, dados in consolidado_dict.items()]
        df_atualizado = pd.DataFrame(lista_registros)
        df_atualizado = df_atualizado[colunas]
        df_atualizado.to_csv(output_csv, index=False, encoding='utf-8')
        print(f"✅ [FASE 2] CSV atualizado: {output_csv}")

        # Atualiza o arquivo de índice com o último índice processado
        with open(last_index_file, "w") as f:
            f.write(str(idx + 1))

def fase3_gerar_novas_palavras(novos_csv, main_csv, media_dir):
    """
    FASE 3: Integra novas palavras do CSV 'novos_csv' ao CSV principal ('main_csv')
    e preenche os campos faltantes (Meaning, Example, Pronúncia, CEFR, áudios, Imagem).
    
    Antes da integração, os dados do novo CSV são tratados:
      - Todos os textos são convertidos para minúsculas;
      - Remoção de espaços em excesso nas extremidades;
      - Registros com a palavra (campo "Palavra") contendo mais de 8 palavras são ignorados.
    
    Se a palavra já existir no CSV principal, ela será ignorada.
    Ao final, todas as palavras são ordenadas alfabeticamente no CSV.
    """
    colunas = [
        'Palavra', 'AudioPalavra', 'Pronuncia', 'Imagem', 'Meaning',
        'Example', 'AudioMeaning', 'AudioExample', 'CEFR'
    ]
    
    print("=== FASE 3: Integração de novas palavras e complementação de campos ===")
    
    # Lê o CSV de novas palavras
    try:
        df_novos = pd.read_csv(novos_csv, encoding='utf-8')
        print(f"   > CSV de novas palavras lido: {novos_csv} (total: {len(df_novos)} registros)")
    except Exception as e:
        print(f"Erro ao ler o CSV de novas palavras: {e}")
        return

    # Tratamento dos dados: converte para minúsculas e remove espaços em excesso em todas as colunas de texto
    for col in df_novos.select_dtypes(include=['object']).columns:
        df_novos[col] = df_novos[col].apply(lambda x: x.strip().lower() if isinstance(x, str) else x)
    
    # Valida o campo "Palavra": ignora registros que tenham mais de 8 palavras
    df_novos = df_novos[df_novos['Palavra'].apply(lambda x: len(x.split()) <= 8)]
    print(f"   > Registros após validação da quantidade de palavras na coluna 'Palavra': {len(df_novos)}")
    
    # Define as colunas de mídia e garante que existam no df_novos
    media_cols = ["AudioPalavra", "AudioMeaning", "AudioExample", "Imagem"]
    for mcol in media_cols:
        if mcol not in df_novos.columns:
            df_novos[mcol] = ""
        else:
            df_novos[mcol] = df_novos[mcol].apply(lambda x: os.path.basename(str(x)) if pd.notnull(x) else "")
    
    # Lê o CSV principal ou cria um DataFrame vazio se não existir
    if os.path.exists(main_csv):
        df_main = pd.read_csv(main_csv, encoding='utf-8')
        print(f"   > CSV principal encontrado: {main_csv} (total: {len(df_main)} registros)")
    else:
        df_main = pd.DataFrame(columns=colunas)
        print("   > CSV principal não encontrado. Será criado um novo.")

    # Cria um dicionário com as palavras do CSV principal (chave: 'Palavra')
    main_dict = df_main.set_index('Palavra').to_dict(orient='index')
    
    # Mescla as novas palavras no dicionário principal,
    # ignorando as palavras que já existem
    for idx, row in df_novos.iterrows():
        palavra = str(row.get('Palavra', "")).strip()
        if not palavra:
            continue
        if palavra in main_dict:
            print(f"   > Palavra '{palavra}' já existe no CSV principal. Ignorando nova entrada.")
            continue
        main_dict[palavra] = row.to_dict()
    
    print(f"   > Mesclagem concluída. Total de palavras consolidadas: {len(main_dict)}")

    total = len(main_dict)
    # Itera sobre cada palavra para preencher os campos faltantes
    for i, (palavra, entry) in enumerate(main_dict.items(), start=1):
        print(f"\n   [FASE 3] ({i}/{total}) Processando palavra: '{palavra}'")
        word_fmt = sanitize_filename(palavra.replace(" ", "_").lower())
        
        meaning = str(entry.get('Meaning', "")).strip()
        example = str(entry.get('Example', "")).strip()
        pronuncia = str(entry.get('Pronuncia', "")).strip()
        cefr = str(entry.get('CEFR', "")).strip()
        
        # Se Meaning ou Example estiverem vazios, chama a IA para gerar os dados
        if not meaning or meaning == 'nan' or not example or example == 'nan':
            print("     > Meaning/Example faltando. Chamando IA...")
            new_meaning, new_example = get_meaning_and_example(palavra)
            if new_meaning:
                meaning = new_meaning
                entry['Meaning'] = meaning
            if new_example:
                example = new_example
                entry['Example'] = example

            # Gera os áudios para Meaning e Example
            audio_meaning_name = f"{word_fmt}_meaning.mp3"
            audio_meaning_path = os.path.join(media_dir, audio_meaning_name)
            if meaning:
                create_audio(meaning, audio_meaning_path)
                entry['AudioMeaning'] = audio_meaning_name

            audio_example_name = f"{word_fmt}_example.mp3"
            audio_example_path = os.path.join(media_dir, audio_example_name)
            if example:
                create_audio(example, audio_example_path)
                entry['AudioExample'] = audio_example_name

        # Se Pronúncia estiver vazia, gera a transcrição IPA
        if not pronuncia or pronuncia == 'nan':
            print("     > Pronúncia faltando. Gerando IPA...")
            prn = transcrever_fonetica(palavra)
            entry['Pronuncia'] = prn
            print("     > Pronúncia gerada:", prn)
        
        # Se CEFR estiver vazio, consulta a IA para determinar o nível
        if not cefr or cefr == 'nan':
            print("     > CEFR faltando. Consultando IA...")
            niv = get_cefr_level(palavra)
            if niv:
                entry['CEFR'] = niv
                print("     > CEFR definido:", niv)
        
        # ÁUDIO DA PALAVRA
        audio_palavra_name = f"{word_fmt}.mp3"
        audio_palavra_path = os.path.join(media_dir, audio_palavra_name)
        if os.path.exists(audio_palavra_path):
            entry['AudioPalavra'] = audio_palavra_name
            print("     > Áudio da palavra já existe:", audio_palavra_name)
        else:
            create_audio(palavra, audio_palavra_path)
            entry['AudioPalavra'] = audio_palavra_name

        # Gera os áudios para Meaning e Example
            audio_meaning_name = f"{word_fmt}_meaning.mp3"
            audio_meaning_path = os.path.join(media_dir, audio_meaning_name)
            if meaning:
                create_audio(meaning, audio_meaning_path)
                entry['AudioMeaning'] = audio_meaning_name

            audio_example_name = f"{word_fmt}_example.mp3"
            audio_example_path = os.path.join(media_dir, audio_example_name)
            if example:
                create_audio(example, audio_example_path)
                entry['AudioExample'] = audio_example_name

        
        # Verifica se há imagem; se estiver ausente, procura no disco
        imagem_atual = str(entry.get('Imagem', "")).strip()
        if not imagem_atual or imagem_atual == 'nan':
            print("     > Imagem faltando. Procurando no disco...")
            found_img = encontrar_imagem(palavra, media_dir)
            if found_img:
                entry['Imagem'] = found_img
                print("     > Imagem encontrada:", found_img)
        else:
            base_img = os.path.basename(imagem_atual)
            if base_img != imagem_atual:
                entry['Imagem'] = base_img

    # Converte o dicionário consolidado em DataFrame
    lista_registros = [{'Palavra': key, **value} for key, value in main_dict.items()]
    df_final = pd.DataFrame(lista_registros)
    df_final = df_final[colunas]

    # Ordena alfabeticamente pelas palavras
    # df_final = df_final.sort_values(by='Palavra').reset_index(drop=True)
    
    df_final.to_csv(main_csv, index=False, encoding='utf-8')
    print("\n✅ [FASE 3] CSV principal atualizado com novas palavras (duplicatas ignoradas) e campos preenchidos, ordenado alfabeticamente.")

# -------------------------------------------------------
#        Função principal que orquestra Fase 1, 2 e 3
# -------------------------------------------------------
def consolidar_csv(input_dir, output_csv):
    colunas = [
        'Palavra','AudioPalavra','Pronuncia','Imagem','Meaning',
        'Example','AudioMeaning','AudioExample','CEFR'
    ]
    print("=== Iniciando consolidar_csv() ===")

    # FASE 1: importa e "limpa" caminhos de mídia
    df_apos_fase1 = fase1_importar_apenas(input_dir, output_csv, colunas)

    # FASE 2: gera IA e áudios apenas para o que estiver faltando
    #fase2_gerar_campos_e_audios(df_apos_fase1, output_csv, media_dir, colunas)

    print("=== Processo completo. ===")

def executar_fase1(input_dir, output_csv):
    """
    Executa a Fase 1: Importa os CSVs de 'input_dir', limpa os caminhos completos
    nas colunas de mídia e consolida os dados no CSV final.
    """
    colunas = [
        'Palavra', 'AudioPalavra', 'Pronuncia', 'Imagem', 'Meaning',
        'Example', 'AudioMeaning', 'AudioExample', 'CEFR'
    ]
    print("=== Executando Fase 1: Importar e limpar caminhos de mídia ===")
    df_final = fase1_importar_apenas(input_dir, output_csv, colunas)
    print("=== Fase 1 concluída. CSV salvo em:", output_csv)
    return df_final

def executar_fase2(output_csv, media_dir):
    """
    Executa a Fase 2: A partir do CSV gerado na Fase 1, atualiza os campos que estiverem
    faltando (Meaning, Example, CEFR, etc.) e gera os áudios correspondentes.
    """
    colunas = [
        'Palavra', 'AudioPalavra', 'Pronuncia', 'Imagem', 'Meaning',
        'Example', 'AudioMeaning', 'AudioExample', 'CEFR'
    ]
    print("=== Executando Fase 2: Gerar IA e áudios ===")
    try:
        df_final = pd.read_csv(output_csv, encoding='utf-8')
    except Exception as e:
        print(f"Erro ao carregar CSV: {e}")
        return

    fase2_gerar_campos_e_audios(df_final, output_csv, media_dir, colunas)
    print("=== Fase 2 concluída. CSV atualizado em:", output_csv)

def executar_fase3(novos_csv, main_csv, media_dir):
    """
    Função que encapsula a execução da Fase 3.
    """
    fase3_gerar_novas_palavras(novos_csv, main_csv, media_dir)

if __name__ == "__main__":
    # consolidar_csv(input_csv_dir, output_csv_file)

    #df = executar_fase1(input_csv_dir, output_csv_file)

    executar_fase2(output_csv_file, media_dir)

    novos_csv_path = r'C:\Users\gabri\Documents\DATA\AnkiCards\featureDB.csv'
    main_csv_path = r'C:\Users\gabri\Documents\DATA\AnkiCards\csv_final_completo copy 2.csv'

    # executar_fase3(novos_csv_path, main_csv_path, media_dir)
