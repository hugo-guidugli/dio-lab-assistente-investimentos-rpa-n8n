import sys
import requests
import urllib3
from bs4 import BeautifulSoup

# Configura UTF-8 no terminal Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL_PAGINA = "https://digitalinnovationone.github.io/dio-lab-assistente-investimentos-rpa-n8n/"

# 1) Baixar a página
print("1) Baixando página de clientes...")
try:
    html = requests.get(URL_PAGINA, verify=False, timeout=10).text
except Exception:
    with open("../docs/index.html", "r", encoding="utf-8") as f:
        html = f.read()

# 2) Ler a tabela de clientes
print("2) Extraindo dados dos clientes...")
soup = BeautifulSoup(html, "html.parser")
linhas = soup.select("#clientes tbody tr")

clientes = []

for linha in linhas:
    colunas = linha.find_all("td")

    cliente = {
        "nome":  colunas[0].get_text(strip=True),
        "email": colunas[1].get_text(strip=True),
        "saldo": colunas[2].get_text(strip=True),
        "perfil": colunas[3].get_text(strip=True),
    }

    clientes.append(cliente)

print(f"Total de {len(clientes)} clientes encontrados:")
for cliente in clientes:
    print(" -", cliente)

# 3) Enviar para o n8n via POST
N8N_WEBHOOK = "http://localhost:5678/webhook-test/Clientes"
print(f"\n3) Enviando dados para o Webhook do n8n em: {N8N_WEBHOOK}")

try:
    resposta = requests.post(N8N_WEBHOOK, json={"clientes": clientes}, timeout=10)
    print("\n[OK] Sucesso! Resposta recebida do n8n:")
    print("Status HTTP:", resposta.status_code)
    print("Conteudo retornado:", resposta.text)
except requests.exceptions.ConnectionError:
    print("\n[ERRO] Erro de conexao: O n8n esta aberto, mas verifique se clicou em 'Listen for test event'.")
except Exception as e:
    print("\n[ERRO] Ocorreu um erro ao enviar:", e)
