from playwright.sync_api import sync_playwright
import time
import re



def _slugify_filename(name):
    name = name.strip() if isinstance(name, str) else ""
    # Substitui caracteres inválidos no Windows e normaliza espaços
    name = re.sub(r'[\\/*?:"<>|]', '_', name)
    name = re.sub(r'\s+', '_', name)
    # Limita tamanho para evitar problemas de caminho
    return name[:120] or "arquivo"