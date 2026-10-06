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
Validação de dados do cadastro de usuário (protótipo educativo).

Objetivo pedagógico
-------------------
- Reduzir lixo no arquivo `usuarios.txt` e erros bobos (CPF incompleto, e-mail sem @).
- Mostrar que validação **no cliente/CLI** é só a primeira camada; em produção repete-se
  no servidor e com regras de negócio.

Limitações honestas
-------------------
- E-mail: verificação por **padrão simplificado**, não implementa o RFC 5322 completo.
- CPF: algoritmo oficial dos dígitos verificadores; números **matematicamente válidos**
  podem ainda ser **falsos** na vida real (consulta à Receita é outra história).

Referência sugerida no documento de análise: evolução futura com **Pydantic** ou API REST.
"""

from __future__ import annotations

import re

# Ex.: usuario@sub.dominio.br — suficiente para laboratório; não cobre todos os casos RFC.
_PADRAO_EMAIL_SIMPLES = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z]{2,})+$"
)

def _cpf_todos_digitos_iguais(onze_digitos: str) -> bool:
    """True se os 11 dígitos são todos iguais (CPF matematicamente inválido no Brasil)."""
    return len(set(onze_digitos)) == 1


def normalizar_cpf(texto: str) -> str:
    """
    Mantém apenas dígitos — aceita entrada formatada (123.456.789-09).

    Por que normalizar?
    ------------------
    Armazenar sempre 11 dígitos facilita comparar e validar; a formatação é só visual.
    """
    return "".join(c for c in texto if c.isdigit())


def formatar_cpf_exibicao(onze_digitos: str) -> str:
    """
    Converte 11 dígitos em `000.000.000-00` só para leitura humana (CLI/recibo).

    Não valida dígitos verificadores; use após `normalizar_cpf` e validação bem-sucedida.
    Se não houver exatamente 11 dígitos após extrair números, devolve o texto original
    (fallback defensivo).
    """
    d = "".join(c for c in onze_digitos if c.isdigit())
    if len(d) != 11:
        return onze_digitos.strip()
    return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"


def validar_cpf(texto: str) -> tuple[bool, str]:
    """
    Valida CPF brasileiro pelos dois dígitos verificadores.

    Retorno:
        (True, "") se válido.
        (False, "mensagem") se inválido — mensagem curta para exibir no terminal.

    Algoritmo (resumo):
        1) Exige 11 dígitos após normalização.
        2) Rejeita sequências 000..., 111..., ... 999...
        3) Calcula o 10º e o 11º dígitos com pesos oficiais e compara com os informados.
    """
    cpf = normalizar_cpf(texto)
    if len(cpf) != 11:
        return False, "CPF deve conter 11 dígitos (pode usar pontos e traço)."
    if _cpf_todos_digitos_iguais(cpf):
        return False, "CPF invalido (sequencia repetida)."

    # Primeiro dígito verificador (posição 9 no índice 0-based)
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito_esperado = 0 if resto < 2 else 11 - resto
    if digito_esperado != int(cpf[9]):
        return False, "CPF invalido (digito verificador)."

    # Segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito_esperado = 0 if resto < 2 else 11 - resto
    if digito_esperado != int(cpf[10]):
        return False, "CPF invalido (digito verificador)."

    return True, ""


def normalizar_email(texto: str) -> str:
    """Remove espaços nas pontas; não altera maiúsculas (parte local pode ser sensível)."""
    return texto.strip()


def validar_email(texto: str) -> tuple[bool, str]:
    """
    Valida formato “razoável” de e-mail para o protótipo.

    Em produção você pode usar:
        - biblioteca `email-validator`;
        - ou Pydantic `EmailStr` quando migrar para API.
    """
    email = normalizar_email(texto)
    if not email:
        return False, "E-mail nao pode ser vazio."
    if len(email) > 254:
        return False, "E-mail excede tamanho maximo aceito."
    if not _PADRAO_EMAIL_SIMPLES.match(email):
        return False, "Formato de e-mail invalido (ex.: nome@dominio.com)."
    return True, ""


def normalizar_nome(texto: str) -> str:
    """Remove espaços extras no início/fim; múltiplos espaços internos viram um só."""
    partes = texto.strip().split()
    return " ".join(partes)


def validar_nome(texto: str) -> tuple[bool, str]:
    """
    Regras simples para nome legível no arquivo e na listagem.

    Não bloqueia caracteres acentuados (usuários brasileiros).
    """
    nome = normalizar_nome(texto)
    if len(nome) < 2:
        return False, "Nome muito curto (minimo 2 caracteres validos)."
    if len(nome) > 120:
        return False, "Nome muito longo (maximo 120 caracteres)."
    return True, ""


def validar_formulario_cadastro(nome: str, email: str, cpf: str) -> tuple[bool, str]:
    """
    Executa todas as validações na ordem: nome → e-mail → CPF.

    Retorno:
        (True, "") se tudo ok (use `normalizar_*` ao gravar).
        (False, mensagem) com o primeiro erro encontrado.
    """
    ok, msg = validar_nome(nome)
    if not ok:
        return False, msg
    ok, msg = validar_email(email)
    if not ok:
        return False, msg
    ok, msg = validar_cpf(cpf)
    if not ok:
        return False, msg
    return True, ""
