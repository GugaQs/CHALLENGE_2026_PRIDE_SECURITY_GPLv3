# 🧪 04 - Testes — Flask Python

<p align="left">
  <img src="https://img.shields.io/badge/Doc-Testes_Flask-16A34A?style=flat&logo=pytest&logoColor=white" alt="Testes Flask">
  <img src="https://img.shields.io/badge/Stack-Pytest_%2B_Flask-0E7490?style=flat&logo=flask&logoColor=white" alt="Pytest e Flask">
  <img src="https://img.shields.io/badge/Testes-234-success?style=flat&logo=githubactions&logoColor=white" alt="234 testes">
  <img src="https://img.shields.io/badge/Cobertura_web-71%25-16A34A?style=flat&logo=codecov&logoColor=white" alt="Cobertura 71%">
</p>

**Navegação:** [📚 05 - Dicionário da documentação](../../documentacao/README.md) • [🌐 03 - Módulo Flask Python](../README.md) • [🐍 01 - API Python](../../api_python/README.md)

Este documento descreve a arquitetura da suíte de testes do módulo `flask-python`.

---

## 📊 Estado medido

```bash
cd flask-python
python -m pytest tests/ -q
```

| métrica | valor |
|---|---|
| Testes coletados | **234** |
| Passando | **215** |
| `xfail` (defeitos registrados, ver abaixo) | **19** |
| Falhando | **0** |
| Cobertura de `app/web` + `app/utils` | **71%** |
| Tempo da suíte completa | **12,8 s** (7,6 s com `-m "not lento"`) |

---

## 🧭 Os cinco princípios desta suíte

Não são estilo; cada um nasceu de um defeito real encontrado neste projeto.

### 1. Toda guarda é calibrada — vista reprovando antes de ser confiada

Um teste que nunca foi visto vermelho não prova nada. Antes de entrar na suíte,
cada guarda importante foi exercitada contra um **caso-controle doente**, com o
defeito injetado de propósito, e teve de reprovar. Depois o código foi
restaurado e ela teve de passar.

Calibrações executadas (defeito injetado → suíte reprovou → restaurado → passou):

| defeito injetado | guarda que pegou |
|---|---|
| `<script>` inline num template | `test_nenhum_template_tem_script_inline` |
| `<script src>` apontando para CDN | `test_nenhum_recurso_externo_alem_do_que_a_csp_declara` |
| `margin: 12px` no `style.css` | `test_style_css_nao_usa_px` |
| `--txt-3` escurecido para reprovar AA | `test_paleta_de_texto_passa_contraste_wcag_aa` |
| `X-Content-Type-Options` removido | 8 testes de `tests/seguranca/` |
| `'unsafe-inline'` acrescentado à CSP | 2 testes de contrato + segurança |
| `min(100, …)` trocado por `max(0, …)` | 2 testes de `test_utils.py` |
| um módulo removido do sandbox | `test_sandbox_cobre_todos_os_escritores` |
| arquivo real apagado durante a suíte | guarda de sessão `INV-TESTE-003` |
| filtro de severidade removido da rota | `test_auditoria_ia_local_filtra_por_severidade` |
| caminho VÁLIDO (`"."`) na lista de fuzz | guarda `INV-TESTE-003` (relatório real criado) |

### 2. Afirma o contrato, nunca o rótulo de tela

`test_auditoria_ia_local_filtra_por_severidade` ficou vermelho desde que nasceu
porque procurava a string `"Filtrar por severidade"` — que **nunca existiu em
nenhuma versão do template** (`git log -S` confirma). Pior: mesmo se existisse,
passaria com o filtro completamente desligado.

A regra que ficou: afirmar `name="severidade"` (o que a rota lê em
`request.args`) e o **efeito** (a falha ALTO entra, a CRÍTICO sai). Rótulo é
texto de tela e muda com o design; contrato não.

### 3. Rodar a suíte é operação segura

Antes, `pytest` escrevia nos logs reais, deixava resíduo permanente em
`logs/generic/reports/` e podia **sobrescrever um relatório real do usuário**
(os nomes são gerados por segundo). Numa auditoria automatizada deste projeto,
relatórios foram efetivamente apagados e o `.gitignore` impediu recuperá-los.

O `conftest.py` fecha isso com quatro invariantes — ver a seção seguinte.

**E a guarda já falhou uma vez, durante a própria construção da suíte.** A lista
de valores do teste de fuzz incluía `"."` e `"../../.."`, que são **diretórios
válidos**: cada POST disparava um scan real da árvore inteira numa thread de
fundo. A thread sobrevive ao teardown da fixture, então gravava três relatórios
de 1,2 MB no `logs/` verdadeiro — e a guarda, que só olhava arquivos apagados e
alterados, deixava passar em silêncio. Corrigido nas duas pontas: a lista de
fuzz não contém mais caminho existente, e a guarda passou a reprovar também
arquivo **criado**. Efeito colateral medido: a suíte caiu de 80 s para 12,8 s,
porque deixou de escanear o projeto inteiro dezenas de vezes.

### 4. Instrumento cego é pior que instrumento ausente

Vários testes carregam um **controle positivo** explícito: uma afirmação de que
o instrumento consegue enxergar. Sem ele, `/documentacao/arquivo` devolvendo 404
para tudo faria todos os testes de traversal passarem — por cegueira, não por
proteção.

### 5. Achado de auditoria vira teste, não documento

Ver [Registro executável de defeitos](#-registro-executável-de-defeitos).

---

## 🛡️ `conftest.py` — o alicerce

Quatro invariantes, todas verificadas por `tests/test_isolamento.py`:

| id | invariante | mecanismo |
|---|---|---|
| **INV-TESTE-001** | Nenhuma escrita fora do sandbox | Os 13 módulos que derivam a raiz do projeto de `os.path.dirname(__file__)` têm o `__file__` repontado para um temporário. **Isola sem alterar uma linha de código de produção.** |
| **INV-TESTE-002** | Nenhum acesso de rede | `socket.socket.connect` bloqueado. `/ia-local/` chama `localhost:1234` a cada GET; com o bloqueio, o caminho de erro real é exercitado e a suíte caiu de ~10 s para ~1,4 s. |
| **INV-TESTE-003** | Logs reais invioláveis | Fotografa `logs/` por SHA-256 antes e confere depois. Apagar, alterar **ou criar relatório** fora do sandbox **reprova a sessão inteira**, nomeando o arquivo. A checagem de arquivo *criado* foi acrescentada depois de um vazamento real — ver a nota abaixo. |
| **INV-TESTE-004** | Logger não vaza entre testes | Handlers do logger `ASPM` são fechados e removidos a cada teste. |

`test_sandbox_cobre_todos_os_escritores` varre o código atrás de módulos novos
que resolvam caminho de log e reprova se algum ficar fora do sandbox — foi ela
que encontrou 8 módulos faltando na primeira execução.

### Fixtures disponíveis

| fixture | para quê |
|---|---|
| `sandbox_de_caminhos` | raiz temporária do projeto; devolve o caminho para inspeção |
| `app` / `client` | aplicação em modo teste, CSRF desligado |
| `client_producao` | erro vira **500** em vez de propagar — para provar "nada derruba" |
| `client_csrf` | CSRF **ligado**, para os testes que provam a proteção |
| `projeto_vulneravel` | projeto de amostra com uma falha de cada categoria (controle positivo do motor) |
| `projeto_limpo` | projeto sem código analisável (controle negativo) |
| `relatorio_valido` | relatório JSON íntegro no sandbox |
| `payloads_traversal` | 10 vetores de path traversal, em lista única |

---

## 🧱 Estrutura

```text
tests/
├── conftest.py                          # isolamento e fixtures
├── test_isolamento.py            #  9  calibração do próprio sandbox
│
├── unit/                                # função isolada, sem HTTP
│   ├── test_scan_filtro_service.py      # 23  filtros avançados
│   ├── test_utils.py                    # 19  tempo, progresso, helpers
│   ├── test_job_progresso.py            #  4
│   ├── test_log_sistema.py              #  4
│   └── test_servicos_assincronos.py     #  3
│
├── integration/                         # rota via test_client
│   ├── test_cobertura_de_rotas.py       #  6  varredura das 43 rotas
│   ├── test_rotas_assincronas.py        #  4
│   └── test_scan_engines.py             #  3
│
├── seguranca/
│   ├── test_cabecalhos_e_csrf.py        # 33  CSP, cabeçalhos, CSRF, segredos
│   └── test_path_traversal.py           # 10  4 rotas × 10 vetores
│
├── robustez/
│   ├── test_entradas_malformadas.py     # 52  tipo errado, borda, método
│   └── test_concorrencia.py             #  7  scans e jobs simultâneos
│
├── contrato/
│   └── test_contrato_front_end.py       # 11  CSP × templates, CSS × JS, WCAG
│
├── regressao/
│   └── test_achados_auditoria.py        # 21  registro executável de defeitos
│
├── test_web_rotas.py                    # 14
├── test_log_paths.py                    #  6  (reescrito — não tinha assert)
├── test_seguranca_completo.py           #  2
└── test_exemplo_scan.py                 #  3
```

---

## ⚙️ Como executar

```bash
cd flask-python
python -m pytest tests/ -q                 # tudo (~13 s)
python -m pytest tests/ -m "not lento" -q  # ciclo rápido (~8 s)
python -m pytest tests/ -m seguranca -q    # só segurança
python -m pytest tests/ -m regressao -q    # só o registro de defeitos
python -m pytest tests/ --cov=app/web --cov=app/utils --cov-report=term-missing
```

### Marcadores

`unidade` (55) · `integracao` (101) · `seguranca` (45) · `robustez` (59) ·
`contrato` (11) · `regressao` (21) · `lento` (9)

`--strict-markers` está ligado no `pytest.ini`: marcador com erro de digitação
vira erro, e não silêncio. Sem isso, `@pytest.mark.segurnaca` sairia da
categoria sem ninguém perceber.

---

## 📌 Registro executável de defeitos

`tests/regressao/test_achados_auditoria.py` guarda os achados de auditoria como
teste, não como documento.

**Os defeitos ainda não corrigidos afirmam o comportamento CORRETO e estão
marcados `xfail(strict=True)`.** Consequência, e é o ponto todo:

- enquanto o defeito existe → o teste falha → `xfail` → a suíte fica verde;
- assim que alguém corrigir → o teste passa → `XPASS` → e o `strict`
  **reprova a suíte**, obrigando a remover o marcador.

O registro não apodrece: ele avisa sozinho quando deixa de ser verdade. Isso já
aconteceu uma vez durante a construção desta suíte — `test_nenhum_teste_da_suite_fica_sem_assert`
nasceu `xfail`, o defeito foi corrigido, ele passou a `XPASS` e o `strict`
obrigou a promovê-lo a guarda permanente.

Todo achado registrado foi **reproduzido de forma independente** antes de entrar;
nenhum entrou por confiança no relatório da auditoria.

### Nota de método: uma refutação minha que estava errada

O achado "relatório ilegível derruba `/scan/logs`" foi **refutado por engano** na
primeira medição. O script ad-hoc repontava o `__file__` do `scan_service`, mas
`obter_diretorio_logs()` é definida em `app.ui.scan_projeto.listar_falhas` e
importada de lá — o script continuou lendo a pasta **real** de relatórios, cheia
de arquivos válidos, e devolveu 200.

O `200` não era prova de tratamento: era o instrumento apontado para o diretório
errado. Dentro do sandbox correto, a rota devolve 500. É o mesmo princípio do
*"`0` não é prova"*, aplicado ao 200.

---

## 🛠️ Observações

- `PytestCacheWarning` em alguns ambientes Windows: use `-p no:cacheprovider`.
- Nenhum teste depende de GPU, LM Studio, rede ou serviço externo.
- Os módulos com 0% de cobertura são todos **menus de CLI** (`menu.py`,
  `menu_scan_projeto.py`, `menu_listar.py`, …). Este módulo não tem entrypoint
  de terminal — o CLI é o `api_python` —, então são código inalcançável aqui.
  0% ali é o número correto, não uma lacuna.
