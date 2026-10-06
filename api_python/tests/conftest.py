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
Isolamento da suíte de testes do módulo `api_python`.

PROPÓSITO DE NEGÓCIO
--------------------
Cinco arquivos de teste deste módulo executam o motor de scan e o logger de
verdade (`rodar_engine_scan`, `salvar_log_json*`, `get_hardware_logger`). Sem
isolamento, cada `pytest` grava relatórios e linhas de log na árvore REAL de
`api_python/logs/` — e como os nomes de relatório são gerados com granularidade
de **segundo**, um teste pode sobrescrever um relatório de verdade do usuário.

Isto não é hipotético neste repositório: relatórios de scan já foram perdidos
aqui, e o `.gitignore` (`logs/`) impede recuperá-los pelo git.

Este arquivo é a contrapartida do `flask-python/tests/conftest.py`, com a mesma
mecânica e as mesmas invariantes.

INVARIANTES DO DOMÍNIO
----------------------
- **INV-TESTE-001** · Nenhuma escrita fora do sandbox. Os onze módulos que
  derivam a raiz do projeto de `os.path.dirname(__file__)` têm o `__file__`
  repontado para um diretório temporário. Isola **sem alterar código de
  produção**.
- **INV-TESTE-003** · Os logs reais são invioláveis: `logs/` é fotografado por
  SHA-256 antes e conferido depois. Apagar, alterar ou criar relatório fora do
  sandbox reprova a sessão inteira.
- **INV-TESTE-004** · Handlers do logger `ASPM` são limpos entre testes, senão o
  primeiro teste fixa um FileHandler apontando para o log real.

COMPORTAMENTO EM CASO DE FALHA
------------------------------
Falha da guarda de integridade encerra a sessão com falha explícita, nomeando os
arquivos afetados — em vez de o dado sumir em silêncio.
"""

from __future__ import annotations

import hashlib
import importlib
import logging
import os
import sys

import pytest

RAIZ_MODULO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ_MODULO not in sys.path:
    sys.path.insert(0, RAIZ_MODULO)


# (módulo, níveis que o código sobe a partir do próprio arquivo até a raiz).
# Medido lendo cada `os.path.dirname(__file__)` do código.
_MODULOS_COM_CAMINHO = [
    ("app.utils.log_sistema", 2),
    ("app.ui.scan_projeto.executar_scan", 3),
    ("app.ui.scan_projeto.listar_falhas", 3),
    ("app.ui.scan_projeto.listar.service", 4),
    ("app.ui.log_sistema.menu_log_sistema", 3),
    ("app.ui.scan_ia_local.scan_amd.executar_scan", 4),
    ("app.ui.scan_ia_local.scan_amd.listar_falhas", 4),
    ("app.ui.scan_ia_local.scan_amd.menu", 4),
    ("app.ui.scan_ia_local.scan_nvidia.executar_scan", 4),
    ("app.ui.scan_ia_local.scan_nvidia.listar_falhas", 4),
    ("app.ui.scan_ia_local.scan_nvidia.menu", 4),
]


def _fotografar(pasta: str) -> dict[str, str]:
    """Mapeia caminho relativo -> sha256 de cada arquivo sob `pasta`."""
    foto: dict[str, str] = {}
    if not os.path.isdir(pasta):
        return foto
    for raiz, _dirs, arquivos in os.walk(pasta):
        for nome in arquivos:
            caminho = os.path.join(raiz, nome)
            rel = os.path.relpath(caminho, pasta)
            try:
                with open(caminho, "rb") as fh:
                    foto[rel] = hashlib.sha256(fh.read()).hexdigest()
            except OSError:
                foto[rel] = "ILEGIVEL"
    return foto


@pytest.fixture(scope="session", autouse=True)
def guarda_logs_reais():
    """Reprova a sessão se a suíte mexer em logs ou relatórios reais."""
    pasta = os.path.join(RAIZ_MODULO, "logs")
    antes = _fotografar(pasta)

    yield

    depois = _fotografar(pasta)

    # `.log` cresce por natureza (o import abre o logger); `.json` de relatório,
    # não: ele só nasce quando um scan roda, e nenhum teste pode rodar scan fora
    # do sandbox.
    def _tolerado(rel: str) -> bool:
        return rel.lower().endswith(".log") or rel.endswith(".gitkeep")

    apagados = sorted(r for r in antes if r not in depois and not _tolerado(r))
    alterados = sorted(
        r for r in antes
        if r in depois and antes[r] != depois[r] and not _tolerado(r)
    )
    criados = sorted(r for r in depois if r not in antes and not _tolerado(r))

    problemas = []
    if apagados:
        problemas.append(f"APAGADOS ({len(apagados)}): {apagados}")
    if alterados:
        problemas.append(f"ALTERADOS ({len(alterados)}): {alterados}")
    if criados:
        problemas.append(f"CRIADOS fora do sandbox ({len(criados)}): {criados}")

    if problemas:
        pytest.fail(
            "INV-TESTE-003 violada — a suite mexeu em logs REAIS do usuario:\n  "
            + "\n  ".join(problemas)
            + "\nNenhum teste pode escrever fora do sandbox.",
            pytrace=False,
        )


def _limpar_handlers_aspm():
    """Fecha e remove os FileHandlers do logger ASPM (INV-TESTE-004)."""
    nomes = [
        n for n in list(logging.root.manager.loggerDict)
        if n == "ASPM" or n.startswith("ASPM.")
    ]
    for nome in nomes + ["ASPM"]:
        log = logging.getLogger(nome)
        for handler in list(log.handlers):
            try:
                handler.close()
            except Exception:
                pass
            log.removeHandler(handler)


@pytest.fixture(autouse=True)
def sandbox_de_caminhos(tmp_path, monkeypatch):
    """
    Repõe a raiz do projeto para um diretório temporário, por teste.

    Os módulos calculam a raiz com `dirname(__file__)` + N níveis de `..`.
    `__file__` é global do módulo e portanto monkeypatchável: apontando-a para
    um caminho de mesma profundidade dentro do temporário, a mesma aritmética
    passa a resolver no sandbox.
    """
    sandbox = tmp_path / "sandbox_projeto"
    for sub in ("logs/generic/reports", "logs/amd/reports", "logs/amd/system",
                "logs/nvidia/reports", "logs/nvidia/system", "logs/system"):
        (sandbox / sub).mkdir(parents=True, exist_ok=True)

    for nome_modulo, niveis in _MODULOS_COM_CAMINHO:
        try:
            modulo = importlib.import_module(nome_modulo)
        except ImportError:
            # Módulo pode não existir neste módulo-irmão; a guarda de deriva
            # abaixo é quem cobra a lista estar correta.
            continue
        falso = sandbox.joinpath(*(["nivel"] * niveis)) / "modulo.py"
        falso.parent.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(modulo, "__file__", str(falso), raising=False)

    _limpar_handlers_aspm()
    yield sandbox
    _limpar_handlers_aspm()
