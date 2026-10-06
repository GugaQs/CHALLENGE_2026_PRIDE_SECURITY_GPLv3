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

"""Servicos web dos modulos em evolucao (IA API, containers, software)."""

import os

from app.ui.scan_containers.executar_scan_containers import executar_scan_containers
from app.ui.scan_ia_api.config_api import (
    PROVEDORES_DISPONIVEIS,
    carregar_config_ia_api,
    iniciar_varredura_ia_api,
    registrar_api_key_ia_api,
    salvar_provedor_ia_api,
)
from app.ui.scan_software.listar_software import listar_software_instalado
from app.web.services.job_progresso import (
    atualizar_job,
    criar_job,
    iniciar_thread,
    obter_job,
)


def obter_config_ia_api():
    """Config atual para template."""
    return carregar_config_ia_api()


def obter_provedores_ia_api():
    """Lista de provedores suportados."""
    return list(PROVEDORES_DISPONIVEIS)


def configurar_provedor(provedor):
    """Salva provedor IA API."""
    return salvar_provedor_ia_api(provedor)


def configurar_api_key(api_key):
    """Registra API key (mascarada em disco)."""
    return registrar_api_key_ia_api(api_key)


def executar_varredura_ia_api(caminho):
    """Inicia varredura placeholder."""
    return iniciar_varredura_ia_api(caminho)


def executar_scan_docker(caminho, progress_callback=None):
    """Lista artefatos Docker no projeto."""
    return executar_scan_containers(caminho, progress_callback=progress_callback)


def iniciar_scan_docker_assincrono(caminho):
    """Scan Docker em background com progresso."""
    caminho = (caminho or "").strip()
    if not caminho or not os.path.isdir(caminho):
        return False, "Caminho invalido.", None

    job_id = criar_job("Buscando artefatos Docker...")
    iniciar_thread(
        job_id,
        lambda jid: _scan_docker_background(jid, caminho),
    )
    return True, "Scan Docker iniciado.", job_id


def _scan_docker_background(job_id, caminho):
    """Worker do scan de containers."""

    def atualizar(payload):
        atualizar_job(job_id, payload)

    try:
        ok, msg, artefatos = executar_scan_containers(
            caminho,
            progress_callback=atualizar,
        )
        atualizar_job(
            job_id,
            {
                "status": "concluido" if ok else "erro",
                "mensagem": msg,
                "percentual": 100,
                "extra": {"artefatos": artefatos},
            },
        )
    except Exception as erro:
        atualizar_job(job_id, {"status": "erro", "mensagem": str(erro)})


def obter_status_scan_docker(job_id):
    """Consulta status do job Docker."""
    return obter_job(job_id)


def listar_programas_instalados(limite=50):
    """Lista software instalado (Windows)."""
    return listar_software_instalado(limite=limite)
