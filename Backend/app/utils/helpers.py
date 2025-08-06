import os
import re
import pandas as pd

def sanitize_filename(filename: str) -> str:
    return re.sub(r'[\\/:"*?<>|]+', '_', filename)

def contar_campos_preenchidos(row: pd.Series) -> int:
    return sum(pd.notna(v) and str(v).strip() != "" for v in row.values)
