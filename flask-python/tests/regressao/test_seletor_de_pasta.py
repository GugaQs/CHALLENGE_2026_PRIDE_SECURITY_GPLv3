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
Seletor de pasta — guarda contra a regressão que travava a máquina do usuário.

PROPÓSITO DE NEGÓCIO
--------------------
O botão "buscar pasta" abre o diálogo nativo do sistema para o operador apontar
o projeto a escanear. Ele passou a **travar a interface e, às vezes, o desktop
inteiro**. O mecanismo, medido:

1. `ShowDialog()` era chamado **sem janela dona e sem TopMost**. O Windows não
   garante primeiro plano nesse caso, e o diálogo nasce **sem botão na barra de
   tarefas** — ele abria atrás do navegador, invisível e inalcançável.
2. Como nada aparecia, o operador clicava de novo. **Não havia trava**: cada
   clique subia outro PowerShell, outro diálogo modal invisível e prendia outra
   thread do Flask por até 60 s (`app.run` serve com `threaded=True`).
3. Cancelar o diálogo do PowerShell produzia saída vazia, indistinguível de
   falha — e caía no caminho de contingência, que abria uma **segunda** janela,
   essa em `tkinter` com `-topmost` e `focus_force()`. Uma janela sempre-no-topo
   que sequestra o foco deixa o desktop sem resposta.

INVARIANTES PROTEGIDAS AQUI
---------------------------
- **INV-SELETOR-001** · Um diálogo por vez; o segundo pedido é recusado na hora.
- **INV-SELETOR-002** · O diálogo nasce com janela dona `TopMost`.
- **INV-SELETOR-003** · Cancelar não dispara contingência.
- **INV-SELETOR-004** · Nenhuma janela Tk fora da thread principal.
- **INV-SELETOR-005** · No tempo esgotado, a árvore de processos é morta.
- **INV-SELETOR-006** · O navegador desiste DEPOIS do servidor.

COMPORTAMENTO EM CASO DE FALHA
------------------------------
Falha aqui significa que a ferramenta voltou a poder empilhar janelas modais
invisíveis na máquina de quem usa. Tratar como bloqueio.

NOTA DE MÉTODO
--------------
Nenhum teste deste arquivo abre um diálogo de verdade — abrir seria reproduzir o
próprio defeito na máquina de quem roda a suíte. O processo do PowerShell é
substituído por `monkeypatch`, e o que se afirma é o **contrato** entre as
camadas.
"""

from __future__ import annotations

import os
import re
import threading
import time

import pytest

from tests.conftest import RAIZ_MODULO

pytestmark = [pytest.mark.regressao, pytest.mark.robustez]


APP_JS = os.path.join(RAIZ_MODULO, "app", "web", "static", "js", "app.js")


@pytest.fixture(autouse=True)
def proibir_janela_de_verdade(monkeypatch):
    """
    Impede que QUALQUER teste deste arquivo abra um diálogo real.

    Não é zelo excessivo: durante a calibração destas guardas, ao reintroduzir o
    defeito de propósito, um teste caiu no caminho de contingência e **abriu um
    diálogo `tkinter` de verdade**, pendurando o pytest por 300 s à espera de
    alguém clicar. Uma suíte que pode abrir janela modal na máquina de quem a
    roda reproduz o próprio defeito que existe para prevenir.

    `tkinter` passa a levantar `ImportError` — que é o mesmo que aconteceria
    numa máquina sem suporte gráfico, então o código sob teste segue um caminho
    que ele já sabe tratar.
    """
    import builtins

    importacao_real = builtins.__import__

    def sem_tkinter(nome, *args, **kwargs):
        if nome == "tkinter" or nome.startswith("tkinter."):
            raise ImportError(
                "tkinter bloqueado pela suite: nenhum teste pode abrir janela"
            )
        return importacao_real(nome, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", sem_tkinter)


@pytest.fixture
def servico():
    """Módulo sob teste, com a trava garantidamente livre."""
    from app.web.services import scan_service

    if scan_service._TRAVA_SELETOR_PASTA.locked():  # pragma: no cover
        scan_service._TRAVA_SELETOR_PASTA.release()
    return scan_service


# ── INV-SELETOR-001 · Um diálogo por vez ─────────────────────────────────────

def test_segundo_pedido_e_recusado_na_hora_sem_abrir_outra_janela(servico):
    """
    Com um seletor aberto, o próximo clique recebe recusa imediata.

    Este é o conserto central: era daqui que vinha o empilhamento de janelas
    modais invisíveis que deixava a máquina sem resposta.
    """
    segurando = threading.Event()
    liberar = threading.Event()

    def ocupar():
        servico._TRAVA_SELETOR_PASTA.acquire()
        segurando.set()
        liberar.wait(20)
        servico._TRAVA_SELETOR_PASTA.release()

    dono = threading.Thread(target=ocupar, daemon=True)
    dono.start()
    assert segurando.wait(5), "a fixture nao conseguiu ocupar a trava"

    try:
        inicio = time.perf_counter()
        ok, mensagem, caminho = servico.selecionar_pasta_sistema()
        decorrido = time.perf_counter() - inicio
    finally:
        liberar.set()
        dono.join(timeout=5)

    assert ok is False
    assert caminho is None
    assert decorrido < 1.0, (
        f"a recusa levou {decorrido:.2f}s — deveria ser imediata. Esperar pela "
        "trava prenderia a thread ate o usuario fechar a janela anterior, que e "
        "pior que o defeito original."
    )
    assert "aberto" in mensagem.lower(), mensagem


def test_a_trava_e_liberada_mesmo_quando_o_seletor_estoura(servico, monkeypatch):
    """
    Exceção no meio do diálogo não pode deixar a trava presa para sempre.

    Sem o `finally`, um erro inesperado tornaria o botão inútil até reiniciar a
    aplicação — e o usuário veria "ja existe um seletor aberto" para sempre.
    """
    def explodir():
        raise RuntimeError("falha simulada no seletor")

    monkeypatch.setattr(servico, "_abrir_seletor_de_pasta", explodir)

    with pytest.raises(RuntimeError):
        servico.selecionar_pasta_sistema()

    assert not servico._TRAVA_SELETOR_PASTA.locked(), (
        "a trava ficou presa apos a excecao — o botao nunca mais funcionaria"
    )


def test_trava_livre_permite_o_fluxo_normal(servico, monkeypatch):
    """
    Controle positivo: sem concorrência, o seletor funciona.

    Sem este caso, os testes de recusa acima passariam mesmo com a função
    quebrada e sempre devolvendo `False`.
    """
    monkeypatch.setattr(
        servico,
        "_selecionar_pasta_windows_powershell",
        lambda: ("ok", r"C:\Projetos\Exemplo"),
    )
    monkeypatch.setattr(os, "name", "nt")

    ok, _mensagem, caminho = servico.selecionar_pasta_sistema()

    assert ok is True
    assert caminho == r"C:\Projetos\Exemplo"
    assert not servico._TRAVA_SELETOR_PASTA.locked()


# ── INV-SELETOR-003 · Cancelar é cancelar ────────────────────────────────────

def test_cancelar_nao_abre_uma_segunda_janela(servico, monkeypatch):
    """
    Cancelamento devolve recusa e **não** cai no caminho de contingência.

    Antes, cancelar produzia saída vazia — indistinguível de falha — e o código
    seguia para o `tkinter`, abrindo uma segunda janela por cima. O operador
    cancelava e via outra janela aparecer.
    """
    monkeypatch.setattr(os, "name", "nt")
    monkeypatch.setattr(
        servico, "_selecionar_pasta_windows_powershell", lambda: ("cancelado", None)
    )

    contingencia = {"acionada": False}

    import builtins

    importacao_real = builtins.__import__

    def espiao(nome, *args, **kwargs):
        if nome == "tkinter" or nome.startswith("tkinter."):
            contingencia["acionada"] = True
            raise AssertionError(
                "o caminho de contingencia (tkinter) foi acionado apos um "
                "CANCELAMENTO — era exatamente a segunda janela do defeito"
            )
        return importacao_real(nome, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", espiao)

    ok, mensagem, caminho = servico.selecionar_pasta_sistema()

    assert contingencia["acionada"] is False
    assert ok is False
    assert caminho is None
    assert "cancel" in mensagem.lower(), mensagem


def test_falha_do_mecanismo_e_distinguivel_de_cancelamento(servico, monkeypatch):
    """
    Mecanismo indisponível produz mensagem diferente de cancelamento.

    Confundir os dois foi a raiz da segunda janela: os dois casos precisam de
    respostas diferentes porque exigem ações diferentes do operador.
    """
    monkeypatch.setattr(os, "name", "nt")

    monkeypatch.setattr(
        servico, "_selecionar_pasta_windows_powershell", lambda: ("cancelado", None)
    )
    _ok1, msg_cancelado, _c1 = servico.selecionar_pasta_sistema()

    monkeypatch.setattr(
        servico, "_selecionar_pasta_windows_powershell", lambda: ("tempo_esgotado", None)
    )
    _ok2, msg_tempo, _c2 = servico.selecionar_pasta_sistema()

    assert msg_cancelado != msg_tempo, (
        "cancelamento e tempo esgotado devolvem a MESMA mensagem; o operador "
        "nao consegue saber se a janela dele foi fechada por ele ou pelo sistema"
    )
    assert "cancel" in msg_cancelado.lower()
    assert str(servico.SEGUNDOS_LIMITE_SELETOR) in msg_tempo


# ── INV-SELETOR-004 · Nada de Tk fora da thread principal ────────────────────

def test_tkinter_nunca_e_usado_a_partir_de_uma_thread_worker(servico, monkeypatch):
    """
    Numa requisição web, a contingência `tkinter` não pode ser acionada.

    `app.run` serve com `threaded=True`, então toda rota roda em thread worker.
    Uma janela Tk criada ali, com `-topmost` e `focus_force()`, sequestra o foco
    do desktop — é a metade "trava o PC" do defeito.
    """
    monkeypatch.setattr(os, "name", "posix")  # força o caminho de contingência

    resultado = {}

    def na_worker():
        import builtins

        importacao_real = builtins.__import__

        def espiao(nome, *args, **kwargs):
            if nome == "tkinter" or nome.startswith("tkinter."):
                resultado["tkinter"] = True
                raise AssertionError("tkinter acionado a partir de thread worker")
            return importacao_real(nome, *args, **kwargs)

        builtins.__import__ = espiao
        try:
            resultado["retorno"] = servico.selecionar_pasta_sistema()
        finally:
            builtins.__import__ = importacao_real

    thread = threading.Thread(target=na_worker, name="WorkerFlaskSimulada")
    thread.start()
    thread.join(timeout=15)

    assert not thread.is_alive(), "a chamada pendurou na thread worker"
    assert resultado.get("tkinter") is not True, (
        "tkinter foi importado a partir de uma thread worker"
    )
    ok, _mensagem, caminho = resultado["retorno"]
    assert ok is False and caminho is None


def test_codigo_nao_usa_mais_topmost_nem_focus_force():
    """
    `-topmost` + `focus_force()` sumiram do seletor.

    Uma janela sempre-no-topo que rouba o foco, se travar, deixa o desktop sem
    resposta: o usuário não consegue clicar em mais nada. Guarda textual porque
    o dano só aparece com janela real, que a suíte não pode abrir.
    """
    caminho = os.path.join(
        RAIZ_MODULO, "app", "web", "services", "scan_service.py"
    )
    with open(caminho, encoding="utf-8") as fh:
        fonte = fh.read()

    # Ignora comentários: o histórico do defeito está documentado no código.
    codigo = "\n".join(
        linha for linha in fonte.splitlines()
        if not linha.strip().startswith("#")
    )

    assert "focus_force" not in codigo, "focus_force() voltou ao seletor"
    assert "-topmost" not in codigo, "-topmost voltou ao seletor"


# ── INV-SELETOR-002 · A janela aparece na frente ─────────────────────────────

def test_dialogo_e_aberto_com_janela_dona_topmost(servico, monkeypatch):
    """
    O comando PowerShell cria uma dona `TopMost` e passa como owner.

    Sem dono, `ShowDialog()` não garante primeiro plano e o diálogo não recebe
    botão na barra de tarefas — ele abre atrás do navegador e some.
    """
    monkeypatch.setattr(os, "name", "nt")
    capturado = {}

    def espiao(comando):
        capturado["comando"] = comando
        return "ok", servico._MARCA_CANCELADO

    monkeypatch.setattr(servico, "_executar_comando_powershell", espiao)
    servico._selecionar_pasta_windows_powershell()

    comando = capturado["comando"]
    assert "New-Object System.Windows.Forms.Form" in comando, "sem janela dona"
    assert "$dono.TopMost = $true" in comando, "a dona nao e TopMost"
    assert "ShowDialog($dono)" in comando, (
        "ShowDialog foi chamado SEM o owner — o dialogo volta a abrir atras "
        "do navegador"
    )
    assert "$dono.Close()" in comando, "a janela dona nao e fechada"


def test_saida_do_powershell_e_traduzida_pelos_tres_estados(servico, monkeypatch):
    """A sentinela cobre selecionado, cancelado e saída inesperada."""
    monkeypatch.setattr(os, "name", "nt")

    casos = [
        (f"{servico._MARCA_SELECIONADO}C:\\Projetos\\X", ("ok", "C:\\Projetos\\X")),
        (servico._MARCA_CANCELADO, ("cancelado", None)),
        (f"{servico._MARCA_SELECIONADO}   ", ("cancelado", None)),
        ("lixo inesperado na saida", ("falhou", None)),
        ("", ("falhou", None)),
    ]
    for saida, esperado in casos:
        monkeypatch.setattr(
            servico, "_executar_comando_powershell", lambda _c, s=saida: ("ok", s)
        )
        assert servico._selecionar_pasta_windows_powershell() == esperado, (
            f"saida {saida!r} traduzida errado"
        )


# ── INV-SELETOR-005 · Timeout mata a árvore ──────────────────────────────────

@pytest.mark.lento
@pytest.mark.skipif(os.name != "nt", reason="taskkill /T e especifico do Windows")
def test_tempo_esgotado_encerra_o_processo_e_nao_deixa_orfao(servico, monkeypatch):
    """
    Um comando que nunca termina é morto dentro do limite.

    `subprocess.run(timeout=...)` mata só o filho direto; a janela do diálogo
    poderia sobreviver órfã na tela, modal e sem dono — impossível de fechar.
    """
    monkeypatch.setattr(servico, "SEGUNDOS_LIMITE_SELETOR", 3)

    inicio = time.perf_counter()
    estado, saida = servico._executar_comando_powershell("Start-Sleep -Seconds 90")
    decorrido = time.perf_counter() - inicio

    assert estado == "tempo_esgotado", f"estado inesperado: {estado!r}"
    assert saida == ""
    assert decorrido < 30, (
        f"levou {decorrido:.1f}s para desistir de um limite de 3s — o processo "
        "nao esta sendo morto"
    )


def test_powershell_ausente_nao_derruba_a_rota(servico, monkeypatch):
    """Executável inexistente vira recusa educada, não exceção."""
    import subprocess as sp

    def sem_powershell(*_args, **_kwargs):
        raise OSError("powershell nao encontrado")

    monkeypatch.setattr(sp, "Popen", sem_powershell)
    estado, saida = servico._executar_comando_powershell("Write-Output 'x'")

    assert estado == "falhou"
    assert saida == ""


# ── INV-SELETOR-006 · O navegador desiste depois do servidor ─────────────────

def test_limite_do_navegador_e_maior_que_o_do_servidor(servico):
    """
    O `AbortController` do `app.js` precisa ser MAIOR que o limite do servidor.

    Se o navegador desistir primeiro, o botão volta ao normal convidando a
    clicar de novo — enquanto o diálogo continua aberto e órfão na tela. Era
    assim: 65 s no navegador contra 60 s no servidor, sem margem nenhuma.
    """
    with open(APP_JS, encoding="utf-8") as fh:
        js = fh.read()

    achado = re.search(r"LIMITE_SELETOR_MS\s*=\s*(\d+)", js)
    assert achado, "LIMITE_SELETOR_MS nao encontrado em app.js"

    limite_js_s = int(achado.group(1)) / 1000
    limite_servidor_s = servico.SEGUNDOS_LIMITE_SELETOR

    assert limite_js_s > limite_servidor_s, (
        f"navegador desiste em {limite_js_s}s e o servidor em "
        f"{limite_servidor_s}s — o servidor tem de desistir PRIMEIRO para matar "
        "o processo do dialogo"
    )
    assert limite_js_s - limite_servidor_s >= 5, (
        f"margem de apenas {limite_js_s - limite_servidor_s}s entre navegador e "
        "servidor; use ao menos 5s para absorver a latencia da resposta"
    )


def test_rota_de_selecao_devolve_json_com_contrato_estavel(client_producao, monkeypatch):
    """
    A rota responde `{ok, mensagem, caminho}` — o `app.js` lê os três campos.

    Afirma o contrato, não o texto: a mensagem é de tela e muda; as chaves não.
    """
    from app.web.services import scan_service

    monkeypatch.setattr(
        scan_service,
        "selecionar_pasta_sistema",
        lambda: (False, "Selecao cancelada pelo usuario.", None),
    )
    import app.web.routes.scan_routes as rotas

    monkeypatch.setattr(
        rotas, "selecionar_pasta_sistema", scan_service.selecionar_pasta_sistema
    )

    resposta = client_producao.post("/scan/selecionar-pasta")
    corpo = resposta.get_json()

    assert resposta.status_code < 500
    assert set(corpo) >= {"ok", "mensagem", "caminho"}, corpo
    assert corpo["ok"] is False
    assert corpo["caminho"] is None
    assert corpo["mensagem"]
