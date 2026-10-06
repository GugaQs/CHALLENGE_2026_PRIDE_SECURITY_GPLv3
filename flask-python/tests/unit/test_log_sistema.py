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

"""Testes do logger central — apenas funcoes (pytest)."""

import logging
import os

import pytest

from app.utils.log_sistema import get_logger, get_hardware_logger, _pasta_logs_api_python


def test_pasta_logs_base():
    """Verifica se a pasta base de logs e resolvida corretamente."""
    pasta = _pasta_logs_api_python()
    assert pasta.endswith("logs")
    assert os.path.isabs(pasta)


def test_get_logger_basic():
    """Verifica se o logger basico e retornado."""
    log = get_logger("teste_unitario")
    assert isinstance(log, logging.Logger)
    assert log.name == "ASPM.teste_unitario"


def test_get_hardware_logger_amd():
    """Verifica se o logger AMD aponta para logs/amd/system."""
    log = get_hardware_logger("amd")
    assert log.name == "ASPM.amd"

    found_handler = False
    for handler in log.handlers:
        if isinstance(handler, logging.FileHandler):
            caminho = handler.baseFilename
            if "logs" in caminho and "amd" in caminho and "system" in caminho:
                found_handler = True
                break
    assert found_handler, "FileHandler AMD system nao encontrado."


def test_get_hardware_logger_nvidia():
    """Verifica se o logger NVIDIA aponta para logs/nvidia/system."""
    log = get_hardware_logger("nvidia")
    assert log.name == "ASPM.nvidia"

    found_handler = False
    for handler in log.handlers:
        if isinstance(handler, logging.FileHandler):
            caminho = handler.baseFilename
            if "logs" in caminho and "nvidia" in caminho and "system" in caminho:
                found_handler = True
                break
    assert found_handler, "FileHandler NVIDIA system nao encontrado."
