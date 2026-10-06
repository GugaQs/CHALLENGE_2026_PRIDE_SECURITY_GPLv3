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
 * Inicializacao do Mermaid na pagina de documentacao.
 *
 * PROPOSITO DE NEGOCIO
 * --------------------
 * A rota /documentacao/ renderiza os arquivos Markdown do repositorio dentro da
 * interface web. Os diagramas de arquitetura desses documentos sao escritos em
 * Mermaid e precisam virar SVG no navegador para que a equipe leia a arquitetura
 * sem sair da aplicacao.
 *
 * INVARIANTES DO DOMINIO
 * ----------------------
 * - Este arquivo e servido como estatico (/static/js/docs-mermaid.js) porque a
 *   Content-Security-Policy da aplicacao e `script-src 'self'`: script inline e
 *   script vindo de CDN externo sao BLOQUEADOS pelo navegador. A versao anterior
 *   era um `<script type="module">` inline importando de cdn.jsdelivr.net, e por
 *   isso nunca executava — nenhum diagrama chegava a aparecer.
 * - O bundle do Mermaid tambem e servido localmente (/static/js/mermaid.min.js)
 *   pelo mesmo motivo. Dependencia externa em pagina do sistema fica proibida.
 * - O tema fica fixo em "dark" para acompanhar a paleta da interface.
 * - `securityLevel: "strict"` impede que HTML dentro de um rotulo de diagrama seja
 *   interpretado. O conteudo vem de arquivos do proprio repositorio, mas manter
 *   estrito custa zero e evita criar um vetor de XSS por Markdown.
 *
 * COMPORTAMENTO EM CASO DE FALHA
 * ------------------------------
 * - Se `window.mermaid` nao existir (bundle nao carregou), a funcao retorna em
 *   silencio e o bloco continua legivel como texto. A pagina nao quebra.
 * - Se um diagrama tiver sintaxe invalida, o Mermaid marca aquele bloco com a
 *   propria mensagem de erro e segue renderizando os demais.
 */
(function () {
    "use strict";

    if (!window.mermaid) {
        return;
    }

    window.mermaid.initialize({
        startOnLoad: true,
        theme: "dark",
        securityLevel: "strict",
        fontFamily: '"Segoe UI", Tahoma, Arial, sans-serif',
        themeVariables: {
            background: "#0B1220",
            primaryColor: "#152239",
            primaryTextColor: "#EAF2F7",
            primaryBorderColor: "#00FDFF",
            lineColor: "#6b8ba3",
            secondaryColor: "#1c2c47",
            tertiaryColor: "#111c30"
        }
    });
})();
