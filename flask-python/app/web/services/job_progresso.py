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

"""Gerenciamento de jobs assincronos com barra de progresso (funcoes puras)."""

import threading
import uuid

JOBS_PROGRESSO = {}
JOBS_LOCK = threading.Lock()


def criar_job(mensagem_inicial="Iniciando..."):
    """Cria job e retorna job_id."""
    job_id = uuid.uuid4().hex
    with JOBS_LOCK:
        JOBS_PROGRESSO[job_id] = {
            "job_id": job_id,
            "status": "em_andamento",
            "mensagem": mensagem_inicial,
            "percentual": 0,
            "atual": 0,
            "total": 0,
            "nome_log": None,
            "redirect_url": None,
            "extra": None,
        }
    return job_id


def atualizar_job(job_id, payload):
    """Atualiza campos do job."""
    with JOBS_LOCK:
        job = JOBS_PROGRESSO.get(job_id)
        if not job:
            return
        for chave in (
            "status",
            "mensagem",
            "percentual",
            "atual",
            "total",
            "nome_log",
            "redirect_url",
            "extra",
        ):
            if chave in payload and payload[chave] is not None:
                job[chave] = payload[chave]


def obter_job(job_id):
    """Retorna copia do estado do job."""
    with JOBS_LOCK:
        job = JOBS_PROGRESSO.get(job_id)
        if not job:
            return None
        return dict(job)


def iniciar_thread(job_id, alvo):
    """Executa funcao alvo(job_id) em thread daemon."""
    thread = threading.Thread(target=alvo, args=(job_id,), daemon=True)
    thread.start()
