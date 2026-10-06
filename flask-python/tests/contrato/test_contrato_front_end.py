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
Contrato entre a Content-Security-Policy, os templates, o CSS e o JavaScript.

PROPÓSITO DE NEGÓCIO
--------------------
A CSP desta aplicação (`script-src 'self'`, `default-src 'self'`) decide o que o
front-end pode fazer, e **viola em silêncio**: script bloqueado não emite erro na
tela, a página carrega inteira e o comportamento simplesmente não acontece. Foi
assim que os diagramas Mermaid de `/documentacao/` e os botões do terminal de log
ficaram inertes — os dois eram `<script>` inline, um deles importando de CDN.

Estes testes transformam essa regra, que hoje só existe em prosa na documentação,
em **guarda executável**. Documento e hash provam que a regra foi lida; só guarda
executável prova que ela foi aplicada.

INVARIANTES DO DOMÍNIO
----------------------
- INV-FE-001 · Nenhum template contém `<script>` com corpo inline.
- INV-FE-002 · Nenhum recurso externo é referenciado, salvo os hosts que a
  própria CSP declara.
- INV-FE-003 · Todo gancho de DOM que o `app.js` consulta existe nos templates
  ou no CSS. Renomear um deles quebra a interface sem erro visível.
- INV-FE-004 · `style.css` não usa `px`, para que a interface acompanhe o
  tamanho de fonte configurado pela pessoa no navegador.
- INV-FE-005 · CSS e JS servidos pelo layout carregam `?v=`, senão o navegador
  serve a versão em cache e um deploy parece não ter efeito.

COMPORTAMENTO EM CASO DE FALHA
------------------------------
Falha aqui significa que a interface vai quebrar no navegador real sem quebrar
nenhum teste de rota — status HTTP 200 continua sendo devolvido. Tratar como
defeito funcional, não como estilo.
"""

from __future__ import annotations

import os
import re

import pytest

from tests.conftest import RAIZ_MODULO

pytestmark = pytest.mark.contrato

TEMPLATES = os.path.join(RAIZ_MODULO, "app", "web", "templates")
ESTATICOS = os.path.join(RAIZ_MODULO, "app", "web", "static")
CSS = os.path.join(ESTATICOS, "css", "style.css")
APP_JS = os.path.join(ESTATICOS, "js", "app.js")

# Hosts externos que a CSP declara explicitamente. Qualquer outro é violação.
HOSTS_PERMITIDOS = {"img.shields.io"}


def _templates():
    for raiz, _dirs, arquivos in os.walk(TEMPLATES):
        for nome in arquivos:
            if nome.endswith(".html"):
                yield os.path.join(raiz, nome)


def _ler(caminho: str) -> str:
    with open(caminho, encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def _sem_comentarios_css(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


# ── INV-FE-001 · Nenhum script inline ────────────────────────────────────────

@pytest.mark.seguranca
def test_nenhum_template_tem_script_inline():
    """
    `script-src 'self'` sem `'unsafe-inline'` bloqueia bloco `<script>` com corpo.

    Um `<script src=...>` é permitido; um `<script>codigo</script>` não.
    """
    inline = re.compile(
        r"<script(?![^>]*\bsrc\s*=)[^>]*>(?P<corpo>.*?)</script>",
        re.S | re.I,
    )
    ofensores = []
    for caminho in _templates():
        for m in inline.finditer(_ler(caminho)):
            corpo = m.group("corpo").strip()
            if corpo:  # `<script></script>` vazio é inofensivo
                rel = os.path.relpath(caminho, RAIZ_MODULO)
                ofensores.append(f"{rel}: {corpo[:70]!r}")

    assert not ofensores, (
        "Script INLINE em template — a CSP (`script-src 'self'`) bloqueia isto no "
        "navegador, em silencio, e o comportamento some sem erro:\n  "
        + "\n  ".join(ofensores)
        + "\nMova o codigo para um arquivo em app/web/static/js/ e referencie por src."
    )


# ── INV-FE-002 · Nenhum recurso externo ──────────────────────────────────────

@pytest.mark.seguranca
def test_nenhum_recurso_externo_alem_do_que_a_csp_declara():
    """CDN, webfont e import remoto não carregam sob `default-src 'self'`."""
    url = re.compile(r"""(?:src|href)\s*=\s*["'](https?://[^"']+)["']""", re.I)
    ofensores = []

    for caminho in _templates():
        texto = _ler(caminho)
        for endereco in url.findall(texto):
            host = re.sub(r"^https?://", "", endereco).split("/")[0].lower()
            if host in HOSTS_PERMITIDOS:
                continue
            # Link de navegação (<a href>) não é carregamento de recurso.
            if re.search(
                r"<a\b[^>]*href\s*=\s*[\"']" + re.escape(endereco),
                texto,
                re.I,
            ):
                continue
            rel = os.path.relpath(caminho, RAIZ_MODULO)
            ofensores.append(f"{rel}: {endereco}")

    css = _sem_comentarios_css(_ler(CSS))
    if re.search(r"@import|url\(\s*['\"]?https?:", css):
        ofensores.append("style.css: @import ou url() externa")

    assert not ofensores, (
        "Recurso EXTERNO referenciado — a CSP (`default-src 'self'`) recusa, e a "
        "pagina perde a funcionalidade sem avisar:\n  "
        + "\n  ".join(ofensores)
        + "\nSirva o arquivo localmente em app/web/static/."
    )


# ── INV-FE-003 · Ganchos de DOM que o JS consulta ────────────────────────────

def _ganchos_do_js() -> tuple[set[str], set[str]]:
    """Extrai (classes, ids) que o app.js consulta no DOM."""
    js = _ler(APP_JS)
    classes = set()
    ids = set()

    for seletor in re.findall(r"""querySelector(?:All)?\(\s*["'`]([^"'`]+)["'`]""", js):
        classes.update(re.findall(r"\.([A-Za-z_][\w-]*)", seletor))
        ids.update(re.findall(r"#([A-Za-z_][\w-]*)", seletor))

    ids.update(re.findall(r"""getElementById\(\s*["']([^"']+)["']""", js))
    classes.update(
        re.findall(r"""classList\.(?:add|remove|toggle|contains)\(\s*["']([^"']+)["']""", js)
    )
    return classes, ids


def test_ganchos_de_classe_do_js_existem_no_css_ou_nos_templates():
    """
    Toda classe que o `app.js` procura precisa existir em algum lugar.

    Renomear uma classe no CSS e esquecer o JS (ou vice-versa) não gera erro:
    `querySelectorAll` devolve lista vazia e o recurso some em silêncio.
    """
    classes, _ids = _ganchos_do_js()
    css = _sem_comentarios_css(_ler(CSS))
    html = " ".join(_ler(c) for c in _templates())

    orfas = [
        c for c in sorted(classes)
        if f".{c}" not in css and c not in html
    ]
    assert not orfas, (
        "Classes que o app.js consulta e que nao existem nem no CSS nem em "
        f"template: {orfas}. O querySelector devolve vazio e o comportamento "
        "some sem erro."
    )


def test_ganchos_de_id_do_js_existem_nos_templates_ou_sao_criados_pelo_proprio_js():
    """Todo id consultado pelo JS existe em template ou é criado pelo próprio JS."""
    _classes, ids = _ganchos_do_js()
    html = " ".join(_ler(c) for c in _templates())
    js = _ler(APP_JS)

    # Ids montados dinamicamente (variável) não são verificáveis estaticamente.
    dinamicos = {"idCampo"}

    orfaos = [
        i for i in sorted(ids)
        if i not in dinamicos
        and f'id="{i}"' not in html
        and f"'{i}'" not in js.replace(f'getElementById("{i}")', "")
        and f'id="{i}"' not in js
    ]
    assert not orfaos, (
        f"Ids consultados pelo app.js e ausentes dos templates: {orfaos}"
    )


def test_classe_oculto_e_o_unico_mecanismo_de_visibilidade_do_js():
    """
    `.oculto` é o contrato de esconder/mostrar entre JS e CSS.

    Se o CSS deixar de defini-la, `classList.add("oculto")` deixa de esconder
    qualquer coisa — o painel de progresso passaria a aparecer sempre.
    """
    css = _sem_comentarios_css(_ler(CSS))
    assert ".oculto" in css, "o CSS precisa definir .oculto"
    regra = re.search(r"\.oculto\s*\{([^}]*)\}", css)
    assert regra, "regra .oculto nao encontrada"
    assert "display" in regra.group(1) and "none" in regra.group(1), (
        f".oculto precisa esconder de fato; hoje: {regra.group(1).strip()!r}"
    )


def test_tooltip_global_continua_posicionado_em_absolute():
    """
    O `app.js` escreve `left`/`top` em coordenadas de DOCUMENTO
    (`rect + window.scrollX/Y`). Com `position: fixed`, que usa coordenadas de
    viewport, a dica apareceria deslocada ao rolar a página.
    """
    css = _sem_comentarios_css(_ler(CSS))
    regra = re.search(r"\.tooltip-global\s*\{([^}]*)\}", css)
    assert regra, "regra .tooltip-global nao encontrada"
    assert re.search(r"position\s*:\s*absolute", regra.group(1)), (
        "tooltip-global precisa de position: absolute — o JS calcula a posicao "
        "em coordenadas de documento."
    )


# ── INV-FE-004 · Unidades relativas ──────────────────────────────────────────

def test_style_css_nao_usa_px():
    """
    Medida em `px` ignora o tamanho de fonte que a pessoa configurou no
    navegador. A folha usa `rem`, `%`, `clamp()`, `em` e `vh`.

    Exceção declarada: dentro de `@media print`, unidade física (`pt`) é correta.
    """
    css = _sem_comentarios_css(_ler(CSS))
    ocorrencias = re.findall(r"(?<![\w-])-?[\d.]+px\b", css)
    assert not ocorrencias, (
        f"{len(ocorrencias)} medida(s) em px no style.css: {ocorrencias[:12]}. "
        "Use rem para tipografia/espacamento, % para largura de layout."
    )


def test_media_queries_usam_em_e_nao_px():
    """Ponto de quebra em `em` acompanha o zoom de fonte; em `px`, não."""
    css = _sem_comentarios_css(_ler(CSS))
    consultas = re.findall(r"@media[^{]+", css)
    com_px = [q.strip() for q in consultas if re.search(r"[\d.]+px", q)]
    assert not com_px, f"media queries em px: {com_px}"


def test_paleta_de_texto_passa_contraste_wcag_aa():
    """
    Cada token de texto contra cada superfície, medido — não afirmado.

    AA para texto normal exige 4.5:1. Isto é acessibilidade, e é a razão pela
    qual `--txt-4` foi clareado: em #61798C ele dava 3.68:1 sobre `--sup-2` e
    pinta a data em `.log-data`, que é conteúdo.
    """
    css = _ler(CSS)
    tok = dict(re.findall(r"(--[\w-]+):\s*(#[0-9A-Fa-f]{6});", css))

    def canal(v: int) -> float:
        c = v / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    def luminancia(hexa: str) -> float:
        h = hexa.lstrip("#")
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        return 0.2126 * canal(r) + 0.7152 * canal(g) + 0.0722 * canal(b)

    def razao(a: str, b: str) -> float:
        la, lb = luminancia(a), luminancia(b)
        return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

    superficies = ["--deep-space", "--sup-0", "--sup-1", "--sup-2"]
    textos = ["--txt-1", "--txt-2", "--txt-3", "--txt-4", "--acento",
              "--ok", "--atencao", "--perigo", "--info", "--v-fin-gold"]

    faltando = [t for t in textos + superficies if t not in tok]
    assert not faltando, f"tokens de cor ausentes do :root: {faltando}"

    reprovados = []
    for t in textos:
        for s in superficies:
            r = razao(tok[t], tok[s])
            if r < 4.5:
                reprovados.append(f"{t} sobre {s} = {r:.2f}:1")

    assert not reprovados, (
        "Pares abaixo de 4.5:1 (WCAG AA para texto normal):\n  "
        + "\n  ".join(reprovados)
    )


# ── INV-FE-005 · Versionamento de asset ──────────────────────────────────────

def test_layout_versiona_css_e_js():
    """
    Sem `?v=`, o navegador serve o asset em cache e o deploy parece sem efeito.

    O helper `asset_version` já existia em `app/web/app.py` e ficou sem uso até
    a interface mudar e não aparecer para ninguém.
    """
    base = _ler(os.path.join(TEMPLATES, "base.html"))
    for asset in ("css/style.css", "js/app.js"):
        linha = re.search(
            re.escape(asset) + r"['\"]\s*\)\s*\}\}(?P<resto>[^\"'>]*)", base
        )
        assert linha, f"{asset} nao referenciado em base.html"
        assert "?v=" in linha.group("resto"), (
            f"{asset} servido sem ?v= — o navegador vai manter a versao em cache"
        )


def test_csp_declarada_pela_app_bate_com_o_que_o_front_end_usa(client):
    """
    A política que a aplicação envia é a mesma que estes testes assumem.

    Se alguém acrescentar `'unsafe-inline'` em `script-src`, as guardas acima
    passam a proteger contra uma regra que não existe mais — e viram teatro.
    """
    csp = client.get("/").headers.get("Content-Security-Policy", "")
    assert csp, "a aplicacao precisa enviar Content-Security-Policy"

    diretivas = {
        parte.strip().split(" ")[0]: parte.strip()
        for parte in csp.split(";") if parte.strip()
    }
    assert "script-src" in diretivas, f"CSP sem script-src: {csp}"
    assert "'unsafe-inline'" not in diretivas["script-src"], (
        "script-src ganhou 'unsafe-inline' — as guardas de script inline deste "
        f"arquivo passam a nao proteger nada. CSP atual: {csp}"
    )
    assert "default-src" in diretivas and "'self'" in diretivas["default-src"]
