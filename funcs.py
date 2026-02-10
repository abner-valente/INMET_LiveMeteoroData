from playwright.sync_api import sync_playwright
import time
import re



def _slugify_filename(name: str) -> str:
    name = name.strip() if isinstance(name, str) else ""
    # Substitui caracteres inválidos no Windows e normaliza espaços
    name = re.sub(r'[\\/*?:"<>|]', '_', name)
    name = re.sub(r'\s+', '_', name)
    # Limita tamanho para evitar problemas de caminho
    return name[:120] or "arquivo"

def insert_cod_estacao(nome_estacao: str) -> str:
    if nome_estacao:
        try:
            cod_estacao = nome_estacao.split('(')[1].split(')')[0]
            return cod_estacao
        except Exception:
            return ""
    return ""