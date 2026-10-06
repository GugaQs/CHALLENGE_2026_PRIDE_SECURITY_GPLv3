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
Logger central ASPM — arquivo `logs/erro_sistema.log` na raiz `api_python/`.

Uso:
    from app.utils.log_sistema import get_logger
    log = get_logger("cadastro")  # nome opcional para aparecer em %(name)s

Nivel INFO grava no ficheiro; DEBUG pode ser usado para detalhe (mesmo handler).
Timestamps no ficheiro seguem UTC (`time.gmtime` no Formatter).
"""

from __future__ import annotations

import logging
import os
import time

_LOGGER_RAIZ = "ASPM"


def _pasta_logs_api_python(subpasta: str | None = None) -> str:
    """`api_python/logs` ou `api_python/logs/<subpasta>`.
    
    Este ficheiro esta em `api_python/app/utils/`.
    """
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    pasta = os.path.join(base, "logs")
    if subpasta:
        pasta = os.path.join(pasta, subpasta)
    return pasta


def _configurar_raiz_se_preciso() -> logging.Logger:
    """Garante um FileHandler unico no logger raiz ASPM (idempotente)."""
    log = logging.getLogger(_LOGGER_RAIZ)
    log.setLevel(logging.DEBUG)
    log.propagate = False
    if log.handlers:
        return log

    pasta = _pasta_logs_api_python()
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, "erro_sistema.log")
    handler = logging.FileHandler(caminho, encoding="utf-8")
    handler.setLevel(logging.INFO)
    formato = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    formato.converter = time.gmtime
    handler.setFormatter(formato)
    log.addHandler(handler)
    log.info(
        "ASPM PRIDE Security — logger configurado (timestamps UTC no arquivo)."
    )
    return log


def get_logger(submodulo: str | None = None) -> logging.Logger:
    """
    Retorna logger ASPM ou ASPM.<submodulo> (filhos propagam para o raiz).

    Args:
        submodulo: ex. "cadastro", "scan", "listar_falhas" — aparece no campo name do log.
    """
    _configurar_raiz_se_preciso()
    if submodulo:
        return logging.getLogger(f"{_LOGGER_RAIZ}.{submodulo}")
    return logging.getLogger(_LOGGER_RAIZ)


def get_hardware_logger(hardware: str) -> logging.Logger:
    """
    Logger dedicado por fabricante de GPU (trilha do motor de scan IA local).

    Grava em ``api_python/logs/<hardware>/system/sistema_<hardware>.log`` (timestamps UTC).
    ``propagate=True`` permite espelhar mensagens no logger raiz ``ASPM`` (``erro_sistema.log``)
    para auditoria unificada, mantendo ficheiro separado por AMD vs NVIDIA.

    Args:
        hardware: ``"amd"`` ou ``"nvidia"`` (case-insensitive).
    """
    hardware = hardware.lower()
    log_name = f"{_LOGGER_RAIZ}.{hardware}"
    log = logging.getLogger(log_name)
    
    # Se ja tem handlers, nao adiciona de novo
    if log.handlers:
        return log
        
    # Agora salvando na subpasta 'system' dentro de logs/<hardware>/
    pasta = os.path.join(_pasta_logs_api_python(hardware), "system")
    os.makedirs(pasta, exist_ok=True)
    
    caminho = os.path.join(pasta, f"sistema_{hardware}.log")
    handler = logging.FileHandler(caminho, encoding="utf-8")
    handler.setLevel(logging.INFO)
    
    formato = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    formato.converter = time.gmtime
    handler.setFormatter(formato)
    
    log.addHandler(handler)
    log.propagate = True # Permite que tambem va para o erro_sistema.log se o raiz estiver configurado
    
    return log
