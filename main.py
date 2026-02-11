import time
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='automation_log.log',
    filemode='a'
    )

URL = "https://tempo.inmet.gov.br/TabelaEstacoes/"


 # Lendo arquivo loc_estacoes.csv para obter os códigos das estações
try:
    df_loc_estacoes = pd.read_csv("loc_estacoes.csv", encoding='utf-8', sep=';')
    cod_estacao_map = dict(zip(df_loc_estacoes['CD_ESTACAO'], df_loc_estacoes['DC_NOME']))
    logging.info(f"Arquivo loc_estacoes.csv carregado com sucesso. {len(cod_estacao_map)} estações mapeadas.")
except Exception as e:
    logging.error(f"Erro ao carregar loc_estacoes.csv: {e}")
    df_loc_estacoes = pd.DataFrame()  # Cria um DataFrame vazio
    cod_estacao_map = {}

# Define a pasta de saída dentro do projeto
pasta_downloads = os.path.join(os.path.dirname(__file__), "downloads")

# Cria a pasta se não existir
os.makedirs(pasta_downloads, exist_ok=True)

#apagar arquivos antigos da pasta downloads
for nome in os.listdir(pasta_downloads):
    caminho = os.path.join(pasta_downloads, nome)
    if os.path.isfile(caminho) or os.path.islink(caminho):
        os.remove(caminho)
    elif os.path.isdir(caminho):
        shutil.rmtree(caminho)


with sync_playwright() as p:
        
    logging.info("Iniciando o navegador")
    navegador = p.chromium.launch(headless=False)
    pagina = navegador.new_page()
    pagina.goto(URL)
    logging.info(f"Acessou a URL: {URL}")
    
    #Clicar pra abrir a lista da esquerda
    pagina.click('//*[@id="root"]/div[1]/div[1]/i')
    
    #Selecionar Estaçoes Automáticas
    pagina.click('//*[@id="root"]/div[2]/div[1]/div[2]/div[1]/button[1]')
    
    #clicar para abrir opções de estado
    pagina.click('//*[@id="root"]/div[2]/div[1]/div[2]/div[2]/input')
    time.sleep(1)
    
    #selecionar o estado de MS
    pagina.click('//*[@id="root"]/div[2]/div[1]/div[2]/div[2]/div[2]/div[13]')
    time.sleep(1)
    
    #clicar para abrir opções de estação
    pagina.click('//*[@id="root"]/div[2]/div[1]/div[2]/div[3]/input')
    time.sleep(1)
    
    estacoes = pagina.locator('//*[@id="root"]/div[2]/div[1]/div[2]/div[3]/div[2]/div').all()
    total_estacoes = len(estacoes)
    
    # Agora você pode iterar
    for i in range(1, total_estacoes + 1): 
        logging.info(f"Baixando dados da estação {i}/{total_estacoes}")
        print(f"Baixando dados da estação {i}/{total_estacoes}")
        
        if i > 1 :
            #Clicar pra abrir a lista da esquerda
            pagina.click('//*[@id="root"]/div[1]/div[1]/i')
        
            # Reabre a lista de estações (caso tenha fechado)
            pagina.click('//*[@id="root"]/div[2]/div[1]/div[2]/div[3]')
            time.sleep(1)        
        
        # Seleciona a estação atual
        pagina.click(f'//*[@id="root"]/div[2]/div[1]/div[2]/div[3]/div[2]/div[{i}]')
        
        try:
            nome_estacao = pagina.locator(f'//*[@id="root"]/div[2]/div[1]/div[2]/div[3]/div[2]/div[{i}]').inner_text()
        except Exception:
            nome_estacao = ""        
        logging.info(f"Estação selecionada: {nome_estacao}")
        

        print(nome_estacao)
        time.sleep(1)
    
    
        #clicar para gerar a tabela
        pagina.click('//*[@id="root"]/div[2]/div[1]/div[2]/button')
        time.sleep(1)
    
        #clicar para baixar a tabela em CSV e capturar o download
        try:
            # Aguarda o botão de download ficar visível antes de clicar
            pagina.wait_for_selector('//*[@id="root"]/div[2]/div[2]/div/div/div/span/a', timeout=30000)
            
            with pagina.expect_download() as download_info:
                pagina.click('//*[@id="root"]/div[2]/div[2]/div/div/div/span/a')
            
            download = download_info.value

            
            if not nome_estacao:
                # Fallback: usa o nome sugerido (sem extensão) caso o input não esteja acessível
                nome_estacao = os.path.splitext(download.suggested_filename)[0]

            safe_name = _slugify_filename(nome_estacao)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            custom_filename = f"{safe_name}_{timestamp}.csv"
            
            # Salva o arquivo na pasta Downloads com nome customizado
            caminho_arquivo = os.path.join(pasta_downloads, custom_filename)
            download.save_as(caminho_arquivo)
            
            df_estacao = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8')
            
            # Modificando o DF da acordo com o padrão da equipe    
            df_estacao = mdf_df_estacao(nome_estacao, df_estacao, df_loc_estacoes, time_delta=2)
            df_estacao.to_csv(caminho_arquivo, index=False, encoding='utf-8', sep=';')

            print(f"Arquivo baixado com sucesso: {caminho_arquivo}")
        
        except TimeoutError:
            print(f"Timeout ao tentar baixar dados da estação {nome_estacao}. Pulando para próxima.")
            logging.error(f"Timeout ao tentar baixar dados da estação {nome_estacao}. Pulando para próxima.")
            continue
    
    navegador.close()

# unificando os arquivos baixados em um único DataFrame
arq = glob.glob('downloads/*.csv')
df_unificado = pd.concat([pd.read_csv(f, sep=';', encoding='utf-8') for f in arq], ignore_index=True)
logging.info(f"{len(arq)} arquivos CSV encontrados e unificados em um DataFrame com {len(df_unificado)} registros.")
print(f"{len(arq)} arquivos CSV encontrados e unificados em um DataFrame com {len(df_unificado)} registros.")


# Salvando em .csv
df_unificado.to_csv(F'INMET_{datetime.now().strftime('%H') + '00'}_UTC.csv', index=False, sep=';', encoding='utf-8')
logging.info(f"Arquivo unificado salvo como INMET_{datetime.now().strftime('%H') + '00'}_UTC.csv")
print(f"Arquivo unificado salvo como INMET_{datetime.now().strftime('%H') + '00'}_UTC.csv")

# Processo para gerar o arquivo .geojson
# Tratamentos de formatação de latitude e longitude
logging.info("Iniciando processo de conversão para GeoJSON")
print("Iniciando processo de conversão para GeoJSON")
df_unificado['VL_LONGITUDE'] = (
    df_unificado['VL_LONGITUDE']
    .astype(str)
    .str.replace(',', '.', regex=False)
)
df_unificado['VL_LATITUDE'] = (
    df_unificado['VL_LATITUDE']
    .astype(str)
    .str.replace(',', '.', regex=False)
)
df_unificado['VL_LONGITUDE'] = pd.to_numeric(df_unificado['VL_LONGITUDE'], errors='coerce')
df_unificado['VL_LATITUDE'] = pd.to_numeric(df_unificado['VL_LATITUDE'], errors='coerce')

df_unificado = df_unificado.dropna(subset=['VL_LATITUDE', 'VL_LONGITUDE'])
geometry = [Point(float(lon), float(lat)) for lon, lat in zip(df_unificado['VL_LONGITUDE'], df_unificado['VL_LATITUDE'])]
gdf = gpd.GeoDataFrame(df_unificado, geometry=geometry, crs='EPSG:4326')
gdf.to_file(f'INMET_{(datetime.now() - timedelta(hours=2)).strftime("%H") + "00"}_UTC.geojson', driver='GeoJSON')

logging.info(f"Processo de conversão para GeoJSON concluído. Arquivo salvo como INMET_{(datetime.now() - timedelta(hours=2)).strftime('%H') + '00'}_UTC.geojson")
print(f"Processo de conversão para GeoJSON concluído. Arquivo salvo como INMET_{(datetime.now() - timedelta(hours=2)).strftime('%H') + '00'}_UTC.geojson")



