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

"""Rotas de documentacao renderizada em HTML dentro da web app."""

from pathlib import Path
import html
import re

import markdown
from flask import Blueprint, abort, render_template, request, send_file, url_for


documentacao_bp = Blueprint("documentacao", __name__, url_prefix="/documentacao")

_RE_LINK_MD = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_RE_URL_ABSOLUTA = re.compile(r"^(https?:)?//", re.I)
_RE_MERMAID = re.compile(
    r"<pre><code class=\"language-mermaid\">(.*?)</code></pre>",
    re.S,
)


def _repo_root():
    return Path(__file__).resolve().parents[4]


def _lista_docs():
    raiz = _repo_root()
    docs = [
        "README.md",
        "api_python/README.md",
        "api_python/tests/README_TESTES.md",
        "flask-python/README.md",
        "flask-python/tests/README_TESTES.md",
        "documentacao/README.md",
        "documentacao/01-visao-geral.md",
        "documentacao/02-instalacao-execucao.md",
        "documentacao/03-arquitetura-tecnica.md",
        "documentacao/04-modulos-responsabilidades.md",
        "documentacao/05-operacao-manutencao.md",
        "documentacao/06-troubleshooting-faq.md",
        "documentacao/07-roadmap.md",
        "documentacao/08-ia-local-amd-nvidia.md",
        "documentacao/09-equipe.md",
        "documentacao/10-repositorio-oficial.md",
        "documentacao/11-indice-api-python.md",
        "documentacao/12-indice-flask-python.md",
    ]

    saida = []
    for rel in docs:
        if (raiz / rel).exists():
            saida.append(rel)
    return saida


def _normalizar_doc(rel):
    if not rel:
        return "flask-python/README.md"
    rel = rel.replace("\\", "/").strip().lstrip("/")
    return rel


def _resolver_doc(rel):
    raiz = _repo_root()
    rel = _normalizar_doc(rel)
    caminho = (raiz / rel).resolve()
    if raiz not in caminho.parents and caminho != raiz:
        return None, None
    if not caminho.exists() or caminho.suffix.lower() != ".md":
        return None, None
    return caminho, rel


def _resolver_arquivo(rel):
    raiz = _repo_root()
    rel = _normalizar_doc(rel)
    caminho = (raiz / rel).resolve()
    if raiz not in caminho.parents and caminho != raiz:
        return None, None
    if not caminho.exists() or not caminho.is_file():
        return None, None
    return caminho, rel


def _titulo_doc(caminho, fallback):
    try:
        conteudo = caminho.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return fallback
    for linha in conteudo.splitlines():
        if linha.strip().startswith("#"):
            return linha.strip().lstrip("#").strip()
    return fallback


def _converter_links_markdown(texto, doc_atual):
    base = Path(doc_atual).parent

    def _sub(m):
        label = m.group(1).strip()
        alvo = m.group(2).strip()
        if alvo.startswith("#") or _RE_URL_ABSOLUTA.match(alvo):
            return f"[{label}]({alvo})"

        alvo_limpo = alvo.split("#", 1)[0].split("?", 1)[0].replace("\\", "/")
        if alvo_limpo.lower().endswith(".md"):
            destino = (base / alvo_limpo).as_posix()
            return f"[{label}]({url_for('documentacao.pagina_documentacao', doc=destino)})"

        destino = (base / alvo_limpo).as_posix()
        return f"[{label}]({url_for('documentacao.arquivo_documentacao', file=destino)})"

    return _RE_LINK_MD.sub(_sub, texto)


def _md_para_html(conteudo, doc_atual):
    conteudo = _converter_links_markdown(conteudo, doc_atual)
    html_doc = markdown.markdown(
        conteudo,
        extensions=[
            "extra",
            "fenced_code",
            "tables",
            "sane_lists",
            "toc",
            "md_in_html",
        ],
        output_format="html5",
    )

    def _trocar_mermaid(match):
        bloco = html.unescape(match.group(1)).strip()
        return f'<div class="mermaid">{bloco}</div>'

    return _RE_MERMAID.sub(_trocar_mermaid, html_doc)


@documentacao_bp.route("/", methods=["GET"])
def pagina_documentacao():
    docs = _lista_docs()
    doc_param = request.args.get("doc", default="flask-python/README.md", type=str)
    caminho, doc_rel = _resolver_doc(doc_param)
    if not caminho:
        abort(404)

    conteudo = caminho.read_text(encoding="utf-8", errors="ignore")
    html_doc = _md_para_html(conteudo, doc_rel)

    menu_docs = []
    for rel in docs:
        arq, _ = _resolver_doc(rel)
        if not arq:
            continue
        menu_docs.append(
            {
                "rel": rel,
                "titulo": _titulo_doc(arq, Path(rel).name),
                "url": url_for("documentacao.pagina_documentacao", doc=rel),
                "ativo": rel == doc_rel,
            }
        )

    return render_template(
        "documentacao/documentacao.html",
        titulo_pagina=_titulo_doc(caminho, Path(doc_rel).name),
        doc_rel=doc_rel,
        conteudo_html=html_doc,
        menu_docs=menu_docs,
    )


@documentacao_bp.route("/arquivo", methods=["GET"])
def arquivo_documentacao():
    """Serve arquivo local referenciado por markdown (imagens/artefatos)."""
    rel = request.args.get("file", default="", type=str)
    caminho, _ = _resolver_arquivo(rel)
    if not caminho:
        abort(404)
    return send_file(caminho)
