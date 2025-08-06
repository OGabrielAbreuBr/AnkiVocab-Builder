import os
import re
import pandas as pd

def converter_html_para_csv(
    arquivo_html: str,
    csv_saida: str,
) -> None:
    """
    Lê um arquivo HTML que possui 8 colunas separadas por tabulação, no formato:
      0) Palavra
      1) Pronuncia
      2) Texto da Meaning (ex: "Meaning: ...")
      3) Texto da Example (ex: "→ Example: ...")
      4) Áudio da Frente [sound:...]
      5) Áudio do Meaning [sound:...]
      6) Áudio do Example [sound:...]
      7) Tag de imagem (<img src="...">)

    Gera um CSV com colunas:
      Palavra,Pronuncia,Meaning,Example,AudioPalavra,AudioMeaning,AudioExample,Imagem
    """

    # Regex para capturar [sound:arquivo.mp3]
    regex_sound = re.compile(r'\[sound:(.*?)\]', re.IGNORECASE)

    def clean_text(text: str) -> str:
        """Remove tags HTML básicas, &nbsp; e aspas triplas."""
        text = re.sub(r'<.*?>', '', text)
        text = text.replace('&nbsp;', ' ')
        text = text.replace('"""', '')
        return text.strip()

    def remove_prefixes(text: str, prefix_list) -> str:
        """Remove um prefixo do início de 'text' se ele existir."""
        text = text.strip()
        for prefix in prefix_list:
            if text.startswith(prefix):
                return text[len(prefix):].strip()
        return text

    def extract_sound(raw: str) -> str:
        """
        Se houver [sound:arquivo.mp3], retorna só 'arquivo.mp3'.
        Caso contrário, retorna o texto limpo.
        """
        match = regex_sound.search(raw)
        if match:
            return match.group(1).strip()  # só o que está dentro de [sound:...]
        return clean_text(raw)

    # Regex que pega src="conteudo" ou src='conteudo'
    regex_image = re.compile(r'src\s*=\s*([\'"])(.*?)\1', re.IGNORECASE)

    def fix_double_quotes(raw: str) -> str:
        """
        Substitui ocorrências de aspas duplas duplas ("") 
        por uma única aspa dupla ("). Exemplo:
        "<img src=""Cuter.png"">" -> "<img src="Cuter.png">"
        """
        return raw.replace('""', '"')

    def strip_outer_quotes(raw: str) -> str:
        """
        Se a string toda estiver envolta em aspas simples ou duplas, remove-as.
        Exemplo:
        "\"<img src=\"Cuter.png\">\"" -> "<img src=\"Cuter.png\">"
        "'alguma coisa'" -> "alguma coisa"
        """
        raw = raw.strip()
        if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
            raw = raw[1:-1].strip()
        return raw

    def extract_image(raw: str) -> str:
        """
        Converte casos como "<img src=""Cuter.png"">" em "Cuter.png".
        """
        # 1) Substitui "" -> "
        raw = fix_double_quotes(raw)
        # 2) Remove camada externa de aspas se houver
        raw = strip_outer_quotes(raw)
        # 3) Procura src="..." ou src='...'
        match = regex_image.search(raw)
        if match:
            return match.group(2).strip()
        # Se não encontrou tag <img>, retorna texto sem tags
        return re.sub(r'<.*?>', '', raw).strip()



    with open(arquivo_html, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    registros = []
    for line in lines:
        line = line.strip()
        if not line:
            continue  # ignora linhas vazias

        # Divide a linha em 8 colunas
        parts = line.split('\t')
        if len(parts) < 8:
            parts += [''] * (8 - len(parts))

        # Mapeia cada campo
        palavra_raw   = parts[0].strip()
        pronuncia_raw = parts[1].strip()
        meaning_raw   = parts[2].strip()
        example_raw   = parts[3].strip()
        audio_front   = parts[4].strip()
        audio_meaning = parts[5].strip()
        audio_example = parts[6].strip()
        imagem_raw    = parts[7].strip()

        # Remove "Meaning:" e "→ Example:" do início, se houver
        meaning_final = remove_prefixes(meaning_raw, ["Meaning:", "Meaning: "])
        example_final = remove_prefixes(example_raw,  ["→ Example:", "→ Example: "])

        # Extrai nomes do áudio (sem path) e imagem (sem aspas finais)
        audio_palavra_nome = extract_sound(audio_front)
        audio_meaning_nome = extract_sound(audio_meaning)
        audio_example_nome = extract_sound(audio_example)
        imagem_nome        = extract_image(imagem_raw)

        registro = {
            "Palavra":      clean_text(palavra_raw),
            "Pronuncia":    clean_text(pronuncia_raw),
            "Meaning":      clean_text(meaning_final),
            "Example":      clean_text(example_final),
            "AudioPalavra": audio_palavra_nome,
            "AudioMeaning": audio_meaning_nome,
            "AudioExample": audio_example_nome,
            "Imagem":       imagem_nome
        }
        registros.append(registro)

    # Cria DataFrame com as colunas na ordem desejada
    df = pd.DataFrame(registros, columns=[
        "Palavra",
        "Pronuncia",
        "Meaning",
        "Example",
        "AudioPalavra",
        "AudioMeaning",
        "AudioExample",
        "Imagem"
    ])

    # Exporta para CSV (padrão do pandas faz aspas em campos c/ vírgulas)
    df.to_csv(csv_saida, index=False, encoding='utf-8')

    print(f"✅ CSV gerado com {len(df)} linhas em '{csv_saida}'.")
    # Conferência
    df_check = pd.read_csv(csv_saida, encoding='utf-8')
    print("Exemplo das primeiras linhas do CSV:")
    print(df_check.head(5))


# ------------------ Exemplo de uso --------------------
if __name__ == "__main__":
    html_entrada = r"C:\Users\gabri\Documents\DATA\AnkiCards\VocabularioPersonalizado.html"
    csv_saida = "DB_VocabularyPersonalizado.csv"

    converter_html_para_csv(
        arquivo_html=html_entrada,
        csv_saida=csv_saida,
    )
