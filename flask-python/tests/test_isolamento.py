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
Calibração do próprio instrumento: prova que o isolamento do `conftest.py` isola.

PROPÓSITO DE NEGÓCIO
--------------------
O `conftest.py` promete que nenhum teste escreve em `logs/` real, apaga relatório
do usuário ou sai para a rede. Promessa não é prova. Este módulo é o
**controle positivo** do sandbox: ele exercita cada escritor da aplicação e
afirma que o arquivo apareceu *dentro* do temporário e *não* na árvore real.

Por que isto existe, e o prejuízo que o originou: numa auditoria anterior deste
mesmo projeto, agentes exercitaram a rota `POST /scan/logs/limpar` contra a pasta
real e apagaram relatórios de scan que o `.gitignore` impedia de recuperar. Uma
guarda que nunca foi vista pegando o caso doente não prova nada — então aqui ela
é vista pegando.

INVARIANTES DO DOMÍNIO
----------------------
- Todo escritor conhecido resolve caminho para dentro do sandbox.
- A lista `_MODULOS_COM_CAMINHO` do conftest cobre **todos** os módulos que
  derivam a raiz do projeto de `__file__`; se alguém acrescentar um novo escritor
  e esquecer de registrá-lo, `test_sandbox_cobre_todos_os_escritores` reprova.
- A rede está fechada.

COMPORTAMENTO EM CASO DE FALHA
------------------------------
Falha aqui invalida a suíte inteira: significa que os demais testes podem estar
escrevendo na árvore real. Tratar como bloqueio, não como teste vermelho comum.
"""

from __future__ import annotations

import os
import re
import socket

import pytest

from tests.conftest import RAIZ_MODULO, _MODULOS_COM_CAMINHO


LOGS_REAIS = os.path.join(RAIZ_MODULO, "logs")


def _dentro(caminho: str, pasta: str) -> bool:
    """True se `caminho` está sob `pasta` (comparação canônica)."""
    try:
        return os.path.commonpath(
            [os.path.realpath(caminho), os.path.realpath(pasta)]
        ) == os.path.realpath(pasta)
    except ValueError:
        # Drives diferentes no Windows — logo, não está dentro.
        return False


# ── Escritores de relatório ──────────────────────────────────────────────────

def test_scan_generico_grava_no_sandbox_e_nao_no_real(sandbox_de_caminhos):
    """`salvar_log_json` cai em <sandbox>/logs/generic/reports, não no real."""
    from app.ui.scan_projeto.executar_scan import salvar_log_json

    caminho = salvar_log_json({"controle": "positivo"})

    assert os.path.isfile(caminho), "o arquivo deveria existir"
    assert _dentro(caminho, str(sandbox_de_caminhos)), (
        f"gravou FORA do sandbox: {caminho}"
    )
    assert not _dentro(caminho, LOGS_REAIS), (
        f"gravou na arvore REAL de logs: {caminho}"
    )


@pytest.mark.parametrize(
    "modulo,funcao,subpasta",
    [
        ("app.ui.scan_ia_local.scan_amd.executar_scan", "salvar_log_json_amd", "amd"),
        ("app.ui.scan_ia_local.scan_nvidia.executar_scan", "salvar_log_json_nvidia", "nvidia"),
    ],
)
def test_motores_gpu_gravam_no_sandbox(sandbox_de_caminhos, modulo, funcao, subpasta):
    """Motores AMD e NVIDIA também respeitam o sandbox."""
    import importlib

    salvar = getattr(importlib.import_module(modulo), funcao)
    caminho = salvar({"controle": "positivo"})

    assert os.path.isfile(caminho)
    assert _dentro(caminho, str(sandbox_de_caminhos)), f"fora do sandbox: {caminho}"
    assert not _dentro(caminho, LOGS_REAIS), f"na arvore real: {caminho}"
    assert os.path.join("logs", subpasta, "reports") in caminho


def test_logger_central_grava_no_sandbox(sandbox_de_caminhos):
    """O FileHandler do logger ASPM aponta para dentro do sandbox."""
    import logging

    from app.utils.log_sistema import get_logger

    log = get_logger("prova_isolamento")
    log.info("linha de controle positivo")

    handlers = [
        h for h in logging.getLogger("ASPM").handlers
        if isinstance(h, logging.FileHandler)
    ]
    assert handlers, "o logger ASPM deveria ter um FileHandler"

    for handler in handlers:
        assert _dentro(handler.baseFilename, str(sandbox_de_caminhos)), (
            f"logger apontando FORA do sandbox: {handler.baseFilename}"
        )
        assert not _dentro(handler.baseFilename, LOGS_REAIS), (
            f"logger apontando para o log REAL: {handler.baseFilename}"
        )


def test_servico_web_resolve_raiz_no_sandbox(sandbox_de_caminhos):
    """`scan_service.obter_raiz_projeto()` devolve o sandbox."""
    from app.web.services import scan_service

    raiz = scan_service.obter_raiz_projeto()
    assert _dentro(raiz, str(sandbox_de_caminhos)), f"raiz fora do sandbox: {raiz}"


# ── Rede ─────────────────────────────────────────────────────────────────────

def test_rede_esta_bloqueada():
    """Qualquer tentativa de conexão é recusada de imediato."""
    with pytest.raises(ConnectionRefusedError):
        socket.create_connection(("127.0.0.1", 1234), timeout=1)


def test_status_lm_studio_trata_rede_fechada_sem_estourar():
    """
    Com a rede fechada, a aplicação devolve status offline em vez de exceção.

    Este é o caminho de erro REAL da aplicação sendo exercitado — não contornado.
    É também a prova de que o bloqueio de rede não quebra a suíte: a página
    `/ia-local/` chama esta função a cada GET.
    """
    from app.web.services.ia_local_service import status_lm_studio

    status = status_lm_studio()

    # Afirma o CONTRATO (a chave `conectado`), nao uma substring do repr — que
    # foi o erro que deixou `test_auditoria_ia_local_filtra_por_severidade`
    # vermelho por meses neste mesmo projeto.
    assert isinstance(status, dict), f"esperado dict, veio {type(status).__name__}"
    assert "conectado" in status, f"contrato mudou: {status!r}"
    assert status["conectado"] is False, (
        f"com a rede bloqueada o LM Studio nao pode constar como conectado: {status!r}"
    )


def test_testar_conexao_gpu_trata_rede_fechada():
    """`testar_conexao_gpu` devolve falso/erro em vez de propagar exceção."""
    from app.ui.scan_ia_local.executar_scan_ia import testar_conexao_gpu

    resultado = testar_conexao_gpu()
    assert resultado is not None


# ── Guarda contra deriva: o sandbox cobre todos os escritores? ────────────────

def test_sandbox_cobre_todos_os_escritores():
    """
    Varre o código à procura de módulos que derivam a raiz do projeto de
    `__file__` e confere que **todos** estão registrados em `_MODULOS_COM_CAMINHO`.

    Sem esta guarda, um escritor novo nasceria fora do sandbox e voltaria a
    poluir (ou apagar) a árvore real sem ninguém perceber — que é exatamente a
    classe de falha que este arquivo existe para impedir.
    """
    registrados = {nome for nome, _ in _MODULOS_COM_CAMINHO}
    padrao = re.compile(
        r"os\.path\.(?:abspath|join)\([^)]*dirname\(__file__\)", re.S
    )
    # Só interessa quem usa o caminho para gravar log/relatório.
    interesse = re.compile(r'["\']logs["\']|erro_sistema|reports')

    faltando = []
    for raiz, dirs, arquivos in os.walk(os.path.join(RAIZ_MODULO, "app")):
        dirs[:] = [d for d in dirs if d not in {"__pycache__", ".venv"}]
        for nome in arquivos:
            if not nome.endswith(".py"):
                continue
            caminho = os.path.join(raiz, nome)
            texto = open(caminho, encoding="utf-8", errors="ignore").read()
            if not (padrao.search(texto) and interesse.search(texto)):
                continue
            modulo = (
                os.path.relpath(caminho, RAIZ_MODULO)
                .replace(os.sep, ".")
                .removesuffix(".py")
            )
            if modulo not in registrados:
                faltando.append(modulo)

    assert not faltando, (
        "Modulos que resolvem caminho de log a partir de __file__ e NAO estao no "
        "sandbox do conftest (_MODULOS_COM_CAMINHO):\n  "
        + "\n  ".join(sorted(faltando))
        + "\nAcrescente-os la, com o numero de niveis que o codigo sobe, senao "
          "eles gravam na arvore REAL durante os testes."
    )
