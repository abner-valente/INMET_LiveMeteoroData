# Dockerfile
FROM python:3.14-slim

# Evita .pyc e melhora logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências do sistema (psycopg2 e afins)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
      unixodbc \
      unixodbc-dev \
      libodbc2 \
 && rm -rf /var/lib/apt/lists/*

# Instala dependências python primeiro (melhor cache)
COPY requeriment.txt /app/requeriment.txt
RUN pip install --no-cache-dir -r requeriment.txt
RUN playwright install --with-deps chromium

# Copia o projeto
COPY . /app

# ✅ AJUSTE AQUI o comando do seu projeto:
# Ex: CMD ["python", "main.py"]
CMD ["python", "main.py"]
