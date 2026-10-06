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

"""Entrypoint padrao da aplicacao Flask."""

import os
import threading
import webbrowser

from app.web.app import create_app


app = create_app()


def _abrir_navegador_automaticamente(url):
    """Abre navegador sem bloquear a inicializacao do servidor."""
    timer = threading.Timer(1.0, lambda: webbrowser.open(url))
    timer.daemon = True
    timer.start()


if __name__ == "__main__":
    # Evita abrir duas vezes quando o reloader do Flask reinicia o processo.
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        _abrir_navegador_automaticamente("http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
