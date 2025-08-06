import os
import pandas as pd
from core.config import settings
from utils.helpers import contar_campos_preenchidos

COLUNAS = [
    'Palavra','AudioPalavra','Pronuncia','Imagem','Meaning',
    'Example','AudioMeaning','AudioExample','CEFR'
]

def importar_e_limpar_paths() -> pd.DataFrame:
    """
    Lê todos os CSVs em input_csv_dir, retira paths completos nas colunas de mídia,
    consolida num único DataFrame e salva em output_csv_file.
    """
    out_csv = settings.output_csv_file
    if os.path.exists(out_csv):
        df_final = pd.read_csv(out_csv, encoding='utf-8').drop_duplicates(subset='Palavra')
    else:
        df_final = pd.DataFrame(columns=COLUNAS)

    consolidado = df_final.set_index('Palavra').to_dict(orient='index')

    for nome in os.listdir(settings.input_csv_dir):
        if not nome.lower().endswith('.csv'):
            continue
        df = pd.read_csv(os.path.join(settings.input_csv_dir, nome), encoding='utf-8')
        df.columns = df.columns.str.strip()
        for _, row in df.iterrows():
            palavra = str(row.get('Palavra', '')).strip()
            if not palavra:
                continue
            # só o basename das mídias
            for mcol in ["AudioPalavra","AudioMeaning","AudioExample","Imagem"]:
                val = row.get(mcol, "")
                row[mcol] = os.path.basename(str(val).strip()) if pd.notnull(val) else ""
            existing = consolidado.get(palavra, {})
            if (palavra not in consolidado
                or contar_campos_preenchidos(row) > contar_campos_preenchidos(pd.Series(existing))):
                consolidado[palavra] = row.to_dict()

    df_out = pd.DataFrame([{'Palavra':k, **v} for k,v in consolidado.items()])[COLUNAS]
    df_out.to_csv(out_csv, index=False, encoding='utf-8')
    return df_out
