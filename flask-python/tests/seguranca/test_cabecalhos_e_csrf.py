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
Cabeçalhos de segurança e proteção CSRF.

PROPÓSITO DE NEGÓCIO
--------------------
Esta aplicação executa scans no disco da máquina de quem a roda e abre o
explorador de arquivos por requisição HTTP. Um POST forjado a partir de outra
aba do navegador é capaz de disparar essas ações. A proteção CSRF e os
cabeçalhos de resposta são a única barreira, já que não existe autenticação.

INVARIANTES DO DOMÍNIO
----------------------
- INV-SEC-010 · Toda resposta carrega os quatro cabeçalhos de endurecimento.
- INV-SEC-011 · Toda rota que altera estado exige token CSRF válido.
- INV-SEC-012 · A `SECRET_KEY` é lida do ambiente; o valor embutido no código
  serve só para desenvolvimento e nunca deve valer em produção.

COMPORTAMENTO EM CASO DE FALHA
------------------------------
Falha aqui é achado de segurança. Sem CSRF, qualquer página da internet aberta
no mesmo navegador consegue disparar um scan ou abrir o explorador de arquivos
na máquina da vítima.
"""

from __future__ import annotations

import os

import pytest

from tests.conftest import RAIZ_MODULO

pytestmark = [pytest.mark.seguranca, pytest.mark.integracao]


ROTAS_DE_LEITURA = ["/", "/scan/", "/ia-local/", "/logs/", "/sobre/",
                    "/documentacao/", "/modulos/containers"]


# ── INV-SEC-010 · Cabeçalhos ─────────────────────────────────────────────────

@pytest.mark.parametrize("rota", ROTAS_DE_LEITURA)
def test_cabecalhos_de_endurecimento_em_todas_as_paginas(client, rota):
    """Os quatro cabeçalhos saem em toda resposta, não só na home."""
    cabecalhos = client.get(rota).headers

    assert cabecalhos.get("X-Content-Type-Options") == "nosniff"
    assert cabecalhos.get("X-Frame-Options") == "SAMEORIGIN"
    assert cabecalhos.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert cabecalhos.get("Content-Security-Policy"), (
        f"{rota} respondeu sem Content-Security-Policy"
    )


@pytest.mark.parametrize("rota", ROTAS_DE_LEITURA)
def test_csp_e_identica_em_todas_as_rotas(client, rota):
    """
    Uma CSP que varia por rota é uma CSP que alguém vai relaxar numa página e
    esquecer. O `after_request` aplica a mesma política a tudo.
    """
    referencia = client.get("/").headers["Content-Security-Policy"]
    assert client.get(rota).headers["Content-Security-Policy"] == referencia


def test_csp_nao_permite_script_inline_nem_eval(client):
    """`'unsafe-inline'` ou `'unsafe-eval'` em `script-src` anulam a política."""
    csp = client.get("/").headers["Content-Security-Policy"]
    script_src = next(
        (p.strip() for p in csp.split(";") if p.strip().startswith("script-src")),
        "",
    )
    assert script_src, f"CSP sem script-src: {csp}"
    assert "'unsafe-inline'" not in script_src, script_src
    assert "'unsafe-eval'" not in script_src, script_src


def test_resposta_de_erro_tambem_carrega_os_cabecalhos(client_producao):
    """
    Página 404 é resposta como qualquer outra e precisa dos mesmos cabeçalhos.

    `after_request` roda para respostas de erro também; se um dia alguém mover
    o endurecimento para dentro de uma view, isto reprova.
    """
    resposta = client_producao.get("/rota-que-nao-existe-12345")
    assert resposta.status_code == 404
    assert resposta.headers.get("X-Content-Type-Options") == "nosniff"
    assert resposta.headers.get("Content-Security-Policy")


# ── INV-SEC-011 · CSRF ───────────────────────────────────────────────────────

ROTAS_QUE_ALTERAM_ESTADO = [
    "/scan/executar",
    "/scan/executar-assincrono",
    "/scan/selecionar-pasta",
    "/scan/logs/limpar",
    "/ia-local/executar",
    "/ia-local/executar-assincrono",
    "/ia-local/cognitivo",
    "/ia-local/cognitivo-assincrono",
    "/ia-local/reanalisar",
    "/ia-local/imprimir-parecer",
    "/modulos/containers/executar-assincrono",
    "/logs/abrir-pasta",
]


@pytest.mark.parametrize("rota", ROTAS_QUE_ALTERAM_ESTADO)
def test_post_sem_token_csrf_e_recusado(client_csrf, rota):
    """
    Nenhuma rota de escrita aceita POST sem token.

    Sem isto, uma página maliciosa aberta noutra aba dispara um scan, abre o
    explorador de arquivos ou **apaga os relatórios** (`/scan/logs/limpar`) na
    máquina de quem está com a aplicação no ar.
    """
    resposta = client_csrf.post(rota, data={}, follow_redirects=False)
    assert resposta.status_code in (400, 403), (
        f"{rota} aceitou POST sem token CSRF (HTTP {resposta.status_code}) — "
        "requisicao forjada de outra aba consegue disparar esta acao"
    )


def test_controle_positivo_com_token_a_requisicao_passa_do_csrf(client_csrf, app):
    """
    Prova que os testes acima não passam por a rota estar quebrada.

    Com token válido, a requisição precisa **ultrapassar** a camada CSRF. O que
    acontece depois (erro de validação de caminho, redirect) não importa aqui —
    importa não ser mais 400/403 de CSRF.
    """
    pagina = client_csrf.get("/scan/")
    corpo = pagina.data.decode("utf-8", errors="ignore")

    import re
    achado = re.search(r'name="csrf-token" content="([^"]+)"', corpo)
    assert achado, "a pagina nao publica o meta csrf-token"

    resposta = client_csrf.post(
        "/scan/executar",
        data={"caminho": "", "csrf_token": achado.group(1)},
        follow_redirects=False,
    )
    assert resposta.status_code not in (400, 403), (
        "com token valido a requisicao continuou sendo recusada pelo CSRF — "
        "os testes negativos acima estariam passando por cegueira"
    )


def test_meta_csrf_token_esta_presente_no_layout(client):
    """O `app.js` lê o token de `<meta name="csrf-token">` para os `fetch`."""
    corpo = client.get("/").data.decode("utf-8", errors="ignore")
    assert 'name="csrf-token"' in corpo, (
        "sem o meta, todo fetch POST do app.js perde o token e passa a ser "
        "recusado quando o CSRF estiver ligado"
    )


# ── INV-SEC-012 · Segredo ────────────────────────────────────────────────────

def test_secret_key_vem_do_ambiente_quando_definida(monkeypatch, sandbox_de_caminhos):
    """`FLASK_SECRET_KEY` tem precedência sobre o valor embutido."""
    monkeypatch.setenv("FLASK_SECRET_KEY", "chave-de-teste-vinda-do-ambiente")

    from app.web.app import create_app

    assert create_app().config["SECRET_KEY"] == "chave-de-teste-vinda-do-ambiente"


def test_chave_padrao_de_desenvolvimento_nao_vaza_para_o_html(client):
    """
    O valor embutido nunca pode aparecer numa resposta.

    Ele é previsível e versionado; se vazasse no HTML, qualquer visitante
    assinaria cookies e tokens CSRF válidos.
    """
    for rota in ROTAS_DE_LEITURA:
        corpo = client.get(rota).data
        assert b"aspm-pride-2026-dev" not in corpo, f"chave vazou em {rota}"


def test_nenhum_segredo_obvio_versionado_no_codigo_web():
    """
    Varredura simples por segredo embutido na camada web.

    Não substitui uma ferramenta dedicada — é uma rede de baixo custo contra o
    caso mais comum, que é chave de API colada no fonte durante um teste e
    esquecida no commit.
    """
    import re

    padroes = [
        re.compile(r"""(?:api[_-]?key|apikey)\s*=\s*["'][A-Za-z0-9_\-]{20,}["']""", re.I),
        re.compile(r"""sk-[A-Za-z0-9]{20,}"""),
        re.compile(r"""AKIA[0-9A-Z]{16}"""),
        re.compile(r"""(?:senha|password|passwd)\s*=\s*["'][^"']{8,}["']""", re.I),
    ]

    achados = []
    base = os.path.join(RAIZ_MODULO, "app", "web")
    for pasta, dirs, arquivos in os.walk(base):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for nome in arquivos:
            if not nome.endswith(".py"):
                continue
            caminho = os.path.join(pasta, nome)
            with open(caminho, encoding="utf-8", errors="ignore") as fh:
                texto = fh.read()
            for padrao in padroes:
                for m in padrao.finditer(texto):
                    rel = os.path.relpath(caminho, RAIZ_MODULO)
                    achados.append(f"{rel}: {m.group(0)[:48]}")

    assert not achados, "Possiveis segredos versionados:\n  " + "\n  ".join(achados)
