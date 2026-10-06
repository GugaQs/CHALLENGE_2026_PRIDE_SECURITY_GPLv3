/*
 * Copyright (C) 2026 Equipe ASPM IA FIAP - Challenge 2026
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See LICENSE.md
 * for the full GNU General Public License.
 */

/**
 * Comportamento do terminal de log (pagina de detalhe de log de sistema).
 *
 * PROPOSITO DE NEGOCIO
 * --------------------
 * A tela de detalhe de log mostra centenas de linhas coloridas por nivel. Quem
 * investiga um incidente precisa de dois movimentos: saltar direto para a ultima
 * linha (onde o erro acabou de acontecer) e voltar ao inicio. Alem disso, cada
 * linha de WARNING/ERROR pode trazer uma dica didatica explicando a causa provavel,
 * que fica recolhida para nao poluir a leitura.
 *
 * INVARIANTES DO DOMINIO
 * ----------------------
 * - Este arquivo e servido como estatico (/static/js/log-terminal.js) porque a
 *   Content-Security-Policy da aplicacao e `script-src 'self'`, sem 'unsafe-inline'.
 *   O mesmo codigo vivia num `<script>` inline no template e por isso era
 *   BLOQUEADO pelo navegador: os botoes de rolagem e o toggle das dicas nao
 *   funcionavam, sem nenhum aviso na tela.
 * - A classe `.oculto` e o contrato de visibilidade compartilhado com o style.css;
 *   trocar por `style.display` quebraria a consistencia com o resto da interface.
 * - A dica de uma linha e SEMPRE o irmao imediatamente seguinte no DOM
 *   (`.log-linha` + `.log-dica`). O template gera nessa ordem; se a ordem mudar,
 *   o toggle deixa de encontrar a dica e nao faz nada — nunca abre a dica errada.
 * - O estado visual do botao (`--ativo`) acompanha o estado real da dica, para
 *   que o operador nunca veja um botao aceso com a dica fechada.
 *
 * COMPORTAMENTO EM CASO DE FALHA
 * ------------------------------
 * - Elemento ausente (terminal ou botao) => o listener simplesmente nao e ligado.
 *   Nenhuma excecao e lancada e o restante da pagina segue funcional.
 * - Linha sem dica associada => o clique no toggle retorna sem efeito, em vez de
 *   abrir o elemento seguinte, que poderia ser outra linha de log.
 */
(function () {
    "use strict";

    var terminal = document.getElementById("log-terminal");
    var btnFim = document.getElementById("btn-ir-fim");
    var btnTopo = document.getElementById("btn-ir-topo");

    if (terminal && btnFim) {
        btnFim.addEventListener("click", function () {
            terminal.scrollTo({ top: terminal.scrollHeight, behavior: "smooth" });
        });
    }

    if (terminal && btnTopo) {
        btnTopo.addEventListener("click", function () {
            terminal.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    // Toggle das dicas didaticas.
    document.querySelectorAll(".log-dica-toggle").forEach(function (btn) {
        btn.addEventListener("click", function () {
            var linha = btn.closest(".log-linha");
            if (!linha) {
                return;
            }
            var dica = linha.nextElementSibling;
            if (!dica || !dica.classList.contains("log-dica")) {
                return;
            }
            var aberta = !dica.classList.contains("oculto");
            dica.classList.toggle("oculto", aberta);
            btn.classList.toggle("log-dica-toggle--ativo", !aberta);
            btn.setAttribute("aria-expanded", String(!aberta));
        });

        btn.setAttribute("aria-expanded", "false");
    });
})();
