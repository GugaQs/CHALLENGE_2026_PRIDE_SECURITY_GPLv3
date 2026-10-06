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

"""Servicos web para scan de projeto — delega para app.ui.scan_projeto."""

import datetime
import json
import os
import subprocess
import threading
import unicodedata

from app.ui.scan_projeto.executar_scan import rodar_engine_scan
from app.ui.scan_projeto.listar_falhas import obter_diretorio_logs
from app.web.services.job_progresso import (
    atualizar_job,
    criar_job,
    iniciar_thread,
    obter_job,
)


def obter_raiz_projeto():
    """Retorna caminho absoluto da raiz flask-python."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def obter_diretorio_logs_sistema():
    """Retorna diretorio logs/ na raiz do projeto."""
    return os.path.join(obter_raiz_projeto(), "logs")


def obter_diretorio_logs_scan():
    """Retorna pasta de relatorios JSON do scan classico."""
    return obter_diretorio_logs()


def executar_scan(caminho_alvo):
    """Executa scan validando caminho informado."""
    caminho_alvo = (caminho_alvo or "").strip()
    if not caminho_alvo:
        return False, "Informe o caminho do projeto.", None
    if not os.path.isdir(caminho_alvo):
        return False, "Caminho invalido ou inexistente.", None

    caminho_log = rodar_engine_scan(caminho_alvo)
    if not caminho_log or not os.path.exists(caminho_log):
        return False, "Scan concluido sem gerar log compativel.", None

    return True, "Scan executado com sucesso.", os.path.basename(caminho_log)


def iniciar_scan_assincrono(caminho_alvo):
    """Inicia scan em thread e retorna job_id."""
    caminho_alvo = (caminho_alvo or "").strip()
    if not caminho_alvo:
        return False, "Informe o caminho do projeto.", None
    if not os.path.isdir(caminho_alvo):
        return False, "Caminho invalido ou inexistente.", None

    job_id = criar_job("Iniciando scan de projeto...")
    iniciar_thread(job_id, lambda jid: _executar_scan_background(jid, caminho_alvo))
    return True, "Scan iniciado.", job_id


def _executar_scan_background(job_id, caminho_alvo):
    """Worker do scan assincrono."""

    def atualizar(payload):
        atualizar_job(job_id, payload)

    try:
        caminho_log = rodar_engine_scan(
            caminho_alvo,
            progress_callback=atualizar,
            silent=True,
        )
        if caminho_log and os.path.exists(caminho_log):
            nome = os.path.basename(caminho_log)
            atualizar_job(
                job_id,
                {
                    "status": "concluido",
                    "mensagem": "Scan concluido com sucesso.",
                    "percentual": 100,
                    "nome_log": nome,
                    "redirect_url": f"/scan/logs/{nome}",
                },
            )
        else:
            atualizar_job(
                job_id,
                {
                    "status": "erro",
                    "mensagem": "Scan finalizado sem gerar log compativel.",
                },
            )
    except Exception as erro:
        atualizar_job(
            job_id,
            {"status": "erro", "mensagem": f"Falha no scan: {erro}"},
        )


def obter_status_scan(job_id):
    """Consulta status do job de scan."""
    return obter_job(job_id)


def listar_logs():
    """Lista relatorios JSON de scan generico."""
    pasta_logs = obter_diretorio_logs()
    if not os.path.exists(pasta_logs):
        return []

    arquivos = [f for f in os.listdir(pasta_logs) if f.endswith(".json")]
    arquivos.sort(reverse=True)
    relatorios = []

    for nome_arquivo in arquivos:
        caminho = os.path.join(pasta_logs, nome_arquivo)
        item = _montar_resumo_relatorio(nome_arquivo, caminho)
        relatorios.append(item)

    return relatorios


def _montar_resumo_relatorio(nome_arquivo, caminho):
    """Monta metadados de um relatorio para tabela web."""
    item = {
        "nome_arquivo": nome_arquivo,
        "projeto": "Desconhecido",
        "timestamp": "-",
        "total_arquivos": 0,
        "total_falhas": 0,
        "critico": 0,
        "alto": 0,
        "medio": 0,
        "baixo": 0,
        "filtrado": nome_arquivo.startswith("report_filtrado_"),
        "tamanho_kb": int(os.path.getsize(caminho) / 1024) if os.path.exists(caminho) else 0,
    }
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        falhas = dados.get("vulnerabilidades", [])
        item["projeto"] = dados.get("projeto", "Desconhecido")
        item["timestamp"] = dados.get("timestamp_utc_global", dados.get("timestamp", "-"))
        item["total_arquivos"] = dados.get("total_arquivos_analisados", 0)
        item["total_falhas"] = len(falhas)
        for falha in falhas:
            sev_raw = unicodedata.normalize("NFD", str(falha.get("severidade", "")))
            sev = sev_raw.encode("ascii", "ignore").decode("ascii").upper()
            if "CRIT" in sev:
                item["critico"] += 1
            elif "ALTO" in sev or "ALTA" in sev:
                item["alto"] += 1
            elif "MED" in sev:
                item["medio"] += 1
            else:
                item["baixo"] += 1
        item["score_risco"] = calcular_score_risco(
            item["critico"], item["alto"], item["medio"], item["baixo"]
        )
        item["nivel_risco"] = _nivel_score_risco(item["score_risco"])
    except (OSError, json.JSONDecodeError):
        pass
    return item


def listar_logs_sistema():
    """Lista artefatos em logs/ (raiz, amd, nvidia, generic)."""
    pasta_raiz = obter_diretorio_logs_sistema()
    if not os.path.exists(pasta_raiz):
        return []

    logs = []
    extensoes = (".log", ".json", ".md", ".txt")
    for raiz, _, arquivos in os.walk(pasta_raiz):
        for nome_arquivo in arquivos:
            if not nome_arquivo.lower().endswith(extensoes):
                continue
            caminho = os.path.join(raiz, nome_arquivo)
            if not os.path.isfile(caminho):
                continue
            tamanho_bytes = os.path.getsize(caminho)
            if tamanho_bytes == 0:
                continue
            modificado_ts = os.path.getmtime(caminho)
            caminho_relativo = os.path.relpath(caminho, pasta_raiz).replace("\\", "/")
            origem = caminho_relativo.split("/")[0] if "/" in caminho_relativo else "raiz"
            logs.append(
                {
                    "nome_arquivo": f"sistema/{caminho_relativo}",
                    "nome_exibicao": caminho_relativo,
                    "origem": origem,
                    "tamanho_kb": int(tamanho_bytes / 1024),
                    "tamanho_legivel": _formatar_tamanho(tamanho_bytes),
                    "modificado_em": str(datetime.datetime.fromtimestamp(modificado_ts))[:19],
                    "modificado_ts": modificado_ts,
                }
            )

    logs.sort(key=lambda item: item["modificado_ts"], reverse=True)
    return logs


def ler_log_sistema(nome_arquivo, limite=400):
    """Le arquivo de log com limite de linhas."""
    nome_relativo = (nome_arquivo or "").replace("\\", "/").strip("/")
    if "/" not in nome_relativo:
        return None

    fonte, nome_interno = nome_relativo.split("/", 1)
    fontes = {
        "sistema": obter_diretorio_logs_sistema(),
        "scan": obter_diretorio_logs_scan(),
    }
    pasta = fontes.get(fonte)
    if not pasta:
        return None

    caminho = os.path.abspath(os.path.join(pasta, nome_interno))
    if os.path.commonpath([pasta, caminho]) != pasta:
        return None
    if not os.path.isfile(caminho):
        return None

    try:
        with open(caminho, "r", encoding="utf-8", errors="ignore") as arquivo:
            linhas = arquivo.readlines()
        if len(linhas) > limite:
            linhas = linhas[-limite:]
        return "".join(linhas)
    except OSError:
        return None


def calcular_score_risco(critico, alto, medio, baixo):
    """Score 0-100: 0-20 baixo, 21-50 medio, 51-80 alto, 81-100 critico."""
    score = (
        min(critico * 22, 80)
        + min(alto * 8, 25)
        + min(medio * 2, 8)
        + min(int(baixo * 0.5), 3)
    )
    return min(int(score), 100)


def _nivel_score_risco(score):
    """Nivel textual do score de risco."""
    if score <= 20:
        return "BAIXO"
    if score <= 50:
        return "MEDIO"
    if score <= 80:
        return "ALTO"
    return "CRITICO"


def _formatar_tamanho(tamanho_bytes):
    """Formata tamanho legivel."""
    if tamanho_bytes < 1024:
        return f"{tamanho_bytes} B"
    return f"{round(tamanho_bytes / 1024, 1)} KB"


def limpar_logs():
    """Remove JSONs de relatorio de scan."""
    pasta_logs = obter_diretorio_logs()
    if not os.path.exists(pasta_logs):
        return True, "Nenhum log para limpar."

    removidos = 0
    try:
        for nome_arquivo in os.listdir(pasta_logs):
            if not nome_arquivo.endswith(".json"):
                continue
            caminho = os.path.join(pasta_logs, nome_arquivo)
            if os.path.isfile(caminho):
                os.remove(caminho)
                removidos += 1
    except OSError as erro:
        return False, f"Falha ao limpar logs: {erro}"

    return True, f"{removidos} relatorio(s) removido(s)."


def obter_log(nome_arquivo):
    """Carrega relatorio JSON pelo nome."""
    nome_limpo = os.path.basename(nome_arquivo or "")
    if not nome_limpo.endswith(".json"):
        return None

    caminho = os.path.join(obter_diretorio_logs(), nome_limpo)
    if not os.path.exists(caminho):
        return None

    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def obter_caminho_log(nome_arquivo):
    """Retorna caminho absoluto do relatorio."""
    nome_limpo = os.path.basename(nome_arquivo or "")
    return os.path.join(obter_diretorio_logs(), nome_limpo)


def abrir_arquivo_por_falha(nome_arquivo, falha_id):
    """Abre no SO o arquivo vinculado a falha."""
    dados = obter_log(nome_arquivo)
    if not dados:
        return False, "Relatorio nao encontrado."

    falhas = dados.get("vulnerabilidades", [])
    alvo = None
    for falha in falhas:
        indice = falha.get("indice", falha.get("id"))
        if str(indice) == str(falha_id):
            alvo = falha
            break

    if not alvo:
        return False, "Falha/ID nao localizado nesse relatorio."

    caminho_arquivo = alvo.get("caminho_completo", alvo.get("caminho"))
    if not caminho_arquivo or not os.path.exists(caminho_arquivo):
        return False, "Arquivo vinculado a falha nao existe no disco."

    try:
        if os.name == "nt":
            os.startfile(caminho_arquivo)
        else:
            subprocess.run(["xdg-open", caminho_arquivo], check=False)
    except OSError as erro:
        return False, f"Nao foi possivel abrir o arquivo: {erro}"

    return True, f"Arquivo aberto: {os.path.basename(caminho_arquivo)}"


# Tempo máximo que o seletor fica aberto. Precisa acompanhar o AbortController
# de `app.js` (`.btn-buscar-pasta`), que deve ser um pouco MAIOR que este valor:
# quem desiste primeiro tem de ser o servidor, para que o processo do diálogo
# seja efetivamente morto em vez de ficar órfão na máquina do usuário.
SEGUNDOS_LIMITE_SELETOR = 120

# Exclusão mútua do seletor de pasta (INV-SELETOR-001).
#
# O servidor Flask roda com `threaded=True` (padrão de `app.run`), então cada
# clique cai numa thread própria. Sem esta trava, cada clique abre MAIS um
# diálogo modal e prende MAIS uma thread — foi exatamente assim que a ferramenta
# passou a "travar o PC": o diálogo abria atrás do navegador, o usuário não via
# nada, clicava de novo, e as janelas modais invisíveis iam se empilhando.
_TRAVA_SELETOR_PASTA = threading.Lock()

# Sentinelas trocadas com o script PowerShell. Existem para distinguir
# "o usuário cancelou" de "o mecanismo falhou" — sem essa distinção, cancelar
# disparava o caminho de contingência e abria uma SEGUNDA janela.
_MARCA_SELECIONADO = "ASPM_PASTA_SELECIONADA:"
_MARCA_CANCELADO = "ASPM_PASTA_CANCELADA"


def selecionar_pasta_sistema():
    """
    Abre o seletor nativo de pasta e devolve o caminho escolhido.

    PROPÓSITO DE NEGÓCIO
    --------------------
    O operador precisa apontar a pasta do projeto a ser escaneada sem digitar o
    caminho à mão. A aplicação roda local, então o diálogo é o do próprio
    sistema operacional da pessoa.

    INVARIANTES DO DOMÍNIO
    ----------------------
    - **INV-SELETOR-001 · Um diálogo por vez.** Enquanto houver um seletor
      aberto, um novo pedido é recusado de imediato, sem abrir outra janela.
      Sem isto, cliques repetidos empilham janelas modais e threads bloqueadas.
    - **INV-SELETOR-002 · A janela aparece na frente.** O diálogo é aberto com
      uma janela dona `TopMost`, para não nascer atrás do navegador — que é a
      causa de o usuário clicar várias vezes achando que não funcionou.
    - **INV-SELETOR-003 · Cancelar é cancelar.** Cancelamento nunca dispara
      caminho de contingência nem abre uma segunda janela.
    - **INV-SELETOR-004 · Nenhuma janela Tk fora da thread principal.** O
      `tkinter` só é usado quando esta função roda na thread principal (uso via
      CLI). Numa requisição web, ele nunca é acionado.

    Returns:
        tuple[bool, str, str | None]: `(ok, mensagem, caminho)`. Em recusa ou
        cancelamento, `caminho` é `None` e a mensagem explica o motivo.

    COMPORTAMENTO EM CASO DE FALHA
    ------------------------------
    - Já há um seletor aberto: devolve `(False, mensagem, None)` de imediato,
      sem bloquear a thread e sem abrir nada.
    - Usuário cancela: `(False, "Selecao cancelada...", None)` — sem contingência.
    - Tempo esgotado: a árvore de processos do diálogo é **morta**, para não
      deixar janela órfã na máquina, e devolve `(False, mensagem, None)`.
    - Mecanismo indisponível (PowerShell ausente, sem sessão gráfica): devolve
      `(False, mensagem, None)` orientando a digitar o caminho à mão.
    """
    # INV-SELETOR-001 — `blocking=False`: recusa na hora em vez de enfileirar.
    # Enfileirar seria pior que o defeito original, porque a thread ficaria
    # presa esperando o usuário fechar a janela anterior.
    if not _TRAVA_SELETOR_PASTA.acquire(blocking=False):
        return (
            False,
            "Ja existe um seletor de pasta aberto. Conclua ou cancele aquela "
            "janela antes de abrir outra.",
            None,
        )
    try:
        return _abrir_seletor_de_pasta()
    finally:
        _TRAVA_SELETOR_PASTA.release()


def _abrir_seletor_de_pasta():
    """
    Escolhe o mecanismo de diálogo e traduz o resultado.

    Chamada apenas por `selecionar_pasta_sistema`, que já detém a trava.
    """
    if os.name == "nt":
        estado, caminho = _selecionar_pasta_windows_powershell()
        if estado == "ok":
            return True, "Pasta selecionada com sucesso.", caminho
        if estado == "cancelado":
            # INV-SELETOR-003: cancelar NÃO cai em contingência.
            return False, "Selecao cancelada pelo usuario.", None
        if estado == "tempo_esgotado":
            return (
                False,
                f"O seletor ficou aberto por mais de {SEGUNDOS_LIMITE_SELETOR}s "
                "e foi fechado. Tente de novo ou digite o caminho no campo.",
                None,
            )
        # estado == "falhou": o mecanismo nativo não existe nesta máquina.

    # INV-SELETOR-004: Tk só na thread principal. Numa requisição web esta
    # condição é sempre falsa, porque `app.run` serve com `threaded=True`.
    if threading.current_thread() is not threading.main_thread():
        return (
            False,
            "Nao foi possivel abrir o seletor nativo nesta maquina. "
            "Digite o caminho da pasta no campo ao lado.",
            None,
        )

    try:
        import tkinter as tk
        from tkinter import filedialog

        raiz = tk.Tk()
        raiz.withdraw()
        # `-topmost` e `focus_force()` foram REMOVIDOS de propósito: uma janela
        # sempre-no-topo que rouba o foco deixa o desktop inutilizável se o
        # diálogo travar. `lift()` sozinho traz para frente sem sequestrar.
        raiz.lift()
        try:
            caminho = filedialog.askdirectory(
                parent=raiz,
                title="Selecione a pasta do projeto para scan",
            )
        finally:
            raiz.destroy()
    except Exception:
        return (
            False,
            "Nao foi possivel abrir o seletor de pasta. "
            "Digite o caminho no campo ao lado.",
            None,
        )

    if not caminho:
        return False, "Selecao cancelada pelo usuario.", None
    return True, "Pasta selecionada com sucesso.", caminho


def _selecionar_pasta_windows_powershell():
    """
    Abre o `FolderBrowserDialog` do Windows num processo PowerShell STA.

    INVARIANTES DO DOMÍNIO
    ----------------------
    - A janela é criada com uma **dona `TopMost`** (INV-SELETOR-002). Sem dono,
      `ShowDialog()` não garante primeiro plano e o diálogo não recebe botão na
      barra de tarefas: ele some atrás do navegador e fica inalcançável.
    - A saída é uma **sentinela**, não o caminho cru, para que cancelamento seja
      distinguível de falha (INV-SELETOR-003). Antes, os dois produziam saída
      vazia e eram tratados igual.

    Returns:
        tuple[str, str | None]: estado em
        `{"ok", "cancelado", "tempo_esgotado", "falhou"}` e o caminho quando `ok`.
    """
    if os.name != "nt":
        return "falhou", None

    # `FolderBrowserDialog` exige apartamento STA — daí o `-Sta`.
    comando = (
        "$ErrorActionPreference = 'Stop'; "
        "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
        "Add-Type -AssemblyName System.Windows.Forms; "
        # Janela dona minúscula e TopMost: é ela que puxa o diálogo para frente.
        "$dono = New-Object System.Windows.Forms.Form; "
        "$dono.TopMost = $true; "
        "$dono.ShowInTaskbar = $false; "
        "$dono.FormBorderStyle = 'None'; "
        "$dono.Opacity = 0; "
        "$dono.Width = 1; $dono.Height = 1; "
        "$dono.StartPosition = 'CenterScreen'; "
        "$dono.Show(); $dono.Activate(); $dono.BringToFront(); "
        "$dialogo = New-Object System.Windows.Forms.FolderBrowserDialog; "
        "$dialogo.Description = 'Selecione a pasta do projeto para scan'; "
        "$dialogo.ShowNewFolderButton = $true; "
        "$resultado = $dialogo.ShowDialog($dono); "
        "$dono.Close(); $dono.Dispose(); "
        "if ($resultado -eq [System.Windows.Forms.DialogResult]::OK) "
        f"{{ Write-Output ('{_MARCA_SELECIONADO}' + $dialogo.SelectedPath) }} "
        f"else {{ Write-Output '{_MARCA_CANCELADO}' }}"
    )

    estado, saida = _executar_comando_powershell(comando)
    if estado != "ok":
        return estado, None

    if saida.startswith(_MARCA_SELECIONADO):
        caminho = saida[len(_MARCA_SELECIONADO):].strip()
        return ("ok", caminho) if caminho else ("cancelado", None)
    if _MARCA_CANCELADO in saida:
        return "cancelado", None
    return "falhou", None


def _executar_comando_powershell(comando):
    """
    Executa um comando PowerShell STA e devolve `(estado, stdout)`.

    INVARIANTES DO DOMÍNIO
    ----------------------
    - **No tempo esgotado, a ÁRVORE de processos é morta.** `subprocess.run`
      com `timeout` mata apenas o filho direto; o `FolderBrowserDialog` pode
      sobreviver como janela órfã na tela do usuário, sem dono e sem como
      fechar. Por isso aqui usa-se `Popen` e, no estouro, `taskkill /T /F`.
    - O console do PowerShell não pisca na tela (`CREATE_NO_WINDOW`); a janela
      do diálogo continua aparecendo normalmente, porque é criada pelo .NET.

    Returns:
        tuple[str, str]: estado em
        `{"ok", "tempo_esgotado", "falhou"}` e a saída padrão (vazia se não `ok`).
    """
    argumentos = ["powershell", "-Sta", "-NoProfile", "-NonInteractive",
                  "-Command", comando]
    sem_janela = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    try:
        processo = subprocess.Popen(
            argumentos,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore",
            creationflags=sem_janela,
        )
    except OSError:
        # PowerShell ausente ou sem permissão de execução.
        return "falhou", ""

    try:
        saida, _erro = processo.communicate(timeout=SEGUNDOS_LIMITE_SELETOR)
    except subprocess.TimeoutExpired:
        _matar_arvore_de_processos(processo)
        return "tempo_esgotado", ""

    if processo.returncode != 0:
        return "falhou", ""
    return "ok", (saida or "").strip()


def _matar_arvore_de_processos(processo):
    """
    Encerra o processo e todos os seus filhos.

    Necessário porque matar só o `powershell.exe` pode deixar a janela do
    diálogo aberta e órfã na tela de quem está usando a aplicação — o usuário
    ficaria com uma janela modal que não fecha e não pertence a nada.

    Falha silenciosamente de propósito: se o processo já morreu, ou se o
    `taskkill` não existe, não há o que reportar e nada a corrigir.
    """
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(processo.pid)],
                capture_output=True,
                check=False,
                timeout=15,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except (OSError, subprocess.TimeoutExpired):
            pass

    try:
        processo.kill()
    except OSError:
        pass
    try:
        processo.communicate(timeout=10)
    except (subprocess.TimeoutExpired, ValueError, OSError):
        pass
