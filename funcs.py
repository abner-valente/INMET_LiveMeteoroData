import re
import pandas as pd
from datetime import datetime, timezone, timedelta


def _slugify_filename(name: str) -> str:
    name = name.strip() if isinstance(name, str) else ""
    # Substitui caracteres inválidos no Windows e normaliza espaços
    name = re.sub(r'[\\/*?:"<>|]', '_', name)
    name = re.sub(r'\s+', '_', name)
    # Limita tamanho para evitar problemas de caminho
    return name[:120] or "arquivo"

def mdf_df_estacao(nome_estacao: str, df: pd.DataFrame, df_loc_estacoes: pd.DataFrame, time_delta: int = 0) -> pd.DataFrame:
    if nome_estacao:
        match = re.search(r'\(([SA]\d{3})\)', nome_estacao)
        if match:
            cod_estacao = match.group(1)
            df['cod_estacao'] = cod_estacao
            
        #renomeando colunas
        df.rename(columns ={"Data": "data",
                            "Hora (UTC)": "hora_utc",
                            "Temp. Ins. (C)": "temp_c",
                            "Temp. Max. (C)": "temp_max_c",
                            "Temp. Min. (C)": "temp_min_c",
                            "Umi. Ins. (%)": "umid_pct",
                            "Umi. Max. (%)": "umid_max_pct",
                            "Umi. Min. (%)": "umid_min_pct",
                            "Pto Orvalho Ins. (C)": "pto_orvalho_c",
                            "Pto Orvalho Max. (C)": "pto_orvalho_max_c",
                            "Pto Orvalho Min. (C)": "pto_orvalho_min_c",
                            "Pressao Ins. (hPa)": "press_hpa",
                            "Pressao Max. (hPa)": "press_max_hpa",
                            "Pressao Min. (hPa)": "press_min_hpa",
                            "Vel. Vento (m/s)": "vento_ms",
                            "Raj. Vento (m/s)": "raj_vento_ms",
                            "Dir. Vento (m/s)" : "dir_vento_ms",
                            "Radiacao (KJ/m²)": "radiacao_kj_m2",
                            "Chuva (mm)": "chuva_mm",}, 
                    inplace = True)
        
        # Fazendo merge com df_loc_estacoes para pegar latitude e longitude
        if 'cod_estacao' in df.columns and 'CD_ESTACAO' in df_loc_estacoes.columns:
            df = df.merge(
                df_loc_estacoes[['CD_ESTACAO', 'VL_LATITUDE', 'VL_LONGITUDE']],
                left_on='cod_estacao',
                right_on='CD_ESTACAO',
                how='left'
            )
            # Remove a coluna CD_ESTACAO duplicada (já temos cod_estacao)
            df.drop(columns=['CD_ESTACAO'], inplace=True, errors='ignore')
        
        # Padronizando hora_utc para 4 dígitos (0900, 0500, etc)
        if 'hora_utc' in df.columns:
            df['hora_utc'] = df['hora_utc'].astype(str).str.zfill(4)
        
        # Filtrando apenas registros onde hora_utc = agora (considerando time_delta)
        hora_utc = datetime.now(timezone.utc) - timedelta(hours=time_delta)
        agora = hora_utc.strftime('%H') + '00'
        
        if 'hora_utc' in df.columns:
            df = df[df['hora_utc'] == agora]
                    
        
    return df
