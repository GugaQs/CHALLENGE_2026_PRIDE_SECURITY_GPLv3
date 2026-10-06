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

"""Testes de integracao dos motores de scan — apenas funcoes (pytest)."""

import os

import pytest

from app.ui.scan_ia_local.scan_amd.executar_scan import salvar_log_json_amd
from app.ui.scan_ia_local.scan_nvidia.executar_scan import salvar_log_json_nvidia
from app.ui.scan_projeto.executar_scan import salvar_log_json


@pytest.fixture
def mock_data():
    """Payload minimo para testar gravacao de relatorios."""
    return {"test": True, "integration_test": "v1"}


def test_salvar_log_json_amd_path(mock_data):
    """Motor AMD grava em logs/amd/reports."""
    caminho = salvar_log_json_amd(mock_data)
    try:
        assert os.path.isabs(caminho)
        assert os.path.join("logs", "amd", "reports") in caminho
        assert os.path.exists(caminho)
    finally:
        if os.path.exists(caminho):
            os.remove(caminho)


def test_salvar_log_json_nvidia_path(mock_data):
    """Motor NVIDIA grava em logs/nvidia/reports."""
    caminho = salvar_log_json_nvidia(mock_data)
    try:
        assert os.path.isabs(caminho)
        assert os.path.join("logs", "nvidia", "reports") in caminho
        assert os.path.exists(caminho)
    finally:
        if os.path.exists(caminho):
            os.remove(caminho)


def test_salvar_log_json_generic_path(mock_data):
    """Motor generico grava em logs/generic/reports."""
    caminho = salvar_log_json(mock_data)
    try:
        assert os.path.isabs(caminho)
        assert os.path.join("logs", "generic", "reports") in caminho
        assert os.path.exists(caminho)
    finally:
        if os.path.exists(caminho):
            os.remove(caminho)
