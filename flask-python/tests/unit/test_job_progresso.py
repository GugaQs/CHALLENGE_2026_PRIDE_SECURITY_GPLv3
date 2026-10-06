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

"""Testes unitarios do gerenciador de jobs com progresso."""

import threading

from app.web.services import job_progresso


def setup_function():
    """Limpa estado global antes de cada teste."""
    job_progresso.JOBS_PROGRESSO.clear()


def test_criar_job_com_campos_padrao():
    """Cria job com payload base esperado."""
    job_id = job_progresso.criar_job("Teste inicial")
    dados = job_progresso.obter_job(job_id)

    assert dados is not None
    assert dados["job_id"] == job_id
    assert dados["status"] == "em_andamento"
    assert dados["mensagem"] == "Teste inicial"
    assert dados["percentual"] == 0
    assert dados["extra"] is None


def test_atualizar_job_aplica_campos_permitidos():
    """Atualiza apenas campos de controle do job."""
    job_id = job_progresso.criar_job()
    job_progresso.atualizar_job(
        job_id,
        {
            "status": "concluido",
            "mensagem": "ok",
            "percentual": 100,
            "atual": 10,
            "total": 10,
            "nome_log": "report.json",
            "redirect_url": "/scan/logs/report.json",
            "extra": {"artefatos": []},
            "campo_invalido": "ignorar",
        },
    )

    dados = job_progresso.obter_job(job_id)
    assert dados["status"] == "concluido"
    assert dados["mensagem"] == "ok"
    assert dados["percentual"] == 100
    assert dados["nome_log"] == "report.json"
    assert dados["redirect_url"] == "/scan/logs/report.json"
    assert dados["extra"] == {"artefatos": []}
    assert "campo_invalido" not in dados


def test_obter_job_retorna_none_para_id_inexistente():
    """Consulta de job inexistente retorna None."""
    assert job_progresso.obter_job("inexistente") is None


def test_iniciar_thread_executa_alvo():
    """Thread criada executa funcao alvo recebendo o job_id."""
    event = threading.Event()
    recebido = {}

    def alvo(job_id):
        recebido["job_id"] = job_id
        event.set()

    job_progresso.iniciar_thread("abc123", alvo)

    assert event.wait(1), "Thread nao executou no tempo esperado."
    assert recebido["job_id"] == "abc123"
