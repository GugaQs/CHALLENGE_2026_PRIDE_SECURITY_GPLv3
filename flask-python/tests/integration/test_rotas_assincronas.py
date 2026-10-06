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

"""Testes de integracao para rotas assincronas com progresso."""

import pytest

from app.web.app import create_app
from app.web.routes import ia_local_routes, modulos_routes, scan_routes


@pytest.fixture
def client():
    """Cliente Flask para testes de integracao."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    return app.test_client()


def test_scan_executar_assincrono_ok(client, monkeypatch):
    """POST /scan/executar-assincrono retorna job quando valido."""
    monkeypatch.setattr(
        scan_routes,
        "iniciar_scan_assincrono",
        lambda _caminho: (True, "Scan iniciado.", "job_scan_1"),
    )

    resposta = client.post("/scan/executar-assincrono", json={"caminho": "G:/tmp"})
    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert dados["ok"] is True
    assert dados["job_id"] == "job_scan_1"


def test_scan_status_job_inexistente(client, monkeypatch):
    """GET /scan/status retorna 404 para job desconhecido."""
    monkeypatch.setattr(scan_routes, "obter_status_scan", lambda _job_id: None)

    resposta = client.get("/scan/status/job_invalido")
    dados = resposta.get_json()

    assert resposta.status_code == 404
    assert dados["ok"] is False


def test_ia_local_rotas_assincronas(client, monkeypatch):
    """Rotas assíncronas de IA local iniciam e consultam status."""
    monkeypatch.setattr(
        ia_local_routes,
        "iniciar_scan_gpu_assincrono",
        lambda _hw, _caminho: (True, "Scan iniciado.", "job_ia_scan"),
    )
    monkeypatch.setattr(
        ia_local_routes,
        "iniciar_scan_cognitivo_assincrono",
        lambda _hw, _caminho: (True, "Cognitivo iniciado.", "job_ia_cog"),
    )
    monkeypatch.setattr(
        ia_local_routes,
        "obter_status_job_ia",
        lambda _job_id: {"status": "em_andamento", "percentual": 55},
    )

    r1 = client.post(
        "/ia-local/executar-assincrono",
        json={"hardware": "amd", "caminho": "G:/tmp"},
    )
    r2 = client.post(
        "/ia-local/cognitivo-assincrono",
        json={"hardware": "nvidia", "caminho": "G:/tmp"},
    )
    r3 = client.get("/ia-local/status/job_ia_scan")

    assert r1.status_code == 200
    assert r1.get_json()["job_id"] == "job_ia_scan"
    assert r2.status_code == 200
    assert r2.get_json()["job_id"] == "job_ia_cog"
    assert r3.status_code == 200
    assert r3.get_json()["dados"]["percentual"] == 55


def test_modulos_containers_assincrono_e_status(client, monkeypatch):
    """Rotas JSON de containers suportam iniciar e consultar status."""
    monkeypatch.setattr(
        modulos_routes,
        "iniciar_scan_docker_assincrono",
        lambda _caminho: (True, "Docker iniciado.", "job_docker_1"),
    )
    monkeypatch.setattr(
        modulos_routes,
        "obter_status_scan_docker",
        lambda _job_id: {
            "status": "concluido",
            "percentual": 100,
            "extra": {"artefatos": [{"nome": "Dockerfile"}]},
        },
    )

    resposta_exec = client.post(
        "/modulos/containers/executar-assincrono",
        json={"caminho": "G:/tmp"},
    )
    resposta_status = client.get("/modulos/containers/status/job_docker_1")

    assert resposta_exec.status_code == 200
    assert resposta_exec.get_json()["job_id"] == "job_docker_1"
    assert resposta_status.status_code == 200
    dados_status = resposta_status.get_json()["dados"]
    assert dados_status["status"] == "concluido"
    assert dados_status["extra"]["artefatos"][0]["nome"] == "Dockerfile"
