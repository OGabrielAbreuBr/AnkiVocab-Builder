import os
import re
import pandas as pd

# EXPRESSÕES REGULARES
regex_word      = re.compile(r"font-size:\s*70px.*>(.*?)<", re.IGNORECASE)
regex_sound     = re.compile(r"\[sound:(.*?)\]", re.IGNORECASE)
regex_pronuncia = re.compile(r"font-size:\s*70px.*>(.*?)<", re.IGNORECASE)
regex_image     = re.compile(r'<img\s+.*?src=""([^""]+)""\s*/?>', re.IGNORECASE)
regex_mean      = re.compile(r"Meaning:\s*(.*)", re.IGNORECASE)
regex_ex        = re.compile(r"Example:\s*(.*)", re.IGNORECASE)

arquivo_html = "4000EssentialEnglish2.html"
csv_saida    = "base_de_dados.csv"
media_dir    = "midias_extraidas"

# Vamos ler o arquivo inteiro como uma lista de linhas
with open(arquivo_html, "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f]

# Preparemos uma lista para guardar nossos registros
registros = []

# Dicionário temporário para preencher
temp = {
    "Palavra": "",
    "AudioPalavra": "",
    "Pronuncia": "",
    "Imagem": "",
    "Meaning": "",
    "Example": "",
    "AudioMeaning": "",
    "AudioExample": ""
}

estado = 0
"""
   Estados (0 a 7) para seguir a ordem:
   0 -> esperando achar 'Palavra'
   1 -> esperando achar 'AudioPalavra'
   2 -> esperando achar 'Pronuncia'
   3 -> esperando achar 'Imagem'
   4 -> esperando achar 'Meaning'
   5 -> esperando achar 'Example'
   6 -> esperando achar 'AudioMeaning'
   7 -> esperando achar 'AudioExample'
   Ao final de 7 -> voltamos ao 0 e salvamos o registro
"""

for line in lines:
    line = line.strip()
    if not line:
        continue  # ignora linha vazia

    # ESTADO 0: Procurando a PALAVRA
    if estado == 0:
        match_w = regex_word.search(line)
        if match_w:
            temp["Palavra"] = match_w.group(1).strip()
            estado = 1  # passa para pronúncia


    # ESTADO 1: Procurando AUDIO PRINCIPAL
    elif estado == 1:
        match_snd = regex_sound.search(line)
        if match_snd:
            snd_name = match_snd.group(1).strip()
            temp["AudioPalavra"] = os.path.join(media_dir, snd_name)
            estado = 2  # passa para a IMAGEM

     # ESTADO 2: Procurando a PRONÚNCIA
    elif estado == 2:
        match_p = regex_pronuncia.search(line)
        if match_p:
            found_text = match_p.group(1).strip()
            # Agora aceitamos mesmo que found_text == temp["Palavra"]
            temp["Pronuncia"] = found_text
            estado = 3      

    # ESTADO 3: Procurando a IMAGEM
    elif estado == 3:
        match_img = regex_image.search(line)
        if match_img:
            img_name = match_img.group(1).strip()
            temp["Imagem"] = os.path.join(media_dir, img_name)
            estado = 4  # passa para Meaning

    # ESTADO 4: Procurando "Meaning:"
    elif estado == 4:
        match_m = regex_mean.search(line)
        if match_m:
            texto = re.sub(r"<.*?>", "", match_m.group(1)).strip()
            temp["Meaning"] = texto
            estado = 5

    # ESTADO 5: Procurando "Example:"
    elif estado == 5:
        match_exm = regex_ex.search(line)
        if match_exm:
            texto = re.sub(r"<.*?>", "", match_exm.group(1)).strip()
            temp["Example"] = texto
            estado = 6

    # ESTADO 6: Procurando AudioMeaning
    elif estado == 6:
        match_snd = regex_sound.search(line)
        if match_snd:
            snd_name = match_snd.group(1).strip()
            if "meaning" in snd_name.lower():
                temp["AudioMeaning"] = os.path.join(media_dir, snd_name)
                estado = 7

    # ESTADO 7: Procurando AudioExample
    elif estado == 7:
        match_snd = regex_sound.search(line)
        if match_snd:
            snd_name = match_snd.group(1).strip()
            if "example" in snd_name.lower():
                temp["AudioExample"] = os.path.join(media_dir, snd_name)
                # Salva o registro
                registros.append(temp.copy())
                # Reseta o temp e volta ao estado 0
                temp = {
                    "Palavra": "",
                    "AudioPalavra": "",
                    "Pronuncia": "",
                    "Imagem": "",
                    "Meaning": "",
                    "Example": "",
                    "AudioMeaning": "",
                    "AudioExample": ""
                }
                estado = 0

# Se sobrou algo incompleto, decida se descarta ou salva parcial
# if temp["Palavra"]:
#    registros.append(temp.copy())

df = pd.DataFrame(registros)

# Ajusta colunas e salva
df = df[
    [
        "Palavra",
        "AudioPalavra",
        "Pronuncia",
        "Imagem",
        "Meaning",
        "Example",
        "AudioMeaning",
        "AudioExample",
    ]
]
df.to_csv(csv_saida, index=False, encoding="utf-8")

print(f"✅ CSV gerado com {len(registros)} registros.")
