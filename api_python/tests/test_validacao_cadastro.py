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
Testes didáticos do modulo app.utils.validacao_cadastro.

Execute: pytest tests/test_validacao_cadastro.py -v
"""

import pytest

from app.utils import validacao_cadastro as val


@pytest.mark.parametrize(
    "cpf,esperado_ok",
    [
        ("529.982.247-25", True),  # valido (digitos verificadores corretos)
        ("11111111111", False),  # sequencia invalida
        ("123", False),  # curto demais
        ("52998224724", False),  # ultimo digito errado
    ],
)
def test_validar_cpf(cpf, esperado_ok):
    ok, _msg = val.validar_cpf(cpf)
    assert ok is esperado_ok


def test_validar_email_basico():
    assert val.validar_email("a@b.co")[0] is True
    assert val.validar_email("sem_arroba")[0] is False
    assert val.validar_email("")[0] is False


def test_validar_nome_tamanho():
    assert val.validar_nome("Ana")[0] is True
    assert val.validar_nome("A")[0] is False


def test_formulario_completo():
    ok, _ = val.validar_formulario_cadastro(
        "Maria Silva",
        "maria@example.com",
        "529.982.247-25",
    )
    assert ok is True


def test_formatar_cpf_exibicao():
    assert val.formatar_cpf_exibicao("52998224725") == "529.982.247-25"
    assert val.formatar_cpf_exibicao("529.982.247-25") == "529.982.247-25"
