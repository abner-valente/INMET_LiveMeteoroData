import time
import tqdm
import os
import shutil
import glob
import geopandas as gpd
from shapely.geometry import Point
from funcs import _slugify_filename, mdf_df_estacao
from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError
from datetime import datetime, timedelta
import logging
from playwright.sync_api import sync_playwright, TimeoutError
import pandas as pd

from db_client import DBConfig, DBClient


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

##############################################################################
# CONFIGURAÇÕES INICIAIS
##############################################################################


# Configurar logger para escrever apenas em arquivo (sem console)
pasta_log = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(pasta_log, exist_ok=True)

logger = logging.getLogger()
logger.handlers.clear()  # Remove handlers padrão
file_handler = logging.FileHandler(os.path.join(pasta_log, 'automation_log.log'))
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


URL = "https://tempo.inmet.gov.br/TabelaEstacoes/"


# Criação de pastas do projeto
try:
    logging.info("Criando pastas do projeto")
    pasta_downloads = os.path.join(os.path.dirname(__file__), "downloads")    
    pasta_saida = os.path.join(os.path.dirname(__file__), "saida")

    os.makedirs(pasta_downloads, exist_ok=True)
    os.makedirs(pasta_saida, exist_ok=True)

    #apagar arquivos antigos da pasta downloads
    logging.info("Limpando pasta de downloads")
    for nome in os.listdir(pasta_downloads):
        caminho = os.path.join(pasta_downloads, nome)
        if os.path.isfile(caminho) or os.path.islink(caminho):
            os.remove(caminho)
        elif os.path.isdir(caminho):
            shutil.rmtree(caminho)
except Exception as e:
    logging.error(f"Erro ao criar pastas do projeto ou apagar arquivos antigos: {e}")
    print("Erro ao criar pastas do projeto. Verifique as permissões de escrita no diretório.")
    exit()

# Validando metadados das Estações
try:
    df_loc_estacoes = pd.read_csv("loc_estacoes.csv", encoding='utf-8', sep=';')
    cod_estacao_map = dict(zip(df_loc_estacoes['CD_ESTACAO'], df_loc_estacoes['DC_NOME']))
    logging.info(f"Arquivo loc_estacoes.csv carregado com sucesso. {len(cod_estacao_map)} estações mapeadas.")
except Exception as e:
    logging.error(f"Erro ao carregar loc_estacoes.csv: {e}")
    print("Erro ao carregar loc_estacoes.csv. Verifique se o arquivo existe e está no formato correto.")
    exit()

##############################################################################
# PROCESSO DE AUTOMATIZAÇÃO COM PLAYWRIGHT
##############################################################################

with sync_playwright() as p:
        
    logging.info("Iniciando o navegador")
    navegador = p.chromium.launch(headless=False)
    pagina = navegador.new_page()
    pagina.goto(URL)
    logging.info(f"Acessou a URL: {URL}")
    
    try:
        pagina.click('//*[@id="root"]/div[1]/div[1]/i') #Clicar pra abrir a lista da esquerda
        pagina.click('//*[@id="root"]/div[2]/div[1]/div[2]/div[1]/button[1]') #Selecionar Estações Automáticas
        pagina.click('//*[@id="root"]/div[2]/div[1]/div[2]/div[2]/input') #clicar para abrir opções de estado    
        time.sleep(1)

        pagina.click('//*[@id="root"]/div[2]/div[1]/div[2]/div[2]/div[2]/div[13]')#selecionar o estado de MS
        time.sleep(1)
        
        pagina.click('//*[@id="root"]/div[2]/div[1]/div[2]/div[3]/input')#clicar para abrir opções de estação
        time.sleep(1)
        
        estacoes = pagina.locator('//*[@id="root"]/div[2]/div[1]/div[2]/div[3]/div[2]/div').all()
        total_estacoes = len(estacoes)
        logging.info(f"Total de estações encontradas para MS: {total_estacoes}")
        
    except Exception as e:
        logging.error(f"Erro ao interagir com a página: {e}")
        logging.info("Entre em contato com desenvolvedores para verificar possívels mudanças na estrutura da página.")
        exit()
    
    pbar = tqdm.tqdm(range(1, total_estacoes + 1), desc="Baixando estações", leave=False)
    for i in pbar:
        logging.info(f"Baixando dados da estação {i}/{total_estacoes}")
        
        if i > 1 :            
            pagina.click('//*[@id="root"]/div[1]/div[1]/i') #Clicar pra abrir a lista da esquerda
            pagina.click('//*[@id="root"]/div[2]/div[1]/div[2]/div[3]') # Reabre a lista de estações (caso tenha fechado)
            time.sleep(1)        
        
        pagina.click(f'//*[@id="root"]/div[2]/div[1]/div[2]/div[3]/div[2]/div[{i}]') # Seleciona a estação atual
        
        try:
            nome_estacao = pagina.locator(f'//*[@id="root"]/div[2]/div[1]/div[2]/div[3]/div[2]/div[{i}]').inner_text()
        except Exception:
            logging.warning(f"Não foi possível capturar o nome da estação {i}. Usando nome do arquivo como fallback.")
            nome_estacao = ""        
        logging.info(f"Estação selecionada: {nome_estacao}")
        
        # Atualiza a barra de progresso com o nome da estação
        pbar.set_postfix({"Estação": nome_estacao[:30]})
        time.sleep(0.5)
            
        pagina.click('//*[@id="root"]/div[2]/div[1]/div[2]/button') #clicar para gerar a tabela
        time.sleep(0.5)
    
        # Processo de download do arquivo CSV
        try:
            pagina.wait_for_selector('//*[@id="root"]/div[2]/div[2]/div/div/div/span/a', timeout=30000)
            
            with pagina.expect_download() as download_info:
                pagina.click('//*[@id="root"]/div[2]/div[2]/div/div/div/span/a')
            
            download = download_info.value
            
            if not nome_estacao:
                # Fallback: usa o nome sugerido (sem extensão) caso o input não esteja acessível
                nome_estacao = os.path.splitext(download.suggested_filename)[0]

            #processo de limpeza de dados do arquivo
            safe_name = _slugify_filename(nome_estacao)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            custom_filename = f"{safe_name}_{timestamp}.csv"
            
            # Salva o arquivo na pasta Downloads com nome customizado
            caminho_arquivo = os.path.join(pasta_downloads, custom_filename)
            download.save_as(caminho_arquivo)
            
            df_estacao = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8')
            
            # Modificando o DF da acordo com o padrão da equipe    
            df_estacao = mdf_df_estacao(nome_estacao, df_estacao, df_loc_estacoes, time_delta=2) #Processo importante de normalização dos dados baixados
            df_estacao.to_csv(caminho_arquivo, index=False, encoding='utf-8', sep=';')
            logging.info(f"Arquivo salvo como {custom_filename} com {len(df_estacao)} registros válidos.")
            
        except TimeoutError:
            print(f"Timeout ao tentar baixar dados da estação {nome_estacao}. Pulando para próxima.")
            logging.error(f"Timeout ao tentar baixar dados da estação {nome_estacao}. Pulando para próxima.")
            continue
    
    navegador.close()
    
##############################################################################
# PROCESSO DE TRATAMENTO DOS DADOS E GERAÇÃO DE ARQUIVOS DE SAÍDA (.csv e .geojson)
##############################################################################

# unificando os arquivos baixados em um único DataFrame
try:
    arq = glob.glob('downloads/*.csv')
    df_unificado = pd.concat([pd.read_csv(f, sep=';', encoding='utf-8') for f in arq], ignore_index=True)
    logging.info(f"{len(arq)} arquivos CSV encontrados e unificados em um DataFrame com {len(df_unificado)} registros.")
    print(f"{len(arq)} arquivos CSV encontrados e unificados em um DataFrame com {len(df_unificado)} registros.")
except Exception as e:
    logging.error(f"Erro ao unificar arquivos CSV: {e} | possível causa: arquivos corrompidos ou estrutura incorreta.")
    print("Erro ao unificar arquivos CSV. Verifique se os arquivos estão no formato correto.")
    exit()

# Salvando em .csv
try:
    df_unificado.to_csv(os.path.join(pasta_saida, f'INMET_MS_{(datetime.now() - timedelta(hours=2)).strftime("%H") + "00"}_UTC.csv'), index=False, sep=';', encoding='utf-8')
    logging.info(f"Arquivo unificado salvo como INMET_MS_{datetime.now().strftime('%H') + '00'}_UTC.csv")
    print(f"Arquivo unificado salvo como INMET_MS_{(datetime.now()- timedelta(hours=2)).strftime('%H') + '00'}_UTC.csv")
except Exception as e:
    logging.error(f"Erro ao salvar arquivo unificado em CSV: {e}")
    print("Erro ao salvar arquivo unificado em CSV. Verifique as permissões de escrita no diretório.")
    exit()

# Processo para gerar o arquivo .geojson
# Tratamentos de formatação de latitude e longitude

try:
    logging.info("Iniciando processo de conversão para GeoJSON")
    print("Iniciando processo de conversão para GeoJSON")
    df_unificado['vl_longitude'] = (df_unificado['vl_longitude'].astype(str).str.replace(',', '.', regex=False))
    df_unificado['vl_latitude'] = (df_unificado['vl_latitude'].astype(str).str.replace(',', '.', regex=False))
    
    df_unificado['vl_longitude'] = pd.to_numeric(df_unificado['vl_longitude'], errors='coerce')
    df_unificado['vl_latitude'] = pd.to_numeric(df_unificado['vl_latitude'], errors='coerce')

    df_unificado = df_unificado.dropna(subset=['vl_latitude', 'vl_longitude'])
    geometry = [Point(float(lon), float(lat)) for lon, lat in zip(df_unificado['vl_longitude'], df_unificado['vl_latitude'])]
    gdf = gpd.GeoDataFrame(df_unificado, geometry=geometry, crs='EPSG:4326')
    gdf.to_file(os.path.join(pasta_saida, f'INMET_MS_{(datetime.now() - timedelta(hours=2)).strftime("%H") + "00"}_UTC.geojson'), driver='GeoJSON')
except Exception as e:
    logging.error(f"Erro ao converter para GeoJSON: {e} | possível causa: dados de latitude/longitude corrompidos ou estrutura do DataFrame incorreta. Verficar funcão mdf_df_estacao para garantir que os dados estão sendo processados corretamente.")
    print("Erro ao converter para GeoJSON. Verifique se os dados estão no formato correto.")
    exit()

logging.info(f"Processo de conversão para GeoJSON concluído. Arquivo salvo como INMET_MS_{(datetime.now() - timedelta(hours=2)).strftime('%H') + '00'}_UTC.geojson")
print(f"Processo de conversão para GeoJSON concluído. Arquivo salvo como INMET_MS_{(datetime.now() - timedelta(hours=2)).strftime('%H') + '00'}_UTC.geojson")

##############################################################################
# Processo de conexão e inserção dos dados trataodos no BD 🎲
##############################################################################

print("Iniciando processo de inserção dos dados no banco de dados")
logging.info("Iniciando processo de inserção dos dados no banco de dados")

create_tb = """
CREATE TABLE IF NOT EXISTS public.inmet_ms_utc (
    id              BIGSERIAL PRIMARY KEY,

    data            DATE NOT NULL,
    hora_utc        INTEGER NOT NULL,

    temp_c              DOUBLE PRECISION,
    temp_max_c          DOUBLE PRECISION,
    temp_min_c          DOUBLE PRECISION,

    umid_pct            DOUBLE PRECISION,
    umid_max_pct        DOUBLE PRECISION,
    umid_min_pct        DOUBLE PRECISION,

    pto_orvalho_c       DOUBLE PRECISION,
    pto_orvalho_max_c   DOUBLE PRECISION,
    pto_orvalho_min_c   DOUBLE PRECISION,

    press_hpa           DOUBLE PRECISION,
    press_max_hpa       DOUBLE PRECISION,
    press_min_hpa       DOUBLE PRECISION,

    vento_ms            DOUBLE PRECISION,
    dir_vento_ms        DOUBLE PRECISION,
    raj_vento_ms        DOUBLE PRECISION,

    radiacao_kj_m2      DOUBLE PRECISION,
    chuva_mm            DOUBLE PRECISION,

    cod_estacao     VARCHAR(10) NOT NULL,

    vl_latitude     DOUBLE PRECISION,
    vl_longitude    DOUBLE PRECISION,

    data_insercao   TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- opcional, mas recomendo MUITO para evitar duplicidades
    CONSTRAINT uq_inmet_ms_utc UNIQUE (cod_estacao, data, hora_utc)
);

CREATE INDEX IF NOT EXISTS idx_inmet_ms_utc_cod_estacao
    ON public.inmet_ms_utc (cod_estacao);

CREATE INDEX IF NOT EXISTS idx_inmet_ms_utc_data
    ON public.inmet_ms_utc (data);

CREATE INDEX IF NOT EXISTS idx_inmet_ms_utc_cod_estacao_data
    ON public.inmet_ms_utc (cod_estacao, data);
        """

df_bd = pd.read_csv(f'saida/INMET_MS_{(datetime.now() - timedelta(hours=2)).strftime("%H") + "00"}_UTC.csv', sep=";", encoding="utf-8")
df_bd["data"] = pd.to_datetime(df_bd["data"], format="%d/%m/%Y", errors="coerce").dt.date

pg_local = DBClient(DBConfig.from_env(prefix="LOCAL_POSTGRES"))

pg_local.criar_tabela_bd(table_name="inmet_ms_utc", create_sql=create_tb, schema="public")

pg_local.df_to_table(df_bd, table_name="inmet_ms_utc", schema="public")

logging.info("Processo de inserção dos dados no banco de dados concluído.")
print("Processo de inserção dos dados no banco de dados concluído.")
