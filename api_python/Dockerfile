# Copyright (C) 2026 Equipe ASPM IA FIAP - Challenge 2026
# Licensed under the GNU General Public License v3.0.
# See LICENSE.md for the full license text.

# Dockerfile para o projeto ASPM IA FIAP - Desafio Pride 2026
FROM python:3.11-slim

# Evita que o Python gere arquivos .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define o diretório de trabalho no container
WORKDIR /app

# Instala as dependências (apenas o colorama por enquanto)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código do projeto
COPY . .

# Expõe o diretório app para o path
ENV PYTHONPATH=/app

# Comando de entrada - Rodando o script principal
CMD ["python", "main.py"]
