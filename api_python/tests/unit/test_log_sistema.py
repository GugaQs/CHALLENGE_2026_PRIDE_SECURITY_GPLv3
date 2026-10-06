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
import unittest
import logging
from app.utils.log_sistema import get_logger, get_hardware_logger, _pasta_logs_api_python

class TestLogSistema(unittest.TestCase):
    def test_pasta_logs_base(self):
        """Verifica se a pasta base de logs e resolvida corretamente."""
        pasta = _pasta_logs_api_python()
        self.assertTrue(pasta.endswith("logs"))
        self.assertTrue(os.path.isabs(pasta))

    def test_get_logger_basic(self):
        """Verifica se o logger basico e retornado."""
        log = get_logger("teste_unitario")
        self.assertIsInstance(log, logging.Logger)
        self.assertEqual(log.name, "ASPM.teste_unitario")

    def test_get_hardware_logger_amd(self):
        """Verifica se o logger AMD e criado no local correto."""
        log = get_hardware_logger("amd")
        self.assertEqual(log.name, "ASPM.amd")
        
        # Verifica se o handler aponta para o caminho correto
        found_handler = False
        for handler in log.handlers:
            if isinstance(handler, logging.FileHandler):
                if "logs" in handler.baseFilename and "amd" in handler.baseFilename and "system" in handler.baseFilename:
                    found_handler = True
                    break
        self.assertTrue(found_handler, "FileHandler para AMD system nao encontrado ou em local errado.")

    def test_get_hardware_logger_nvidia(self):
        """Verifica se o logger NVIDIA e criado no local correto."""
        log = get_hardware_logger("nvidia")
        self.assertEqual(log.name, "ASPM.nvidia")
        
        found_handler = False
        for handler in log.handlers:
            if isinstance(handler, logging.FileHandler):
                if "logs" in handler.baseFilename and "nvidia" in handler.baseFilename and "system" in handler.baseFilename:
                    found_handler = True
                    break
        self.assertTrue(found_handler, "FileHandler para NVIDIA system nao encontrado ou em local errado.")

if __name__ == "__main__":
    unittest.main()
