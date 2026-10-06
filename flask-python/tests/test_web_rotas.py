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

"""Testes das rotas Flask — apenas funcoes (pytest)."""

import pytest

from app.web.app import create_app
from app.web.routes import ia_local_routes


@pytest.fixture
def client():
    """Cliente de testes Flask."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    return app.test_client()


def test_home_ok(client):
    """Pagina inicial responde 200."""
    resposta = client.get("/")
    assert resposta.status_code == 200


def test_scan_pagina(client):
    """Pagina de scan carrega."""
    resposta = client.get("/scan/")
    assert resposta.status_code == 200


def test_logs_sistema(client):
    """Pagina de logs do sistema."""
    resposta = client.get("/logs/")
    assert resposta.status_code == 200


def test_ia_local(client):
    """Painel IA local."""
    resposta = client.get("/ia-local/")
    assert resposta.status_code == 200


def test_modulo_ia_api(client):
    """Configuracao IA API."""
    resposta = client.get("/modulos/ia-api")
    assert resposta.status_code == 200


def test_modulo_containers(client):
    """Scan containers."""
    resposta = client.get("/modulos/containers")
    assert resposta.status_code == 200


def test_modulo_scan_software(client):
    """Scan software."""
    resposta = client.get("/modulos/scan-software")
    assert resposta.status_code == 200


def test_sobre(client):
    """Pagina sobre."""
    resposta = client.get("/sobre/")
    assert resposta.status_code == 200


def test_documentacao_pagina(client):
    """Pagina de documentacao carrega e renderiza conteudo HTML."""
    resposta = client.get("/documentacao/")
    conteudo = resposta.data.decode("utf-8", errors="ignore")
    assert resposta.status_code == 200
    assert "Documentacao do Projeto" in conteudo
    assert "Indice" in conteudo


def test_config_ia_api_provedor(client, tmp_path, monkeypatch):
    """Salvar provedor IA API."""
    from app.ui import scan_ia_api

    def _pasta_fake():
        pasta = tmp_path / "config"
        pasta.mkdir(parents=True, exist_ok=True)
        return str(pasta)

    monkeypatch.setattr(
        scan_ia_api.config_api,
        "_pasta_config",
        _pasta_fake,
    )
    resposta = client.post(
        "/modulos/ia-api",
        data={"acao": "provedor", "provedor": "gemini"},
        follow_redirects=True,
    )
    assert resposta.status_code == 200


def test_template_scan_contem_painel_progresso(client):
    """Pagina /scan exibe painel de progresso reutilizavel."""
    resposta = client.get("/scan/")
    assert resposta.status_code == 200
    assert b'id="painel-progresso"' in resposta.data
    assert b'id="barra-progresso-preenchimento"' in resposta.data


def test_template_ia_local_contem_painel_progresso(client):
    """Pagina /ia-local exibe painel de progresso."""
    resposta = client.get("/ia-local/")
    assert resposta.status_code == 200
    assert b'id="painel-progresso"' in resposta.data
    assert b'id="barra-progresso-preenchimento"' in resposta.data


def test_template_modulo_containers_contem_painel_progresso(client):
    """Pagina /modulos/containers exibe painel de progresso."""
    resposta = client.get("/modulos/containers")
    assert resposta.status_code == 200
    assert b'id="painel-progresso"' in resposta.data
    assert b'id="barra-progresso-preenchimento"' in resposta.data


def test_auditoria_ia_local_filtra_por_severidade(client, monkeypatch):
    """Auditoria IA local deve aplicar filtro de severidade."""
    auditoria_mock = {
        "dados": {"projeto": "x"},
        "falhas": [
            {"indice": 1, "severidade": "CRITICO", "tipo": "a", "arquivo": "a.py", "linha": 1},
            {"indice": 2, "severidade": "ALTO", "tipo": "b", "arquivo": "b.py", "linha": 2},
        ],
        "nome_arquivo": "amd_report.json",
    }
    monkeypatch.setattr(
        ia_local_routes,
        "obter_dados_auditoria",
        lambda _hardware, _nome_log: auditoria_mock,
    )

    resposta = client.get("/ia-local/auditoria/amd/amd_report.json?severidade=ALTO")
    conteudo = resposta.data.decode("utf-8", errors="ignore")

    assert resposta.status_code == 200

    # O formulario de filtro precisa estar na pagina para o filtro ser usavel.
    # Afirmamos o campo pelo NOME, nao pelo rotulo: rotulo e texto de tela e muda
    # com o design; `name="severidade"` e o contrato que a rota le em request.args.
    assert 'name="severidade"' in conteudo
    assert "Filtrar falhas" in conteudo

    # O filtro tem de FILTRAR de verdade: a falha ALTO entra e a CRITICO sai.
    # A versao anterior deste teste so procurava um rotulo, o que passaria mesmo
    # se o filtro nao removesse nada.
    assert "b.py" in conteudo, "a falha de severidade ALTO deveria aparecer"
    assert "a.py" not in conteudo, "a falha CRITICO deveria ter sido filtrada fora"
    assert "a.py" not in conteudo
