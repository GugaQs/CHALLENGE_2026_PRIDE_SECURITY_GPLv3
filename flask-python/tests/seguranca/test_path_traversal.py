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
Path traversal e leitura arbitrária de arquivo.

PROPÓSITO DE NEGÓCIO
--------------------
Quatro rotas desta aplicação montam um caminho de disco a partir de entrada do
usuário: `/documentacao/?doc=`, `/documentacao/arquivo?file=`,
`/logs/ver/<path>` e `/scan/logs/sistema/<path>`. Nenhuma delas exige
autenticação. Se qualquer uma escapar da pasta que deveria confinar, a
aplicação vira um leitor de arquivos da máquina de quem a executa.

MÉTODO
------
Os vetores vêm da fixture `payloads_traversal`, compartilhada por todos os
testes de segurança: vetor novo entra em um lugar só e passa a valer em todas as
rotas. Cada rota é exercitada com todos, e o teste afirma o **efeito**
(não vazou conteúdo de fora, não caiu com 500), nunca o código de status
isoladamente — 404 e 302 são recusas válidas, 200 com conteúdo de fora não é.

INVARIANTES DO DOMÍNIO
----------------------
- INV-SEC-001 · Nenhuma rota devolve conteúdo de arquivo fora da sua pasta base.
- INV-SEC-002 · Entrada maliciosa é **recusada**, não derruba o processo: 500 é
  falha, porque expõe traceback e indica caminho não tratado.
- INV-SEC-003 · Metadados do repositório (`.git/`) nunca são servidos.

COMPORTAMENTO EM CASO DE FALHA
------------------------------
Falha aqui é achado de segurança, não teste vermelho comum: significa leitura
arbitrária de arquivo por HTTP sem autenticação.
"""

from __future__ import annotations

import os

import pytest

from tests.conftest import RAIZ_MODULO

pytestmark = [pytest.mark.seguranca, pytest.mark.integracao]


# Marcas de conteúdo que só existem FORA da pasta permitida. Se aparecerem no
# corpo da resposta, houve vazamento — isto é mais forte que olhar o status.
MARCAS_DE_VAZAMENTO = [
    b"root:x:0:0",          # /etc/passwd
    b"[fonts]",             # win.ini
    b"[extensions]",        # win.ini
    b"[mci extensions]",    # win.ini
]


def _vazou(corpo: bytes) -> str | None:
    for marca in MARCAS_DE_VAZAMENTO:
        if marca.lower() in corpo.lower():
            return marca.decode()
    return None


# ── INV-SEC-001 · Confinamento ───────────────────────────────────────────────

def test_documentacao_doc_nao_serve_arquivo_de_fora(client, payloads_traversal):
    """`/documentacao/?doc=` só renderiza `.md` de dentro do repositório."""
    for vetor in payloads_traversal:
        resposta = client.get("/documentacao/", query_string={"doc": vetor})
        assert resposta.status_code != 200, (
            f"vetor aceito por /documentacao/?doc=: {vetor!r}"
        )
        marca = _vazou(resposta.data)
        assert marca is None, f"vazou {marca!r} com {vetor!r}"


def test_documentacao_arquivo_nao_serve_arquivo_de_fora(client, payloads_traversal):
    """`/documentacao/arquivo?file=` não escapa da raiz do repositório."""
    for vetor in payloads_traversal:
        resposta = client.get("/documentacao/arquivo", query_string={"file": vetor})
        marca = _vazou(resposta.data)
        assert marca is None, (
            f"/documentacao/arquivo VAZOU {marca!r} com o vetor {vetor!r} "
            f"(status {resposta.status_code}, {len(resposta.data)} bytes)"
        )


def test_logs_ver_nao_serve_arquivo_de_fora(client_producao, payloads_traversal):
    """`/logs/ver/<path>` fica confinado a `logs/`."""
    for vetor in payloads_traversal:
        resposta = client_producao.get("/logs/ver/" + vetor)
        marca = _vazou(resposta.data)
        assert marca is None, f"/logs/ver VAZOU {marca!r} com {vetor!r}"


def test_scan_logs_sistema_nao_serve_arquivo_de_fora(client_producao, payloads_traversal):
    """`/scan/logs/sistema/<path>` fica confinado a `logs/`."""
    for vetor in payloads_traversal:
        resposta = client_producao.get("/scan/logs/sistema/" + vetor)
        marca = _vazou(resposta.data)
        assert marca is None, f"/scan/logs/sistema VAZOU {marca!r} com {vetor!r}"


def test_scan_logs_nome_nao_le_arquivo_de_fora(client_producao, payloads_traversal):
    """`/scan/logs/<nome_log>` recusa nome que não seja relatório da pasta."""
    for vetor in payloads_traversal:
        resposta = client_producao.get("/scan/logs/" + vetor)
        marca = _vazou(resposta.data)
        assert marca is None, f"/scan/logs VAZOU {marca!r} com {vetor!r}"


# ── INV-SEC-002 · Recusar sem derrubar ───────────────────────────────────────

@pytest.mark.parametrize(
    "molde",
    [
        # `/logs/ver/{}` NAO entra aqui: ela cai de verdade com caminho em outra
        # unidade (ValueError em os.path.commonpath). O defeito esta registrado
        # como achado confirmado em
        # tests/regressao/test_achados_auditoria.py::
        #   test_logs_ver_com_caminho_em_outro_drive_nao_derruba_a_rota
        # Quando for corrigido, acrescente "/logs/ver/{}" a esta lista.
        "/scan/logs/sistema/{}",
        "/scan/logs/{}",
    ],
)
def test_vetor_de_traversal_nao_derruba_a_rota(client_producao, payloads_traversal, molde):
    """
    Recusar é obrigatório; **cair** também é defeito.

    HTTP 500 numa entrada que o atacante controla expõe traceback e revela
    caminho não tratado. A resposta correta é recusa explícita.
    """
    quebrou = []
    for vetor in payloads_traversal:
        resposta = client_producao.get(molde.format(vetor))
        if resposta.status_code >= 500:
            quebrou.append((vetor, resposta.status_code))

    assert not quebrou, (
        f"{molde} devolveu 5xx (nao tratou a entrada):\n  "
        + "\n  ".join(f"{v!r} -> {s}" for v, s in quebrou)
    )


# ── INV-SEC-003 · Metadados do repositório ───────────────────────────────────

def test_git_nao_e_alcancavel_por_traversal(client_producao):
    """
    `.git/` fora da raiz permitida continua inalcançável.

    Nota: `.git/config` **por caminho direto** (sem `../`) É servido hoje — é um
    achado confirmado, registrado em
    `tests/regressao/test_achados_auditoria.py::test_metadados_do_git_nao_sao_servidos`.
    Este teste cobre o vetor complementar: chegar ao `.git` de FORA da raiz.
    """
    for alvo in ("../.git/config", "../../.git/config", "..\\.git\\config"):
        resposta = client_producao.get(
            "/documentacao/arquivo", query_string={"file": alvo}
        )
        assert resposta.status_code != 200, (
            f"/documentacao/arquivo escapou da raiz e serviu {alvo!r}"
        )


def test_documentacao_arquivo_nao_serve_codigo_fonte(client_producao):
    """
    A rota existe para servir imagem/artefato citado no Markdown, não código.

    Servir `.py` daria a qualquer visitante o fonte da aplicação — inclusive
    a `SECRET_KEY` padrão embutida em `app/web/app.py`.
    """
    for alvo in ("app/web/app.py", "requirements.txt", "app/utils/log_sistema.py"):
        resposta = client_producao.get(
            "/documentacao/arquivo", query_string={"file": alvo}
        )
        assert resposta.status_code != 200, (
            f"/documentacao/arquivo serviu codigo-fonte: {alvo!r}"
        )


# ── Controle positivo do instrumento ─────────────────────────────────────────

def test_controle_positivo_a_rota_de_arquivo_realmente_serve_algo(client):
    """
    Prova que os testes acima não passam por a rota estar simplesmente quebrada.

    Sem este controle, `/documentacao/arquivo` devolvendo 404 para TUDO faria
    todos os testes de traversal passarem — e o instrumento estaria cego.
    """
    # Um arquivo que legitimamente existe sob a raiz e é referenciado por docs.
    alvo = "Gemini_Generated_Image_qpglwoqpglwoqpgl.png"
    if not os.path.exists(os.path.join(RAIZ_MODULO, "..", alvo)):
        pytest.skip(f"arquivo de controle ausente: {alvo}")

    resposta = client.get("/documentacao/arquivo", query_string={"file": alvo})
    assert resposta.status_code == 200, (
        "a rota nao serve nem o arquivo legitimo — os testes de traversal acima "
        "estariam passando por cegueira do instrumento, nao por protecao"
    )
