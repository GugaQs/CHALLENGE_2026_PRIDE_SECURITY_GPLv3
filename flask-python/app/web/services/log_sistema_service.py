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

"""Servicos web de logs — delega para app.ui.log_sistema."""

import os
import re
import subprocess

from app.ui.log_sistema.menu_log_sistema import LOG_ERRO_PADRAO, obter_diretorio_logs


def listar_arquivos_log():
    """Lista arquivos em logs/ (mesma logica do menu CLI)."""
    pasta_base = obter_diretorio_logs()
    if not os.path.isdir(pasta_base):
        return pasta_base, []

    arquivos = []
    for nome in os.listdir(pasta_base):
        caminho = os.path.join(pasta_base, nome)
        if nome.lower().endswith(".log") and os.path.isfile(caminho):
            arquivos.append(
                {
                    "caminho_relativo": nome,
                    "nome": nome,
                    "categoria": "raiz",
                    "tamanho_kb": int(os.path.getsize(caminho) / 1024),
                }
            )

    for sub in ("amd", "nvidia", "generic"):
        for category in ("system", "reports"):
            pasta_sub = os.path.join(pasta_base, sub, category)
            if not os.path.isdir(pasta_sub):
                continue
            for nome in os.listdir(pasta_sub):
                caminho = os.path.join(pasta_sub, nome)
                if not os.path.isfile(caminho):
                    continue
                if not nome.lower().endswith((".log", ".json", ".md", ".txt")):
                    continue
                relativo = os.path.join(sub, category, nome).replace("\\", "/")
                arquivos.append(
                    {
                        "caminho_relativo": relativo,
                        "nome": nome,
                        "categoria": f"{sub}/{category}",
                        "tamanho_kb": int(os.path.getsize(caminho) / 1024),
                    }
                )

    arquivos.sort(key=lambda item: item["caminho_relativo"], reverse=True)
    return pasta_base, arquivos


def _ler_arquivo_com_limite(caminho_absoluto, limite=None):
    """Le arquivo com limite opcional de linhas (ultimas N)."""
    if not os.path.isfile(caminho_absoluto):
        return None

    try:
        with open(caminho_absoluto, "r", encoding="utf-8", errors="replace") as arquivo:
            linhas = arquivo.readlines()
    except OSError:
        return None

    if limite is not None and len(linhas) > limite:
        linhas = linhas[-limite:]
    return "".join(linhas)


def ler_arquivo_log(caminho_relativo, limite=400):
    """Le arquivo dentro de logs/ com limite de linhas."""
    pasta_base = obter_diretorio_logs()
    caminho = os.path.abspath(os.path.join(pasta_base, caminho_relativo or ""))
    if os.path.commonpath([pasta_base, caminho]) != pasta_base:
        return None
    return _ler_arquivo_com_limite(caminho, limite)


def ler_erro_sistema(linhas=80):
    """Ultimas linhas de logs/erro_sistema.log."""
    pasta = obter_diretorio_logs()
    caminho = os.path.join(pasta, LOG_ERRO_PADRAO)
    limite = max(10, min(int(linhas or 80), 500))
    return _ler_arquivo_com_limite(caminho, limite)


def ler_log_amd_sistema(linhas=100):
    """Ultimas linhas do log de sistema AMD."""
    pasta = obter_diretorio_logs()
    caminho = os.path.join(pasta, "amd", "system", "sistema_amd.log")
    limite = max(10, min(int(linhas or 100), 1000))
    return _ler_arquivo_com_limite(caminho, limite)


def ler_log_nvidia_sistema(linhas=100):
    """Ultimas linhas do log de sistema NVIDIA."""
    pasta = obter_diretorio_logs()
    caminho = os.path.join(pasta, "nvidia", "system", "sistema_nvidia.log")
    limite = max(10, min(int(linhas or 100), 1000))
    return _ler_arquivo_com_limite(caminho, limite)


# ── Dicionario de explicacoes didaticas ──────────────────────────────────────
# Cada entrada: (padrao_re, titulo_curto, explicacao, acao_sugerida)
_EXPLICACOES = [
    # ASPM — scan_engine
    (re.compile(r"Iniciando varredura ASPM em (.+) \((\d+) arquivo", re.I),
     "🔍 Scan iniciado",
     "O motor ASPM comecou a varredura de seguranca na pasta indicada. "
     "O numero entre parenteses e a quantidade de arquivos candidatos a analise.",
     "Aguarde a conclusao. Se o numero de arquivos for 0, verifique se o caminho esta correto."),

    (re.compile(r"Relatorio de scan gravado: (.+)", re.I),
     "✅ Relatorio salvo",
     "O resultado do scan foi gravado em disco no formato JSON. "
     "Voce pode abri-lo na aba Relatorios da interface web.",
     "Acesse /scan/logs para visualizar o relatorio gerado."),

    (re.compile(r"Scan finalizado: projeto=(\S+) falhas=(\d+)", re.I),
     "📋 Scan concluido",
     "A varredura terminou. O campo 'falhas' mostra quantas vulnerabilidades foram detectadas. "
     "Falhas = 0 significa projeto limpo para os padroes verificados.",
     "Se houver falhas, abra o relatorio JSON para ver tipo, severidade e linha de cada ocorrencia."),

    (re.compile(r"Scan sem arquivos compativeis na raiz (.+)", re.I),
     "⚠️ Nenhum arquivo escaneavel",
     "O motor nao encontrou arquivos com extensoes suportadas (.py, .js, .ts, .go, etc.) "
     "na pasta informada. Pastas vazias ou com apenas binarios/imagens resultam neste aviso.",
     "Confirme que o caminho aponta para o codigo-fonte do projeto e nao para uma pasta de build/dist."),

    # ASPM — AMD/NVIDIA
    (re.compile(r"Relatorio (AMD|NVIDIA) JSON salvo em: (.+)", re.I),
     "💾 Relatorio GPU salvo",
     "O motor de scan especializado para GPU gerou e gravou o relatorio JSON. "
     "Esse arquivo e usado pela analise cognitiva (LM Studio) e pela auditoria web.",
     "Acesse /ia-local para visualizar e analisar o relatorio com IA."),

    (re.compile(r"Teste de log do sistema (AMD|NVIDIA)", re.I),
     "🧪 Linha de teste",
     "Linha gerada automaticamente pelos testes pytest para verificar se o logger "
     "AMD/NVIDIA esta gravando corretamente. Nao representa um problema real.",
     "Pode ser ignorada em ambiente de producao."),

    # ASPM — inicializacao
    (re.compile(r"ASPM PRIDE Security.*logger configurado", re.I),
     "🚀 Sistema iniciado",
     "O ASPM foi iniciado e o sistema de logs foi configurado com sucesso. "
     "Timestamps sao gravados no fuso local do servidor (indicado como UTC no arquivo).",
     "Nenhuma acao necessaria."),

    # Flask / Werkzeug
    (re.compile(r"Restarting with stat", re.I),
     "🔄 Reloader ativo",
     "O Flask detectou uma mudanca em um arquivo Python e reiniciou o servidor automaticamente. "
     "Isso e normal em modo debug/desenvolvimento.",
     "Em producao, use gunicorn ou uWSGI e desative o debug mode."),

    (re.compile(r"Debugger is active", re.I),
     "🐛 Debugger ativo",
     "O depurador interativo do Werkzeug esta habilitado. "
     "Qualquer erro nao tratado abrira um console Python diretamente no navegador.",
     "NUNCA habilite o debugger em producao — representa risco critico de execucao remota (RCE)."),

    (re.compile(r"Debugger PIN: ([\d-]+)", re.I),
     "🔑 PIN do debugger",
     "Este e o codigo de acesso para o console de depuracao do Werkzeug no navegador. "
     "Qualquer pessoa com acesso a rede e a este PIN pode executar codigo arbitrario no servidor.",
     "Em producao remova debug=True da chamada app.run()."),

    # Python — erros comuns
    (re.compile(r"ModuleNotFoundError: No module named '(.+)'", re.I),
     "📦 Modulo nao encontrado",
     "O Python tentou importar um pacote que nao esta instalado no ambiente virtual atual.",
     "Execute: pip install <nome_do_modulo> ou verifique se o ambiente virtual correto esta ativo."),

    (re.compile(r"FileNotFoundError", re.I),
     "📁 Arquivo nao encontrado",
     "O sistema tentou abrir ou ler um arquivo que nao existe no caminho especificado.",
     "Verifique se o arquivo existe, se o caminho esta correto e se ha permissao de leitura."),

    (re.compile(r"PermissionError", re.I),
     "🔒 Permissao negada",
     "O processo nao tem permissao para acessar um arquivo ou diretorio.",
     "Verifique as permissoes do arquivo (chmod/icacls) ou execute com privilegios adequados."),

    (re.compile(r"ConnectionRefusedError|Connection refused", re.I),
     "🔌 Conexao recusada",
     "A aplicacao tentou conectar a um servico (banco de dados, LM Studio, API) que nao esta respondendo.",
     "Verifique se o servico alvo esta rodando. Para LM Studio: inicie em localhost:1234."),

    (re.compile(r"TimeoutError|timed out", re.I),
     "⏱️ Timeout",
     "Uma operacao de rede ou I/O demorou mais do que o tempo limite configurado.",
     "Verifique a conectividade de rede, aumente o timeout se necessario ou cheque o servico remoto."),

    (re.compile(r"JSONDecodeError|json\.decoder", re.I),
     "🗂️ JSON invalido",
     "O sistema tentou ler um arquivo JSON mal-formado ou corrompido.",
     "Abra o arquivo indicado e verifique se e um JSON valido. Use jsonlint.com para validar."),

    (re.compile(r"UnicodeDecodeError", re.I),
     "🔤 Erro de encoding",
     "O Python nao conseguiu decodificar um arquivo de texto — provavelmente encoding incompativel (ex: latin-1 vs utf-8).",
     "Abra o arquivo com encoding='utf-8', errors='replace' ou converta o arquivo para UTF-8."),

    (re.compile(r"MemoryError", re.I),
     "💾 Memoria insuficiente",
     "O processo ficou sem memoria RAM disponivel.",
     "Reduza o tamanho do dado processado, aumente a RAM ou use processamento por lotes (chunks)."),

    (re.compile(r"RecursionError", re.I),
     "🔁 Recursao infinita",
     "Uma funcao chamou a si mesma recursivamente sem condicao de parada, esgotando a pilha.",
     "Revise a logica da funcao recursiva e adicione um caso base claro."),

    (re.compile(r"Traceback \(most recent call last\)", re.I),
     "💥 Traceback de excecao",
     "Uma excecao nao tratada foi lanada. As linhas seguintes mostram a pilha de chamadas ate o erro.",
     "Leia as linhas abaixo para identificar o arquivo, linha e tipo do erro. Corrija o codigo indicado."),

    # Teste de persistencia
    (re.compile(r"Teste de persistencia de log", re.I),
     "🧪 Teste de log",
     "Linha gravada manualmente para verificar que o sistema de logging esta funcionando.",
     "Pode ser ignorada — e apenas uma entrada de teste."),
]


def _explicar_mensagem(mensagem):
    """Retorna dict com explicacao didatica ou None se nao houver correspondencia."""
    for padrao, titulo, explicacao, acao in _EXPLICACOES:
        m = padrao.search(mensagem)
        if m:
            return {
                "titulo": titulo,
                "explicacao": explicacao,
                "acao": acao,
                "grupos": list(m.groups()),
            }
    return None


# Padrao: 2026-05-26 15:31:08,139 - INFO - ASPM.modulo - mensagem
_RE_LOG = re.compile(
    r"^(?P<data>\d{4}-\d{2}-\d{2})\s+"
    r"(?P<hora>\d{2}:\d{2}:\d{2}),(?P<ms>\d+)"
    r"\s+-\s+(?P<nivel_raw>[A-Z]+)"
    r"\s+-\s+(?P<resto>.*)$"
)


def _nivel_para_classe(nivel_raw):
    """Converte nivel textual do log em classe CSS."""
    valor = nivel_raw.upper()
    if valor in ("CRITICAL", "CRITICO", "FATAL"):
        return "error"
    if valor == "ERROR":
        return "error"
    if valor in ("WARNING", "WARN"):
        return "warning"
    if valor == "INFO":
        return "info"
    if valor == "DEBUG":
        return "debug"
    return "trace"


def classificar_linhas_log(conteudo):
    """Parseia e classifica cada linha do log.

    Retorna lista de dicts com campos:
      data, hora, ms, nivel_raw, nivel (classe css), modulo, mensagem, texto (linha bruta).
    """
    if not conteudo:
        return []

    resultado = []
    for linha in conteudo.splitlines():
        match = _RE_LOG.match(linha)
        if match:
            nivel_raw = match.group("nivel_raw")
            resto = match.group("resto")
            # separa modulo opcional: "ASPM.modulo - mensagem" ou direto "mensagem"
            partes = resto.split(" - ", 1)
            modulo = partes[0].strip() if len(partes) == 2 else ""
            mensagem = partes[1].strip() if len(partes) == 2 else resto.strip()
            nivel_cls = _nivel_para_classe(nivel_raw)
            dica = _explicar_mensagem(mensagem) if nivel_cls in ("error", "warning") else None
            # INFO de interesse especifico tambem recebe dica
            if dica is None:
                dica = _explicar_mensagem(mensagem)
            resultado.append({
                "data": match.group("data"),
                "hora": match.group("hora"),
                "ms": match.group("ms"),
                "nivel_raw": nivel_raw,
                "nivel": nivel_cls,
                "modulo": modulo,
                "mensagem": mensagem,
                "texto": linha,
                "estruturado": True,
                "dica": dica,
            })
        else:
            # linha nao-estruturada: coloriza por palavras-chave
            linha_upper = linha.upper()
            if any(kw in linha_upper for kw in ("CRITICAL", "CRITICO", "ERROR", "ERRO")):
                nivel = "error"
            elif any(kw in linha_upper for kw in ("WARNING", "WARN", "AVISO")):
                nivel = "warning"
            elif "INFO" in linha_upper:
                nivel = "info"
            elif "DEBUG" in linha_upper:
                nivel = "debug"
            else:
                nivel = "trace"
            resultado.append({
                "data": "", "hora": "", "ms": "",
                "nivel_raw": nivel.upper(),
                "nivel": nivel,
                "modulo": "",
                "mensagem": linha,
                "texto": linha,
                "estruturado": False,
                "dica": _explicar_mensagem(linha),
            })
    return resultado


def listar_relatorios_generic():
    """Lista JSONs em logs/generic/reports."""
    pasta = os.path.join(obter_diretorio_logs(), "generic", "reports")
    if not os.path.isdir(pasta):
        return []

    return sorted(
        [nome for nome in os.listdir(pasta) if nome.endswith(".json")],
        reverse=True,
    )


def abrir_pasta_logs_explorador():
    """Abre pasta logs/ no explorador do SO."""
    pasta = obter_diretorio_logs()
    if not os.path.isdir(pasta):
        return False, "Pasta logs nao encontrada."

    try:
        if os.name == "nt":
            os.startfile(pasta)
        else:
            subprocess.run(["xdg-open", pasta], check=False)
        return True, f"Pasta aberta: {pasta}"
    except OSError as erro:
        return False, f"Nao foi possivel abrir a pasta: {erro}"
