# Copyright (C) 2026 Equipe ASPM IA FIAP - Challenge 2026
# Licensed under the GNU General Public License v3.0.
# See LICENSE.md for the full license text.

# ASPM Pride Security — interface web Flask
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

EXPOSE 5000

# Web por padrao; para CLI use: docker compose run app python main.py
CMD ["python", "app.py"]
