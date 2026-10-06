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
Resolução dos caminhos de log por hardware.

PROPÓSITO DE NEGÓCIO
--------------------
Cada motor de GPU escreve a própria trilha: AMD em `logs/amd/system/`, NVIDIA em
`logs/nvidia/system/`. Quem investiga um incidente precisa saber que o arquivo
está onde a interface diz que está — a tela de logs monta os atalhos a partir
desses caminhos.

HISTÓRICO — por que este arquivo foi reescrito
----------------------------------------------
A versão anterior chamava os dois loggers, imprimia `✅ Encontrado` ou
`❌ NÃO ENCONTRADO` e **não tinha uma única asserção**. Ela passava sempre:
com os logs no lugar, com os logs ausentes, e com a função de caminho
completamente quebrada. Pior, escrevia nos logs REAIS do projeto a cada
execução da suíte.

O teste agora afirma o efeito (o arquivo apareceu, no lugar certo, com a linha
que foi escrita) e roda dentro do sandbox do `conftest.py`.

INVARIANTES DO DOMÍNIO
----------------------
- `get_hardware_logger("amd")` grava em `logs/amd/system/sistema_amd.log`.
- `get_hardware_logger("nvidia")` grava em `logs/nvidia/system/sistema_nvidia.log`.
- Os dois são independentes: linha de um não aparece no arquivo do outro.

COMPORTAMENTO EM CASO DE FALHA
------------------------------
Falha aqui significa trilha de auditoria gravada no lugar errado — ou não
gravada. A tela de logs mostraria vazio sem explicar por quê.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.unidade


@pytest.mark.parametrize(
    "hardware,arquivo_esperado",
    [
        ("amd", "sistema_amd.log"),
        ("nvidia", "sistema_nvidia.log"),
    ],
)
def test_logger_de_hardware_grava_no_arquivo_certo(
    sandbox_de_caminhos, hardware, arquivo_esperado
):
    """O logger cria o arquivo no caminho esperado e a linha chega lá."""
    from app.utils.log_sistema import get_hardware_logger

    marca = f"linha de prova para {hardware}"
    log = get_hardware_logger(hardware)
    log.info(marca)

    for handler in log.handlers:
        handler.flush()

    esperado = sandbox_de_caminhos / "logs" / hardware / "system" / arquivo_esperado
    assert esperado.is_file(), (
        f"o logger {hardware} nao criou {esperado}; arquivos presentes: "
        f"{sorted(p.name for p in esperado.parent.glob('*')) if esperado.parent.is_dir() else 'pasta ausente'}"
    )

    conteudo = esperado.read_text(encoding="utf-8", errors="ignore")
    assert marca in conteudo, (
        f"a linha escrita nao chegou ao arquivo. Conteudo: {conteudo[:200]!r}"
    )


def test_loggers_de_hardware_sao_independentes(sandbox_de_caminhos):
    """Linha do AMD não pode aparecer no arquivo do NVIDIA, e vice-versa."""
    from app.utils.log_sistema import get_hardware_logger

    get_hardware_logger("amd").info("MARCA_EXCLUSIVA_AMD")
    get_hardware_logger("nvidia").info("MARCA_EXCLUSIVA_NVIDIA")

    for nome in ("amd", "nvidia"):
        for handler in get_hardware_logger(nome).handlers:
            handler.flush()

    base = sandbox_de_caminhos / "logs"
    texto_amd = (base / "amd" / "system" / "sistema_amd.log").read_text(
        encoding="utf-8", errors="ignore"
    )
    texto_nvidia = (base / "nvidia" / "system" / "sistema_nvidia.log").read_text(
        encoding="utf-8", errors="ignore"
    )

    assert "MARCA_EXCLUSIVA_AMD" in texto_amd
    assert "MARCA_EXCLUSIVA_NVIDIA" in texto_nvidia
    assert "MARCA_EXCLUSIVA_NVIDIA" not in texto_amd, (
        "linha do NVIDIA vazou para o arquivo do AMD"
    )
    assert "MARCA_EXCLUSIVA_AMD" not in texto_nvidia, (
        "linha do AMD vazou para o arquivo do NVIDIA"
    )


def test_pasta_base_de_logs_e_absoluta_e_termina_em_logs(sandbox_de_caminhos):
    """`_pasta_logs_api_python()` devolve caminho absoluto para `logs/`."""
    from app.utils.log_sistema import _pasta_logs_api_python

    pasta = _pasta_logs_api_python()
    assert os.path.isabs(pasta), f"caminho relativo: {pasta}"
    assert pasta.rstrip(os.sep).endswith("logs"), pasta


def test_subpasta_de_logs_e_concatenada_corretamente(sandbox_de_caminhos):
    """`_pasta_logs_api_python('amd')` desce um nível dentro de `logs/`."""
    from app.utils.log_sistema import _pasta_logs_api_python

    base = _pasta_logs_api_python()
    com_sub = _pasta_logs_api_python("amd")

    assert com_sub == os.path.join(base, "amd")


def test_logger_de_hardware_com_nome_desconhecido_nao_derruba(sandbox_de_caminhos):
    """
    Hardware fora de {amd, nvidia} não pode levantar exceção no meio de um scan.

    Documenta o comportamento atual: a função aceita qualquer string e cria a
    pasta correspondente. Se um dia passar a rejeitar, este teste avisa.
    """
    from app.utils.log_sistema import get_hardware_logger

    log = get_hardware_logger("intel")
    assert log is not None
    log.info("hardware desconhecido")
