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

"""Regras de assinatura usadas pelo engine de scan de seguranca."""

from typing import TypeAlias

# Formato: ([padroes], "SEVERIDADE", "DESCRICAO_TECNICA", CONFIANCA, [refs])
Signature: TypeAlias = tuple[list[str], str, str, str, list[str]]

# Mapeamento numerico de severidade para ordenacao de resultados
SEVERIDADE_PESO: dict[str, int] = {
    "CRÍTICO": 4,
    "ALTO":    3,
    "MÉDIO":   2,
    "BAIXO":   1,
}


def obter_assinaturas_vulnerabilidade() -> dict[str, Signature]:
    """
    Retorna assinaturas de risco mapeadas com severidade, confianca e referencias.

    Formato de cada entrada:
        "Nome da Falha": (
            [lista de padroes],
            "SEVERIDADE",       # CRÍTICO | ALTO | MÉDIO | BAIXO
            "DESCRICAO_TECNICA",
            "CONFIANCA",        # ALTA | MÉDIA | BAIXA
            ["CWE-XXX", "https://owasp.org/...", "CVE-YYYY-NNNN opcional"],
        )
    """
    return {

        # ------------------------------------------------------------------
        # SQL
        # ------------------------------------------------------------------
        "Query SQL Detectada": (
            [
                "SELECT ", "INSERT INTO", "UPDATE ", "DELETE FROM",
                "stmt.executeQuery(", "stmt.executeUpdate(",
                "cursor.execute(", "db.execute(", "db.query(",
                "SqlCommand(", "SqlDataAdapter(",
            ],
            "BAIXO",
            "📌 Detecta uso de comandos/execucao SQL no codigo. Nao caracteriza falha "
            "por si so, mas indica superficie de risco que exige revisao de "
            "parametrizacao e controle de entrada.",
            "BAIXA",
            ["CWE-89", "https://owasp.org/www-community/attacks/SQL_Injection"],
        ),
        "SQL Injection Provavel": (
            [
                # Python (f-strings e concatenacao)
                'f"SELECT ', "f'SELECT ", 'f"INSERT ', "f'INSERT ",
                'f"UPDATE ', "f'UPDATE ", 'f"DELETE ', "f'DELETE ",
                '"SELECT " +', "'SELECT ' +",
                '"INSERT INTO " +', "'INSERT INTO ' +",
                '"UPDATE " +', "'UPDATE ' +",
                '"DELETE FROM " +', "'DELETE FROM ' +",
                # PHP (concatenacao com ponto)
                '"SELECT " .', "'SELECT ' .",
                '"INSERT INTO " .', "'INSERT INTO ' .",
                # Java / C#
                "String query =", "String sql =", "string sql =",
                # Ruby (interpolacao)
                '"SELECT #{', "'SELECT #{",
            ],
            "CRÍTICO",
            "🛑 Indica possivel construcao dinamica de SQL com interpolacao/concatenacao. "
            "Esse padrao pode permitir alteracao da consulta por dados externos. "
            "Mitigar com prepared statements, queries parametrizadas ou ORM.",
            "ALTA",
            [
                "CWE-89",
                "https://owasp.org/www-community/attacks/SQL_Injection",
                "CVE-2014-3704",
            ],
        ),

        # ------------------------------------------------------------------
        # RCE
        # ------------------------------------------------------------------
        "Execução de Risco (RCE)": (
            [
                # Java
                "Runtime.getRuntime().exec", "ProcessBuilder",
                # Python — execucao de sistema
                "os.system(", "subprocess.run(", "subprocess.Popen(", "popen(",
                # Python — execucao de codigo dinamico
                "eval(", "exec(", "compile(",
                "__import__(", "marshal.loads(",
                # subprocess com shell=True é especialmente perigoso
                "shell=True",
                # JS / Node
                "child_process.exec", "child_process.execSync",
                "execSync(", "Function(",
                # PHP
                "shell_exec(", "passthru(", "system(",
            ],
            "CRÍTICO",
            "💥 Sinaliza chamadas que executam comandos ou codigo dinamico no "
            "sistema operacional/runtime. Se alimentadas por entrada externa, podem "
            "gerar comprometimento total do host.",
            "MÉDIA",
            [
                "CWE-78",
                "CWE-94",
                "https://owasp.org/www-community/attacks/Code_Injection",
                "CVE-2021-44228",
            ],
        ),

        # ------------------------------------------------------------------
        # Credenciais
        # ------------------------------------------------------------------
        "Credenciais Hardcoded": (
            [
                # Atribuicoes com e sem espaco ao redor do '='
                "password =", "password=",
                "passwd =", "passwd=",
                "secret =", "secret=",
                "api_key =", "api_key=",
                "token =", "token=",
                "auth_token =", "auth_token=",
                # Connection strings
                "connectionString", "jdbc:mysql://", "mongodb://",
                # Provedores de nuvem / pagamento
                "AWSAccessKeyId", "stripe_secret",
            ],
            "ALTO",
            "🔐 Detecta segredos sensiveis embutidos no codigo-fonte (senhas, tokens, "
            "chaves e connection strings). Exposicao em repositorio/log pode "
            "comprometer ambientes e dados.",
            "MÉDIA",
            ["CWE-798", "https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password"],
        ),

        # ------------------------------------------------------------------
        # XSS
        # ------------------------------------------------------------------
        "XSS (Cross-Site Scripting)": (
            [
                # DOM direto
                "innerHTML", "outerHTML", "insertAdjacentHTML(",
                "document.write(", "setAttribute(\"onclick\"", "setAttribute('onclick'",
                # Servidor
                "response.write(", "out.println(", "context.setVariable",
                # React
                "dangerouslySetInnerHTML",
                # Templates sem escape
                "| safe", "mark_safe(",
                # eval em contexto de DOM
                "eval(location", "eval(document",
            ],
            "ALTO",
            "🌐 Identifica escrita/renderizacao HTML potencialmente insegura no "
            "cliente/servidor. Sem escape adequado, entrada controlada por usuario "
            "pode executar scripts no navegador de terceiros.",
            "MÉDIA",
            [
                "CWE-79",
                "https://owasp.org/www-community/attacks/xss/",
                "CVE-2020-11022",
            ],
        ),

        # ------------------------------------------------------------------
        # Path Traversal / LFI
        # ------------------------------------------------------------------
        "Path Traversal / LFI": (
            [
                "file://", "java.io.File(", "FileReader(",
                "fs.readFileSync(", "fs.readFile(",
                # Correlacionar open() com entrada externa reduz falso positivo
                "open(request.", "open(req.", "open(params[",
                "include($_GET", "require_once(", "require(", "include(",
            ],
            "ALTO",
            "📂 Aponta manipulacao potencialmente insegura de caminhos/arquivos. "
            "Sem normalizacao e allowlist de diretorios, pode ocorrer leitura de "
            "arquivos fora do escopo permitido (LFI/Traversal).",
            "MÉDIA",
            ["CWE-22", "https://owasp.org/www-community/attacks/Path_Traversal"],
        ),

        # ------------------------------------------------------------------
        # Entradas externas
        # ------------------------------------------------------------------
        "Entrada Externa para Revisão": (
            [
                "Scanner(", "System.in", "input(",
                "request.form", "request.args", "request.json",
                "getParameter(", "readLine(",
                "req.body", "req.query", "req.params",
                "$_GET[", "$_POST[", "$_REQUEST[",
            ],
            "BAIXO",
            "🧪 Marca pontos de entrada de dados externos. Nao e vulnerabilidade "
            "isolada, mas deve ser correlacionada com uso sensivel (SQL, shell, "
            "arquivo, HTML) e validacao/sanitizacao.",
            "BAIXA",
            ["CWE-20", "https://owasp.org/www-project-top-ten/"],
        ),

        # ------------------------------------------------------------------
        # Configuracao insegura
        # ------------------------------------------------------------------
        "Configuração Insegura / CORS": (
            [
                "debug=True", "DEBUG = True",
                "AllowAnyOrigin", "CORS_ALLOW_ALL",
                "disable_web_security", "verify=False",
                "origin: '*'", "Access-Control-Allow-Origin: *",
            ],
            "BAIXO",
            "⚙️ Detecta configuracoes de desenvolvimento ou permissivas em excesso "
            "(debug, CORS amplo, TLS sem verificacao). Em producao, ampliam superficie "
            "de ataque e risco de interceptacao.",
            "MÉDIA",
            ["CWE-16", "https://owasp.org/www-project-top-ten/"],
        ),

        # ------------------------------------------------------------------
        # SSRF
        # ------------------------------------------------------------------
        "SSRF (Server-Side Request Forgery)": (
            [
                "requests.get(", "requests.post(",
                "urllib.request.urlopen(",
                "URL.openConnection(", "HttpClient(", "RestTemplate",
                "axios.get(", "fetch(", "http.GetAsync(",
            ],
            "ALTO",
            "🌍 Detecta pontos onde o servidor realiza requisicoes de saida. "
            "Sem validacao de destino, entrada externa pode forcar acesso a "
            "recursos internos/metadados (SSRF).",
            "BAIXA",
            ["CWE-918", "https://owasp.org/www-community/attacks/Server_Side_Request_Forgery"],
        ),

        # ------------------------------------------------------------------
        # Deserializacao
        # ------------------------------------------------------------------
        "Deserialização Insegura": (
            [
                "pickle.loads(", "pickle.load(",
                "yaml.load(", "yaml.unsafe_load(",
                "ObjectInputStream", "readObject(",
                "BinaryFormatter", "unserialize(",
                "jsonpickle.decode(",
            ],
            "CRÍTICO",
            "📦 Sinaliza desserializacao de dados potencialmente nao confiaveis. "
            "Esse vetor pode levar a execucao arbitraria de codigo, manipulacao "
            "de objetos e comprometimento da aplicacao.",
            "ALTA",
            ["CWE-502", "https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data"],
        ),

        # ------------------------------------------------------------------
        # TLS/SSL
        # ------------------------------------------------------------------
        "TLS/SSL Inseguro": (
            [
                "verify=False", "rejectUnauthorized: false",
                "ssl._create_unverified_context", "HostnameVerifier", "TrustAll",
                "CERT_NONE", "check_hostname = False",
            ],
            "ALTO",
            "🔒 Detecta desativacao de validacao criptografica em conexoes TLS/SSL. "
            "Pode permitir ataques Man-in-the-Middle e quebra de "
            "confidencialidade/integridade do trafego.",
            "ALTA",
            ["CWE-295", "https://owasp.org/www-community/controls/Certificate_and_Public_Key_Pinning"],
        ),

        # ------------------------------------------------------------------
        # JWT Inseguro  (NOVO)
        # ------------------------------------------------------------------
        "JWT Inseguro": (
            [
                "algorithm='none'", 'algorithm="none"',
                "algorithms=['none']", 'algorithms=["none"]',
                "verify=False",   # jwt.decode(..., verify=False)
                "options={\"verify_signature\": False}",
                "options={'verify_signature': False}",
            ],
            "ALTO",
            "🪙 Detecta uso inseguro de JSON Web Tokens: algoritmo 'none' permite "
            "forjar tokens sem assinatura; desativar verificacao de assinatura anula "
            "a garantia de autenticidade.",
            "ALTA",
            ["CWE-347", "https://owasp.org/www-community/attacks/JWT_vulnerabilities"],
        ),

        # ------------------------------------------------------------------
        # XXE  (NOVO)
        # ------------------------------------------------------------------
        "XXE (XML External Entity)": (
            [
                "XMLParser", "etree.parse(", "DocumentBuilder",
                "SAXParserFactory", "xml.dom.minidom.parseString(",
                "libxml2", "simplexml_load_string(",
                "LOAD_EXTERNAL_DTD", "FEATURE_EXTERNAL_GENERAL_ENTITIES",
            ],
            "ALTO",
            "📄 Identifica parsers XML que podem processar entidades externas. "
            "Sem desativacao de DTD/entidades externas, entrada maliciosa pode "
            "vazar arquivos internos ou disparar SSRF via XML.",
            "MÉDIA",
            ["CWE-611", "https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing"],
        ),

        # ------------------------------------------------------------------
        # Logging sensivel  (NOVO)
        # ------------------------------------------------------------------
        "Logging de Dados Sensíveis": (
            [
                "log.info(password", "log.debug(password",
                "logger.info(password", "logger.debug(password",
                "console.log(token", "console.log(password",
                "print(password", "print(secret", "print(token",
                "logging.info(password", "logging.debug(password",
            ],
            "MÉDIO",
            "📋 Detecta possiveis registros de dados sensiveis em logs. "
            "Credenciais/tokens em logs podem ser capturados por terceiros com "
            "acesso ao sistema de logging.",
            "MÉDIA",
            ["CWE-532", "https://owasp.org/www-community/vulnerabilities/Sensitive_Data_Exposure"],
        ),

        # ------------------------------------------------------------------
        # ReDoS  (NOVO)
        # ------------------------------------------------------------------
        "Regex Vulnerável (ReDoS)": (
            [
                "(.+)+", "(.*)+", "(.+)*",
                "(a|a)+", "(a+)+",
                "re.compile(.*\\*.*\\*",   # regex com quantificadores aninhados
            ],
            "BAIXO",
            "⏱️ Detecta padroes de expressao regular potencialmente vulneraveis a "
            "Catastrophic Backtracking (ReDoS). Entrada maliciosa pode causar "
            "consumo exponencial de CPU e indisponibilidade do servico.",
            "BAIXA",
            ["CWE-1333", "https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS"],
        ),
    }


def obter_extensoes_permitidas() -> list[str]:
    """Retorna extensoes consideradas no processo de scan."""
    return [
        ".java", ".py", ".js", ".html", ".sh",
        ".cs",    # C#
        ".jsx",   # React JavaScript
        ".tsx",   # React TypeScript
        ".ts",    # TypeScript
        ".php",   # PHP
        ".rb",    # Ruby
        ".go",    # Go
        ".kt",    # Kotlin
    ]


def obter_diretorios_ignorados() -> list[str]:
    """Retorna diretorios ignorados para evitar ruido e ganho de performance."""
    return [
        ".git", "__pycache__", ".idea", "target",
        "node_modules", "venv", ".venv", "dist", "build",
        "bin", "obj", ".vs", "coverage", ".next",
        "site-packages", ".pytest_cache", ".mypy_cache",
        ".tox", ".eggs", "htmlcov",
    ]


def ordenar_por_severidade(
    resultados: list[dict],
    chave_severidade: str = "severidade",
) -> list[dict]:
    """
    Ordena uma lista de resultados de scan do mais critico ao menos critico.

    Args:
        resultados: lista de dicts com ao menos a chave `chave_severidade`.
        chave_severidade: nome do campo de severidade em cada dict.

    Returns:
        Lista ordenada (in-place nao; retorna nova lista).
    """
    return sorted(
        resultados,
        key=lambda r: SEVERIDADE_PESO.get(r.get(chave_severidade, "BAIXO"), 0),
        reverse=True,
    )