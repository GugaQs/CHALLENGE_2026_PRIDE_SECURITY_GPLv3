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

// Lê o token CSRF do meta tag para usar em requisições fetch POST.
function obterCsrfToken() {
    var meta = document.querySelector("meta[name='csrf-token']");
    return meta ? meta.getAttribute("content") : "";
}

// Fecha apenas alertas de sucesso automaticamente; erros ficam visíveis.
setTimeout(function () {
    var alertas = document.querySelectorAll(".alerta.success, .alerta.info");
    alertas.forEach(function (alerta) {
        alerta.style.opacity = "0";
        setTimeout(function () {
            if (alerta.parentNode) {
                alerta.parentNode.removeChild(alerta);
            }
        }, 450);
    });
}, 4000);

// Sistema de toast in-page para substituir alert() nativo.
(function () {
    var container = null;

    function obterContainer() {
        if (!container) {
            container = document.createElement("div");
            container.className = "toast-container";
            document.body.appendChild(container);
        }
        return container;
    }

    function mostrarToast(mensagem, tipo, duracao) {
        tipo = tipo || "info";
        duracao = duracao !== undefined ? duracao : (tipo === "erro" ? 0 : 5000);

        var toast = document.createElement("div");
        toast.className = "toast toast--" + tipo;

        var icone = tipo === "ok" ? "✓" : tipo === "erro" ? "✕" : "ℹ";
        toast.innerHTML = "<span style=\"flex-shrink:0;font-weight:700\">" + icone + "</span><span>" + mensagem + "</span>";

        obterContainer().appendChild(toast);

        function remover() {
            toast.classList.add("toast--saindo");
            setTimeout(function () {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 270);
        }

        toast.addEventListener("click", remover);

        if (duracao > 0) {
            setTimeout(remover, duracao);
        }

        return remover;
    }

    window.notificar = mostrarToast;
}());

// Tooltip customizado para elementos clicaveis (links, botoes, cards).
(function () {
    if (!window.matchMedia || !window.matchMedia("(hover: hover)").matches) {
        return;
    }

    var seletorTooltip = [
        "button",
        "a",
        "input[type='submit']",
        "input[type='button']",
        ".linha-clicavel",
        "[role='button']"
    ].join(", ");

    var tooltip = document.createElement("div");
    tooltip.className = "tooltip-global oculto";
    document.body.appendChild(tooltip);
    var alvoAtivo = null;

    function posicionarTooltip(alvo) {
        var rect = alvo.getBoundingClientRect();
        var larguraMax = Math.min(340, window.innerWidth - 24);
        tooltip.style.maxWidth = larguraMax + "px";
        tooltip.style.left = "0px";
        tooltip.style.top = "0px";

        var tooltipRect = tooltip.getBoundingClientRect();
        var esquerda = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
        esquerda = Math.max(8, Math.min(esquerda, window.innerWidth - tooltipRect.width - 8));

        var topo = rect.top - tooltipRect.height - 10;
        if (topo < 8) {
            topo = rect.bottom + 10;
        }

        tooltip.style.left = (esquerda + window.scrollX) + "px";
        tooltip.style.top = (topo + window.scrollY) + "px";
    }

    function textoCurto(texto) {
        return (texto || "")
            .replace(/\s+/g, " ")
            .trim()
            .slice(0, 140);
    }

    function inferirTooltipSemantico(alvo, rotulo) {
        var href = (alvo.getAttribute("href") || "").toLowerCase();
        var id = (alvo.id || "").toLowerCase();
        var classes = (alvo.className || "").toLowerCase();
        var texto = (rotulo || "").toLowerCase();

        if (texto.indexOf("voltar") >= 0 || texto.indexOf("↩") >= 0 || texto.indexOf("⬅") >= 0) {
            return "Volta para a tela anterior relacionada ao fluxo atual.";
        }
        if (texto.indexOf("limpar") >= 0) {
            return "Limpa os filtros ou dados atuais desta tela.";
        }
        if (texto.indexOf("filtrar") >= 0) {
            return "Aplica os criterios selecionados para reduzir os resultados exibidos.";
        }
        if (texto.indexOf("json") >= 0 || href.indexOf("/json") >= 0) {
            return "Abre a visualizacao JSON bruta deste relatorio.";
        }
        if (texto.indexOf("auditoria") >= 0 || href.indexOf("/auditoria/") >= 0) {
            return "Abre a auditoria detalhada com severidade, arquivo e linha das falhas.";
        }
        if (texto.indexOf("logs") >= 0 || href.indexOf("/logs") >= 0) {
            return "Abre a area de logs tecnicos do sistema e do scan.";
        }
        if (texto.indexOf("relatorio") >= 0 || href.indexOf("/scan/logs") >= 0) {
            return "Abre a lista de relatorios de scan com filtros e detalhes.";
        }
        if (texto.indexOf("scan") >= 0 || href.indexOf("/scan") >= 0) {
            return "Abre a tela de varredura para iniciar um novo scan do projeto.";
        }
        if (texto.indexOf("ia local") >= 0 || href.indexOf("/ia-local") >= 0) {
            return "Abre o modulo de IA local para scan GPU e parecer cognitivo.";
        }
        if (texto.indexOf("sobre") >= 0 || href.indexOf("/sobre") >= 0) {
            return "Abre informacoes institucionais e detalhes da equipe do projeto.";
        }
        if (classes.indexOf("linha-clicavel") >= 0) {
            return "Abrir detalhes deste relatorio de scan.";
        }
        if (id.indexOf("btn-ir-fim") >= 0) {
            return "Rola o terminal de log ate a ultima linha.";
        }
        if (id.indexOf("btn-ir-topo") >= 0) {
            return "Rola o terminal de log de volta ao inicio.";
        }
        if (alvo.tagName === "A") {
            return "Abrir: " + rotulo;
        }
        if (alvo.tagName === "BUTTON" || alvo.getAttribute("role") === "button") {
            return "Executar acao: " + rotulo;
        }
        return rotulo;
    }

    function obterTextoAcao(alvo) {
        var explicacao = alvo.getAttribute("data-tooltip");
        if (explicacao) {
            return explicacao;
        }

        var title = alvo.getAttribute("title");
        if (title) {
            alvo.setAttribute("data-tooltip", title);
            alvo.removeAttribute("title");
            if (!alvo.getAttribute("aria-label")) {
                alvo.setAttribute("aria-label", title);
            }
            return title;
        }

        var rotulo = textoCurto(alvo.getAttribute("aria-label") || alvo.textContent);
        if (!rotulo) {
            return "";
        }

        return inferirTooltipSemantico(alvo, rotulo);
    }

    function mostrarTooltip(alvo) {
        if (!alvo || alvo.disabled) {
            return;
        }

        var textoTooltip = obterTextoAcao(alvo);
        if (!textoTooltip) {
            return;
        }
        alvoAtivo = alvo;
        tooltip.textContent = textoTooltip;
        tooltip.classList.remove("oculto");
        posicionarTooltip(alvo);
    }

    function esconderTooltip() {
        alvoAtivo = null;
        tooltip.classList.add("oculto");
    }

    document.addEventListener("mouseover", function (evento) {
        var alvo = evento.target.closest(seletorTooltip);
        if (!alvo) {
            return;
        }
        mostrarTooltip(alvo);
    });
    document.addEventListener("mouseout", function (evento) {
        var alvo = evento.target.closest(seletorTooltip);
        if (!alvo) {
            return;
        }
        if (evento.relatedTarget && alvo.contains(evento.relatedTarget)) {
            return;
        }
        esconderTooltip();
    });
    document.addEventListener("focusin", function (evento) {
        var alvo = evento.target.closest(seletorTooltip);
        if (alvo) {
            mostrarTooltip(alvo);
        }
    });
    document.addEventListener("focusout", function () {
        esconderTooltip();
    });

    window.addEventListener("scroll", function () {
        if (!alvoAtivo) {
            return;
        }
        posicionarTooltip(alvoAtivo);
    }, true);
    window.addEventListener("resize", function () {
        if (!alvoAtivo) {
            return;
        }
        posicionarTooltip(alvoAtivo);
    });
})();

// Submissao automatica ao mudar select — substitui onchange inline (necessario para CSP).
(function () {
    document.querySelectorAll(".auto-submit").forEach(function (el) {
        el.addEventListener("change", function () {
            if (el.form) {
                el.form.submit();
            }
        });
    });
}());

// Confirmacao em formularios sensiveis — substitui onsubmit inline (necessario para CSP).
(function () {
    document.querySelectorAll("[data-confirm]").forEach(function (form) {
        form.addEventListener("submit", function (e) {
            var msg = form.getAttribute("data-confirm");
            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    });
}());

// Busca pasta no computador local via backend Flask (scan e IA local).
(function () {
    var botoes = document.querySelectorAll(".btn-buscar-pasta");
    if (!botoes.length) {
        return;
    }

    botoes.forEach(function (botaoBusca) {
        if (!botaoBusca.getAttribute("title")) {
            botaoBusca.setAttribute(
                "title",
                "Abre o explorador de arquivos para escolher a pasta do projeto no disco local"
            );
        }
        var idCampo = botaoBusca.getAttribute("data-campo") || "caminho";
        var campoCaminho = document.getElementById(idCampo);
        if (!campoCaminho) {
            return;
        }

        var textoOriginal = botaoBusca.textContent;
        botaoBusca.addEventListener("click", function () {
            botaoBusca.disabled = true;
            botaoBusca.textContent = "⏳ Abrindo explorador...";

            // Quem desiste primeiro TEM de ser o servidor.
            // O servidor derruba o seletor em SEGUNDOS_LIMITE_SELETOR (120 s,
            // em app/web/services/scan_service.py) e mata a arvore de processos
            // do dialogo. Se o navegador abortasse antes — como fazia com 65 s —
            // a janela do explorador ficaria aberta e orfa na tela do usuario,
            // com o botao ja reabilitado convidando a clicar de novo.
            // Por isso este valor e MAIOR que o do servidor, com folga.
            var LIMITE_SELETOR_MS = 130000;
            var controller = new AbortController();
            var timer = setTimeout(function () { controller.abort(); }, LIMITE_SELETOR_MS);

            fetch("/scan/selecionar-pasta", {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-CSRFToken": obterCsrfToken() },
                signal: controller.signal
            })
                .then(function (response) {
                    return response.json();
                })
                .then(function (dados) {
                    if (dados.ok && dados.caminho) {
                        campoCaminho.value = dados.caminho;
                    } else if (dados.mensagem) {
                        notificar(dados.mensagem, "erro");
                    }
                })
                .catch(function (err) {
                    if (err.name === "AbortError") {
                        notificar("Tempo esgotado ao abrir seletor de pasta.", "erro");
                    } else {
                        notificar("Falha ao abrir seletor de pasta.", "erro");
                    }
                })
                .finally(function () {
                    clearTimeout(timer);
                    botaoBusca.disabled = false;
                    botaoBusca.textContent = textoOriginal;
                });
        });
    });
})();

// Atualiza pagina de logs automaticamente quando houver mudancas.
(function () {
    if (window.location.pathname !== "/scan/logs") {
        return;
    }

    var assinaturaAtual = null;

    function gerarAssinatura(dados) {
        var sistema = (dados.logs_sistema || []).map(function (item) {
            return [item.nome_arquivo, item.modificado_em, item.tamanho_kb];
        });
        var scan = (dados.logs_scan || []).map(function (item) {
            return [item.nome_arquivo, item.timestamp, item.total_falhas];
        });
        return JSON.stringify({ sistema: sistema, scan: scan });
    }

    function verificarMudancas() {
        fetch("/scan/logs/estado")
            .then(function (response) { return response.json(); })
            .then(function (dados) {
                if (!dados.ok) {
                    return;
                }

                var novaAssinatura = gerarAssinatura(dados);
                if (assinaturaAtual !== null && assinaturaAtual !== novaAssinatura) {
                    window.location.reload();
                    return;
                }
                assinaturaAtual = novaAssinatura;
            })
            .catch(function () {
                // Sem alerta para nao poluir UX em falhas temporarias.
            });
    }

    verificarMudancas();
    setInterval(verificarMudancas, 5000);
})();

// Abre arquivo relacionado a uma falha especifica por ID.
(function () {
    function abrirArquivoFalha(nomeLog, falhaId) {
        fetch("/scan/logs/" + encodeURIComponent(nomeLog) + "/abrir-falha", {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": obterCsrfToken() },
            body: JSON.stringify({ falha_id: falhaId })
        })
            .then(function (response) { return response.json(); })
            .then(function (resultado) {
                if (!resultado.ok) {
                    throw new Error(resultado.mensagem || "Nao foi possivel abrir o arquivo.");
                }
                notificar(resultado.mensagem || "Arquivo aberto com sucesso.", "ok");
            })
            .catch(function (erro) {
                notificar(erro.message || "Falha ao abrir arquivo da falha.", "erro");
            });
    }

    var botoesAcao = document.querySelectorAll(".abrir-falha-botao, .id-falha-botao");
    botoesAcao.forEach(function (botao) {
        botao.addEventListener("click", function () {
            var nomeLog = botao.getAttribute("data-log");
            var falhaId = botao.getAttribute("data-falha-id");
            if (!nomeLog || !falhaId) {
                return;
            }
            abrirArquivoFalha(nomeLog, falhaId);
        });
    });
})();

// Permite clicar na linha inteira para navegar no detalhe.
(function () {
    var linhas = document.querySelectorAll(".linha-clicavel");
    linhas.forEach(function (linha) {
        linha.addEventListener("click", function (evento) {
            if (evento.target && evento.target.tagName === "A") {
                return;
            }
            var href = linha.getAttribute("data-href");
            if (href) {
                window.location.href = href;
            }
        });
    });
})();

// Barra de progresso reutilizavel para escaneamentos assincronos.
function configurarBarraProgresso(opcoes) {
    var form = document.querySelector(opcoes.seletorForm);
    var botao = document.querySelector(opcoes.seletorBotao);
    var painel = document.getElementById("painel-progresso");
    var texto = document.getElementById("texto-progresso");
    var numeros = document.getElementById("numeros-progresso");
    var barra = document.getElementById("barra-progresso-preenchimento");

    if (!form || !botao || !painel || !texto || !numeros || !barra) {
        return;
    }

    var textoBotaoOriginal = botao.textContent;

    function atualizarBarra(dados) {
        var percentual = Number(dados.percentual || 0);
        var atual = Number(dados.atual || 0);
        var total = Number(dados.total || 0);
        barra.style.width = percentual + "%";
        texto.textContent = dados.mensagem || "Escaneamento em andamento...";
        numeros.textContent = percentual + "% (" + atual + "/" + total + ")";
    }

    function restaurarBotao() {
        botao.disabled = false;
        botao.textContent = textoBotaoOriginal;
    }

    function consultarStatus(jobId) {
        fetch(opcoes.urlStatus + encodeURIComponent(jobId))
            .then(function (response) { return response.json(); })
            .then(function (resultado) {
                if (!resultado.ok || !resultado.dados) {
                    throw new Error("Status invalido");
                }

                var dados = resultado.dados;
                atualizarBarra(dados);

                if (dados.status === "concluido") {
                    restaurarBotao();
                    if (typeof opcoes.aoConcluir === "function") {
                        opcoes.aoConcluir(dados);
                        return;
                    }
                    if (dados.redirect_url) {
                        window.location.href = dados.redirect_url;
                        return;
                    }
                    if (dados.nome_log) {
                        window.location.href = "/scan/logs/" + encodeURIComponent(dados.nome_log);
                        return;
                    }
                    notificar(dados.mensagem || "Escaneamento concluido.", "ok");
                    return;
                }

                if (dados.status === "erro") {
                    restaurarBotao();
                    notificar(dados.mensagem || "Falha no escaneamento.", "erro");
                    return;
                }

                setTimeout(function () { consultarStatus(jobId); }, 700);
            })
            .catch(function () {
                restaurarBotao();
                notificar("Falha ao consultar progresso do escaneamento.", "erro");
            });
    }

    form.addEventListener("submit", function (evento) {
        evento.preventDefault();
        var payload = typeof opcoes.obterPayload === "function" ? opcoes.obterPayload() : {};
        if (payload === false) {
            return;
        }

        painel.classList.remove("oculto");
        atualizarBarra({ percentual: 0, atual: 0, total: 0, mensagem: "Iniciando..." });
        botao.disabled = true;
        botao.textContent = opcoes.textoCarregando || "⏳ Escaneando...";

        fetch(opcoes.urlIniciar, {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": obterCsrfToken() },
            body: JSON.stringify(payload)
        })
            .then(function (response) { return response.json(); })
            .then(function (resultado) {
                if (!resultado.ok || !resultado.job_id) {
                    throw new Error(resultado.mensagem || "Nao foi possivel iniciar.");
                }
                consultarStatus(resultado.job_id);
            })
            .catch(function (erro) {
                restaurarBotao();
                notificar(erro.message || "Erro ao iniciar escaneamento.", "erro");
            });
    });
}

function renderizarArtefatosDocker(artefatos) {
    var painel = document.getElementById("painel-resultado-containers");
    var titulo = document.getElementById("titulo-resultado-containers");
    var mensagem = document.getElementById("mensagem-resultado-containers");
    var wrapper = document.getElementById("tabela-containers-wrapper");
    if (!painel || !titulo || !mensagem || !wrapper) {
        return;
    }

    artefatos = artefatos || [];
    painel.classList.remove("oculto");
    titulo.textContent = "Artefatos encontrados (" + artefatos.length + ")";
    mensagem.textContent = artefatos.length
        ? "Varredura concluida."
        : "Nenhum Dockerfile ou compose encontrado.";

    if (!artefatos.length) {
        wrapper.innerHTML = "";
        return;
    }

    var linhas = artefatos.map(function (item) {
        return "<tr><td>" + item.nome + "</td><td><code>" + item.caminho_relativo + "</code></td></tr>";
    }).join("");

    wrapper.innerHTML =
        "<table class=\"tabela-tatica\"><thead><tr><th>Arquivo</th><th>Caminho relativo</th></tr></thead><tbody>" +
        linhas +
        "</tbody></table>";
}

// Scan de projeto generico.
configurarBarraProgresso({
    seletorForm: "#form-scan",
    seletorBotao: "#btn-iniciar-scan",
    urlIniciar: "/scan/executar-assincrono",
    urlStatus: "/scan/status/",
    obterPayload: function () {
        var campo = document.getElementById("caminho");
        var caminho = campo ? (campo.value || "").trim() : "";
        if (!caminho) {
            notificar("Informe o caminho do projeto.", "erro");
            return false;
        }
        return { caminho: caminho };
    },
    textoCarregando: "⏳ Escaneando..."
});

// IA local — scan GPU.
configurarBarraProgresso({
    seletorForm: "#form-scan-ia",
    seletorBotao: "#btn-scan-ia",
    urlIniciar: "/ia-local/executar-assincrono",
    urlStatus: "/ia-local/status/",
    obterPayload: function () {
        var form = document.getElementById("form-scan-ia");
        var campo = document.getElementById("caminho-ia");
        var caminho = campo ? (campo.value || "").trim() : "";
        if (!caminho) {
            notificar("Informe o caminho do projeto.", "erro");
            return false;
        }
        return {
            caminho: caminho,
            hardware: form ? form.getAttribute("data-hardware") : "amd"
        };
    },
    textoCarregando: "⏳ Escaneando GPU..."
});

// IA local — scan cognitivo.
configurarBarraProgresso({
    seletorForm: "#form-cognitivo-ia",
    seletorBotao: "#btn-cognitivo-ia",
    urlIniciar: "/ia-local/cognitivo-assincrono",
    urlStatus: "/ia-local/status/",
    obterPayload: function () {
        var form = document.getElementById("form-cognitivo-ia");
        var campo = document.getElementById("caminho-ia");
        var caminho = campo ? (campo.value || "").trim() : "";
        if (!caminho) {
            notificar("Informe o caminho do projeto.", "erro");
            return false;
        }
        return {
            caminho: caminho,
            hardware: form ? form.getAttribute("data-hardware") : "amd"
        };
    },
    textoCarregando: "⏳ Scan cognitivo..."
});

// Containers Docker.
configurarBarraProgresso({
    seletorForm: "#form-containers",
    seletorBotao: "#btn-scan-containers",
    urlIniciar: "/modulos/containers/executar-assincrono",
    urlStatus: "/modulos/containers/status/",
    obterPayload: function () {
        var campo = document.getElementById("caminho-docker");
        var caminho = campo ? (campo.value || "").trim() : "";
        if (!caminho) {
            notificar("Informe o caminho do projeto.", "erro");
            return false;
        }
        return { caminho: caminho };
    },
    textoCarregando: "⏳ Buscando artefatos...",
    aoConcluir: function (dados) {
        var extra = dados.extra || {};
        renderizarArtefatosDocker(extra.artefatos || []);
    }
});
