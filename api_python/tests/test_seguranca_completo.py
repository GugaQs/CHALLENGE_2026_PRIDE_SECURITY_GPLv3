# Copyright (C) 2026 Equipe ASPM IA FIAP - Challenge 2026
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See LICENSE.md
# for the full GNU General Public License.

"""
Testes de Segurança Completos — ASPM PRIDE Security.

Este módulo realiza testes de integração para verificar se o motor de scan
consegue detectar corretamente as diferentes categorias de vulnerabilidades
definidas nas regras de assinatura.
"""

import os
import json
from pathlib import Path
import pytest
from app.ui.scan_projeto.executar_scan import rodar_engine_scan
from app.ui.scan_projeto.filtros.regras_seguranca import obter_assinaturas_vulnerabilidade

def setup_projeto_vulneravel(tmp_path):
    """Cria um projeto temporário com diversos arquivos contendo vulnerabilidades."""
    projeto = tmp_path / "projeto_teste_seguranca"
    projeto.mkdir()

    # 1. SQL Injection (Python)
    sql_file = projeto / "database_service.py"
    sql_file.write_text('''
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    return db.execute(query)
''', encoding="utf-8")

    # 2. RCE (Python)
    rce_file = projeto / "utils_sistema.py"
    rce_file.write_text('''
import os
import subprocess

def executar_comando(cmd):
    os.system(cmd)
    subprocess.run(cmd, shell=True)
''', encoding="utf-8")

    # 3. Credenciais Hardcoded
    creds_file = projeto / "config_env.py"
    creds_file.write_text('''
API_KEY = "sk_test_" + "CHAVE_DE_TESTE_FICTICIA"
DB_PASSWORD = "super_secret_password_123"
''', encoding="utf-8")

    # 4. XSS (JavaScript)
    xss_file = projeto / "frontend.js"
    xss_file.write_text('''
function renderUser(name) {
    document.getElementById('user-display').innerHTML = "<h1>" + name + "</h1>";
}
''', encoding="utf-8")

    # 5. Path Traversal (usando um padrão que o motor detecta: open(request.)
    path_file = projeto / "file_manager.py"
    path_file.write_text('''
def read_user_file(request):
    with open(request.args['file'], "r") as f:
        return f.read()
''', encoding="utf-8")

    # 6. Deserialização Insegura
    deserial_file = projeto / "cache_service.py"
    deserial_file.write_text('''
import pickle

def load_cache(data):
    return pickle.loads(data)
''', encoding="utf-8")

    # 7. SSRF
    ssrf_file = projeto / "network_client.py"
    ssrf_file.write_text('''
import requests

def fetch_external_resource(url):
    return requests.get(url)
''', encoding="utf-8")

    # 8. JWT Inseguro
    jwt_file = projeto / "auth.py"
    jwt_file.write_text('''
import jwt

def decode_token(token):
    return jwt.decode(token, options={"verify_signature": False})
''', encoding="utf-8")

    return projeto

def test_motor_scan_detecta_todas_categorias_principais(tmp_path):
    """
    Verifica se o motor de scan identifica as principais categorias de falhas
    ao analisar um projeto que as contém propositalmente.
    """
    projeto_path = setup_projeto_vulneravel(tmp_path)
    
    # Executa o scan
    caminho_relatorio = rodar_engine_scan(str(projeto_path))
    
    assert caminho_relatorio is not None
    assert os.path.exists(caminho_relatorio)
    
    with open(caminho_relatorio, "r", encoding="utf-8") as f:
        relatorio = json.load(f)
    
    vulnerabilidades = relatorio.get("vulnerabilidades", [])
    tipos_detectados = {v["tipo"] for v in vulnerabilidades}
    
    # Categorias que DEVEM ser detectadas com base no setup_projeto_vulneravel
    categorias_esperadas = [
        "SQL Injection Provavel",
        "Execução de Risco (RCE)",
        "Credenciais Hardcoded",
        "XSS (Cross-Site Scripting)",
        "Path Traversal / LFI",
        "Deserialização Insegura",
        "SSRF (Server-Side Request Forgery)",
        "JWT Inseguro"
    ]
    
    for categoria in categorias_esperadas:
        assert categoria in tipos_detectados, f"A categoria '{categoria}' não foi detectada pelo scan."

def test_severidade_ordenacao(tmp_path):
    """
    Verifica se o relatório final vem ordenado por severidade (Crítico primeiro).
    """
    projeto_path = setup_projeto_vulneravel(tmp_path)
    caminho_relatorio = rodar_engine_scan(str(projeto_path))
    
    with open(caminho_relatorio, "r", encoding="utf-8") as f:
        relatorio = json.load(f)
    
    vulnerabilidades = relatorio.get("vulnerabilidades", [])
    
    # Mapeamento de pesos para verificação
    pesos = {"CRÍTICO": 4, "ALTO": 3, "MÉDIO": 2, "BAIXO": 1}
    
    pesos_obtidos = [pesos.get(v["severidade"], 0) for v in vulnerabilidades]
    
    # Verifica se a lista de pesos está em ordem decrescente
    assert pesos_obtidos == sorted(pesos_obtidos, reverse=True), "As vulnerabilidades não estão ordenadas por severidade."
