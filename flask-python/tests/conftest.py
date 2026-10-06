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
Fixtures e isolamento da suíte de testes do módulo `flask-python`.

PROPÓSITO DE NEGÓCIO
--------------------
Este arquivo é o alicerce da suíte. Ele garante que rodar `pytest` seja uma
operação **segura e repetível** na máquina de quem desenvolve: nenhum teste
escreve nos logs reais do sistema, nenhum apaga relatório de scan do usuário e
nenhum sai para a rede. Antes dele, rodar a suíte deixava resíduo permanente em
`logs/`, podia sobrescrever um relatório real do usuário e gastava a maior parte
do tempo esperando o timeout de uma conexão ao LM Studio que não existe.

INVARIANTES DO DOMÍNIO
----------------------
- **INV-TESTE-001 · Nenhuma escrita fora do sandbox.** Todo caminho de log e de
  relatório resolvido durante os testes aponta para um diretório temporário.
  Garantido repontando o `__file__` dos módulos que derivam caminho dele — os
  cinco pontos onde a aplicação faz `os.path.dirname(__file__)` para achar a raiz
  do projeto. Isso isola sem exigir nenhuma alteração no código de produção.
- **INV-TESTE-002 · Nenhum acesso de rede.** `socket.socket.connect` é bloqueado.
  Um teste que dependa de serviço externo falha rápido e alto, em vez de passar
  por acidente quando o serviço está no ar e travar quando não está.
- **INV-TESTE-003 · Os relatórios reais do usuário são invioláveis.** Uma guarda
  de sessão fotografa `logs/` antes e confere depois. Se um teste apagar ou
  alterar um arquivo real, a sessão inteira **falha** — em vez de o dado sumir em
  silêncio, que foi exatamente o que aconteceu numa auditoria anterior.
- **INV-TESTE-004 · O logger não vaza entre testes.** O logger `ASPM` guarda
  handlers no registro global do `logging`; sem reset, o primeiro teste fixaria
  um FileHandler apontando para o log real e todos os seguintes escreveriam lá.

COMPORTAMENTO EM CASO DE FALHA
------------------------------
- Se o sandbox não puder ser criado, os testes falham na fixture — nunca caem
  silenciosamente de volta para os caminhos reais.
- Se a guarda de integridade detectar alteração em `logs/`, a sessão termina com
  falha explícita nomeando os arquivos afetados.
- O bloqueio de rede levanta `ConnectionRefusedError`, que é exatamente o que a
  aplicação já trata: o caminho de erro é exercitado de verdade, não contornado.
"""

from __future__ import annotations

import hashlib
import logging
import os
import socket
import sys

import pytest

# Permite `pytest` a partir da raiz do repositório ou de dentro de flask-python.
RAIZ_MODULO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ_MODULO not in sys.path:
    sys.path.insert(0, RAIZ_MODULO)


# ─────────────────────────────────────────────────────────────────────────────
# INV-TESTE-003 · Guarda de integridade dos logs reais
# ─────────────────────────────────────────────────────────────────────────────

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
    """
    Falha a sessão se qualquer teste apagar ou alterar um log/relatório real.

    Novos arquivos são tolerados e reportados — a aplicação legitimamente cria
    log ao ser importada. Apagar ou alterar arquivo pré-existente não é.
    """
    pasta = os.path.join(RAIZ_MODULO, "logs")
    antes = _fotografar(pasta)

    yield

    depois = _fotografar(pasta)

    # Arquivos `.log` crescem por natureza: o próprio import da aplicação abre o
    # logger. Relatório `.json`, não — ele só nasce quando um scan roda de
    # verdade, e nenhum teste pode rodar scan fora do sandbox.
    def _tolerado(rel: str) -> bool:
        return rel.lower().endswith(".log") or rel.endswith(".gitkeep")

    apagados = sorted(
        rel for rel in antes if rel not in depois and not _tolerado(rel)
    )
    alterados = sorted(
        rel for rel in antes
        if rel in depois and antes[rel] != depois[rel] and not _tolerado(rel)
    )
    # NOVOS relatórios também são violação. Esta checagem foi acrescentada
    # depois de um vazamento real: um teste de fuzz mandava `"."` como caminho,
    # que é um diretório VÁLIDO, e disparava um scan de verdade numa thread de
    # fundo. A thread sobrevivia ao teardown do sandbox e gravava três
    # relatórios de 1,2 MB no `logs/` real — e a guarda, que só olhava apagados
    # e alterados, deixava passar em silêncio.
    criados = sorted(
        rel for rel in depois if rel not in antes and not _tolerado(rel)
    )

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
            + "\nNenhum teste pode escrever fora do sandbox. Causa mais comum: "
              "um caminho VALIDO no corpo de um POST assincrono dispara scan "
              "real numa thread, que sobrevive ao teardown da fixture.",
            pytrace=False,
        )


# ─────────────────────────────────────────────────────────────────────────────
# INV-TESTE-002 · Bloqueio de rede
# ─────────────────────────────────────────────────────────────────────────────

class RedeBloqueadaNoTeste(ConnectionRefusedError):
    """Levantada quando um teste tenta abrir conexão de rede."""


@pytest.fixture(scope="session", autouse=True)
def sem_rede():
    """
    Bloqueia conexão de saída durante toda a sessão.

    Motivo medido: `status_lm_studio()` faz `requests.get(localhost:1234,
    timeout=2)` a cada GET de `/ia-local/`. Com o serviço fora do ar, a suite
    gastava a maior parte do tempo em timeout; com o serviço no ar, os testes
    passariam a depender do estado da maquina de quem roda. Bloquear resolve os
    dois: o caminho de erro (que a aplicacao ja trata) e exercitado de verdade e
    o resultado nao depende do ambiente.

    O `test_client` do Flask nao abre socket, entao as rotas continuam testaveis.
    """
    original = socket.socket.connect

    def recusar(self, endereco, *args, **kwargs):
        raise RedeBloqueadaNoTeste(
            f"Conexao de rede bloqueada pela suite de testes: {endereco!r}. "
            "Use monkeypatch para simular o servico externo."
        )

    socket.socket.connect = recusar
    try:
        yield
    finally:
        socket.socket.connect = original


# ─────────────────────────────────────────────────────────────────────────────
# INV-TESTE-001 e INV-TESTE-004 · Sandbox de caminhos e reset do logger
# ─────────────────────────────────────────────────────────────────────────────

# (módulo, quantos ".." o código sobe a partir do próprio arquivo para achar a
#  raiz do projeto). Medido lendo cada função; se o código mudar, o teste
#  `test_sandbox_cobre_todos_os_escritores` neste mesmo diretório acusa.
_MODULOS_COM_CAMINHO = [
    ("app.utils.log_sistema", 2),
    ("app.web.services.scan_service", 3),
    ("app.ui.scan_projeto.executar_scan", 3),
    ("app.ui.scan_projeto.listar_falhas", 3),
    ("app.ui.scan_projeto.listar.service", 4),
    ("app.ui.scan_ia_local.scan_amd.executar_scan", 4),
    ("app.ui.scan_ia_local.scan_amd.listar_falhas", 4),
    ("app.ui.scan_ia_local.scan_amd.menu", 4),
    ("app.ui.scan_ia_local.scan_nvidia.executar_scan", 4),
    ("app.ui.scan_ia_local.scan_nvidia.listar_falhas", 4),
    ("app.ui.scan_ia_local.scan_nvidia.menu", 4),
    ("app.ui.scan_ia_api.config_api", 3),
    ("app.ui.log_sistema.menu_log_sistema", 3),
]


def _limpar_handlers_aspm():
    """Fecha e remove os FileHandlers do logger ASPM (INV-TESTE-004)."""
    for nome in list(logging.root.manager.loggerDict):
        if nome == "ASPM" or nome.startswith("ASPM."):
            log = logging.getLogger(nome)
            for handler in list(log.handlers):
                try:
                    handler.close()
                except Exception:
                    pass
                log.removeHandler(handler)
    raiz = logging.getLogger("ASPM")
    for handler in list(raiz.handlers):
        try:
            handler.close()
        except Exception:
            pass
        raiz.removeHandler(handler)


@pytest.fixture(autouse=True)
def sandbox_de_caminhos(tmp_path, monkeypatch):
    """
    Repõe a raiz do projeto para um diretório temporário, por teste.

    COMO FUNCIONA, e por que não altera código de produção: os cinco módulos que
    gravam em disco calculam a raiz com `os.path.dirname(__file__)` seguido de N
    níveis de `..`. `__file__` é uma variável global do módulo, e portanto
    monkeypatchável. Apontando-a para um caminho equivalente dentro do sandbox, a
    mesma aritmética de caminho passa a resolver dentro do temporário.

    Devolve o caminho do sandbox, para o teste inspecionar o que foi gravado.
    """
    sandbox = tmp_path / "sandbox_projeto"
    for sub in ("logs/generic/reports", "logs/amd/reports", "logs/amd/system",
                "logs/nvidia/reports", "logs/nvidia/system", "logs/system",
                "logs/config"):
        (sandbox / sub).mkdir(parents=True, exist_ok=True)

    import importlib

    for nome_modulo, niveis in _MODULOS_COM_CAMINHO:
        modulo = importlib.import_module(nome_modulo)
        # Caminho fictício com a mesma profundidade do arquivo real, para que
        # `dirname(__file__) + "/.." * niveis` caia exatamente no sandbox.
        falso = sandbox.joinpath(*(["nivel"] * niveis)) / "modulo.py"
        falso.parent.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(modulo, "__file__", str(falso), raising=False)

    _limpar_handlers_aspm()
    yield sandbox
    _limpar_handlers_aspm()


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures de aplicação
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def app(sandbox_de_caminhos):
    """
    Aplicação Flask em modo de teste, já dentro do sandbox.

    Depende de `sandbox_de_caminhos` de propósito: `create_app()` chama
    `get_logger()` na criação, e sem o sandbox ativo o handler nasceria apontando
    para o log real.
    """
    from app.web.app import create_app

    aplicacao = create_app()
    aplicacao.config["TESTING"] = True
    aplicacao.config["WTF_CSRF_ENABLED"] = False
    return aplicacao


@pytest.fixture
def client(app):
    """Cliente HTTP de teste, sem CSRF (o CSRF tem testes próprios)."""
    return app.test_client()


@pytest.fixture
def client_producao(sandbox_de_caminhos):
    """
    Cliente que devolve **500** em vez de propagar a exceção.

    Com `TESTING=True` o Flask re-levanta a exceção, o que é ótimo para depurar
    mas impede afirmar *"nenhuma entrada derruba a rota"* — o teste morre com o
    traceback em vez de medir o status. Este cliente reproduz o comportamento do
    servidor real: erro vira resposta 500.
    """
    from app.web.app import create_app

    aplicacao = create_app()
    aplicacao.config["TESTING"] = True
    aplicacao.config["PROPAGATE_EXCEPTIONS"] = False
    aplicacao.config["WTF_CSRF_ENABLED"] = False
    return aplicacao.test_client()


@pytest.fixture
def client_csrf(sandbox_de_caminhos):
    """
    Cliente com CSRF **ligado**, para os testes que provam a proteção.

    Separado do `client` porque a maioria dos testes exercita regra de negócio e
    não deve carregar o ritual de token; mas desligar CSRF em toda a suíte
    deixaria a proteção sem nenhuma cobertura.
    """
    from app.web.app import create_app

    aplicacao = create_app()
    aplicacao.config["TESTING"] = True
    aplicacao.config["WTF_CSRF_ENABLED"] = True
    return aplicacao.test_client()


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures de dados
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def projeto_vulneravel(tmp_path):
    """
    Projeto de amostra com uma vulnerabilidade de cada categoria conhecida.

    Serve de **controle positivo** do motor de scan: se o scan não achar nada
    aqui, o instrumento está cego e qualquer zero que ele produza noutro teste
    não vale como prova.
    """
    projeto = tmp_path / "projeto_vulneravel"
    projeto.mkdir()

    arquivos = {
        "database_service.py":
            'def get_user(uid):\n'
            '    query = f"SELECT * FROM users WHERE id = \'{uid}\'"\n'
            '    return db.execute(query)\n',
        "utils_sistema.py":
            'import os, subprocess\n'
            'def executar(cmd):\n'
            '    os.system(cmd)\n'
            '    subprocess.run(cmd, shell=True)\n',
        "config_env.py":
            'API_KEY = "sk_test_" + "CHAVE_DE_TESTE_FICTICIA"\n'
            'DB_PASSWORD = "super_secret_password_123"\n',
        "frontend.js":
            'function render(n) {\n'
            '    document.getElementById("x").innerHTML = "<h1>" + n + "</h1>";\n'
            '}\n',
        "file_manager.py":
            'def ler(request):\n'
            '    with open(request.args["file"], "r") as f:\n'
            '        return f.read()\n',
        "cache_service.py":
            'import pickle\n'
            'def load(d):\n'
            '    return pickle.loads(d)\n',
        "network_client.py":
            'import requests\n'
            'def fetch(url):\n'
            '    return requests.get(url)\n',
        "auth.py":
            'import jwt\n'
            'def decode(t):\n'
            '    return jwt.decode(t, options={"verify_signature": False})\n',
    }
    for nome, conteudo in arquivos.items():
        (projeto / nome).write_text(conteudo, encoding="utf-8")

    return projeto


@pytest.fixture
def projeto_limpo(tmp_path):
    """Projeto sem nenhum arquivo analisável — controle negativo do motor."""
    projeto = tmp_path / "projeto_limpo"
    projeto.mkdir()
    (projeto / "leia-me.txt").write_text("sem codigo", encoding="utf-8")
    return projeto


@pytest.fixture
def relatorio_valido(sandbox_de_caminhos):
    """Grava um relatório JSON íntegro no sandbox e devolve (nome, caminho)."""
    import json

    pasta = sandbox_de_caminhos / "logs" / "generic" / "reports"
    caminho = pasta / "report_20260101_000000.json"
    caminho.write_text(
        json.dumps(
            {
                "projeto": "amostra",
                "data_scan": "01/01/2026 | 00:00:00",
                "total_arquivos": 1,
                "total_vulnerabilidades": 1,
                "vulnerabilidades": [
                    {
                        "arquivo": "a.py",
                        "linha": 1,
                        "tipo": "Credenciais Hardcoded",
                        "severidade": "CRÍTICO",
                        "trecho": 'senha = "x"',
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return caminho.name, caminho


# ─────────────────────────────────────────────────────────────────────────────
# Utilidades compartilhadas
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def payloads_traversal():
    """
    Vetores de path traversal usados pelos testes de segurança.

    Lista única para que um vetor novo entre em um lugar só e passe a valer em
    todas as rotas que resolvem caminho a partir de entrada do usuário.
    """
    return [
        "../../../../../../etc/passwd",
        r"..\..\..\..\..\..\Windows\win.ini",
        "....//....//....//etc/passwd",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "..%252f..%252f..%252fetc%252fpasswd",
        "/etc/passwd",
        r"C:\Windows\win.ini",
        "\\\\servidor\\compartilhamento\\arquivo",
        "....\\....\\....\\Windows\\win.ini",
        "..;/..;/..;/etc/passwd",
    ]
