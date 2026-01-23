import time
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "https://tempo.inmet.gov.br/TabelaEstacoes/"

# Define a pasta de saída dentro do projeto
pasta_downloads = os.path.join(os.path.dirname(__file__), "downloads")

# Cria a pasta se não existir
os.makedirs(pasta_downloads, exist_ok=True)

with sync_playwright() as p:
    navegador = p.chromium.launch(headless=False)
    pagina = navegador.new_page()
    pagina.goto(URL)
    
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
    for i in range(total_estacoes): 
        print(f"Baixando dados da estação {i-1}/{total_estacoes}")
        
        if i > 1 :
            #Clicar pra abrir a lista da esquerda
            pagina.click('//*[@id="root"]/div[1]/div[1]/i')
        
            # Reabre a lista de estações (caso tenha fechado)
            pagina.click('//*[@id="root"]/div[2]/div[1]/div[2]/div[3]/input')
            time.sleep(1)
        
        # Seleciona a estação atual
        pagina.click(f'//*[@id="root"]/div[2]/div[1]/div[2]/div[3]/div[2]/div[{i}]')
        time.sleep(1)
    
    
        #clicar para gerar a tabela
        pagina.click('//*[@id="root"]/div[2]/div[1]/div[2]/button')
        time.sleep(5)
    
    #clicar para baixar a tabela em CSV e capturar o download
    with pagina.expect_download() as download_info:
        pagina.click('//*[@id="root"]/div[2]/div[2]/div/div/div/span/a')
    
    download = download_info.value
    
    # Salva o arquivo na pasta Downloads
    caminho_arquivo = os.path.join(pasta_downloads, download.suggested_filename)
    download.save_as(caminho_arquivo)
    
    print(f"Arquivo baixado com sucesso: {caminho_arquivo}")
    
    navegador.close()
    

    