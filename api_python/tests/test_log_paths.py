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

import os
import sys

# Adiciona o path para importar o app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.log_sistema import get_hardware_logger

def test_logs():
    print("Testando logger AMD...")
    log_amd = get_hardware_logger("amd")
    log_amd.info("Teste de log do sistema AMD")
    
    print("Testando logger NVIDIA...")
    log_nvidia = get_hardware_logger("nvidia")
    log_nvidia.info("Teste de log do sistema NVIDIA")
    
    print("\nVerificando arquivos criados:")
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    paths = [
        os.path.join(base, "logs", "amd", "system", "sistema_amd.log"),
        os.path.join(base, "logs", "nvidia", "system", "sistema_nvidia.log")
    ]
    
    for p in paths:
        if os.path.exists(p):
            print(f"✅ Encontrado: {p}")
        else:
            print(f"❌ NÃO ENCONTRADO: {p}")

if __name__ == "__main__":
    test_logs()
