from db_client import DBConfig, DBClient
import pandas as pd
import glob
import os
from datetime import datetime, timedelta
from shapely.geometry import Point
import geopandas as gpd

print("Iniciando processo de inserção dos dados no banco de dados")

create_tb = """
CREATE TABLE IF NOT EXISTS public.inmet_ms_utc (
        id SERIAL PRIMARY KEY,
        data DATE NOT NULL,
        hora_utc INT NOT NULL,
        temp_c FLOAT,
        temp_max_c FLOAT,
        temp_min_c FLOAT,
        umid_pct FLOAT,
        umid_max_pct FLOAT,
        umid_min_pct FLOAT,
        pto_orvalho_c FLOAT,
        pto_orvalho_max_c FLOAT,
        pto_orvalho_min_c FLOAT,
        press_hpa FLOAT,
        press_max_hpa FLOAT,
        press_min_hpa FLOAT,
        vento_ms FLOAT,
        dir_vento_ms FLOAT,
        raj_vento_ms FLOAT,
        radiacao_kj_m2 FLOAT,
        chuva_mm FLOAT,
        cod_estacao VARCHAR(50) NOT NULL,
        vl_latitude FLOAT,
        vl_longitude FLOAT,
        data_insercao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
        """

df_bd = pd.read_csv(r"saida\INMET_MS_0800_UTC.csv", sep=";", encoding="utf-8")

pg_local = DBClient(DBConfig.from_env(prefix="LOCAL_POSTGRES"))

pg_local.criar_tabela_bd(table_name="inmet_ms_utc", create_sql=create_tb, schema="public")

pg_local.df_to_table(df_bd, table_name="inmet_ms_utc", schema="public")

print("Processo de inserção dos dados no banco de dados concluído.")