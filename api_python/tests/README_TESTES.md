# 🧪 02 - Testes de Seguranca — API Python

Para garantir que o motor de busca de vulnerabilidades do projeto **ASPM IA** está funcionando corretamente, implementamos uma suíte de testes de integração completa.

## 📂 Novo Arquivo de Teste
O arquivo `tests/test_seguranca_completo.py` foi criado para validar as assinaturas de segurança.

## 🔍 O que está sendo testado?
A suíte de testes cria um ambiente controlado com arquivos vulneráveis e verifica se o sistema detecta:

| Categoria | Exemplo Detectado | Severidade |
| :--- | :--- | :---: |
| **SQL Injection** | Interpolação de f-strings em queries SQL | CRÍTICO |
| **RCE** | Uso de `os.system` e `subprocess.run(shell=True)` | CRÍTICO |
| **Deserialização** | Uso de `pickle.loads` | CRÍTICO |
| **Credenciais** | Senhas e chaves de API fixas no código | ALTO |
| **XSS** | Manipulação de `innerHTML` sem sanitização | ALTO |
| **Path Traversal** | Acesso a arquivos via `open(request...)` | ALTO |
| **SSRF** | Requisições externas via `requests.get` | ALTO |
| **JWT Inseguro** | Desativação de verificação de assinatura em tokens | ALTO |

## 🚀 Como Executar os Testes

Para rodar os testes localmente, utilize o `pytest` a partir da raiz do diretório `api_python`:

```bash
# Instale as dependências caso ainda não tenha feito
pip install -r requirements.txt
pip install pytest

# Execute os testes de segurança
python -m pytest tests/test_seguranca_completo.py -v
```

## ✅ Resultados Obtidos
Os testes validam não apenas a detecção, mas também se o relatório gerado (`JSON`) está devidamente ordenado por severidade, garantindo que os riscos mais críticos (CRÍTICO e ALTO) apareçam no topo para o analista de segurança.
