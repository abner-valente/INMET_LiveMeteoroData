import time
import os
from funcs import _slugify_filename
from pathlib import Path
from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError
from datetime import datetime
import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='automation_log.log',
    filemode='a'
    )

URL = "https://tempo.inmet.gov.br/TabelaEstacoes/"


# Define a pasta de saída dentro do projeto
pasta_downloads = os.path.join(os.path.dirname(__file__), "downloads")

# Cria a pasta se não existir
os.makedirs(pasta_downloads, exist_ok=True)


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

            print(f"Arquivo baixado com sucesso: {caminho_arquivo}")
        
        except TimeoutError:
            print(f"Timeout ao tentar baixar dados da estação {nome_estacao}. Pulando para próxima.")
            logging.error(f"Timeout ao tentar baixar dados da estação {nome_estacao}. Pulando para próxima.")
            continue
    
    navegador.close()


    