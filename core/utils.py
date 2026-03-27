import unicodedata
import json
import requests
from .state import contadores, acoes_lista, campos_acao 
from core import state

def contador_atual():
    if state.contador_sessao_atual == 0:
        print("Contador iniciado")
        state.contador_sessao_atual += 1
    else:
        print("contador somado")
        state.contador_sessao_atual += 1

def remover_acentos(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def obter_url_ngrok():
    """Tenta conectar na API local do Ngrok para pegar a URL pública."""
    try:
        # O Ngrok sempre expõe essa API na porta 4040 localmente
        resposta = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2)
        if resposta.status_code == 200:
            dados = resposta.json()
            # Procura o túnel HTTPS
            for tunnel in dados.get("tunnels", []):
                if tunnel.get("public_url", "").startswith("https"):
                    state.ngrok_url = tunnel["public_url"]
                    print(f"🔗 Túnel Ngrok detectado: {state.ngrok_url}")
                    return
                    
        state.ngrok_url = "Nenhum túnel HTTPS encontrado no Ngrok."
    except Exception:
        # Se der erro (ex: Ngrok não está aberto), não trava o servidor
        state.ngrok_url = "Inicie o Ngrok para gerar a URL pública."
        print("⚠️ Ngrok não detectado rodando na porta 4040.")

#captaliza a letra inicial do texto enviado
def capitalizarAcao(texto: str) -> str:
    if isinstance(texto, str) and texto.strip():
        texto = texto.lower()
        texto = texto.replace("_", " ")
        palavras = texto.split()
        capitalizadas = [palavra[0].upper() + palavra[1:] for palavra in palavras]
        return " ".join(capitalizadas)
    return "Texto inválido"

def carregarContadores():
    global contadores
    try:
        if state.ARQUIVOCONTADORES.exists():
            with state.ARQUIVOCONTADORES.open(encoding="utf-8") as f:
                data = json.load(f)
                contadores.update(data.get("contadores",{}))
    except:
        with state.ARQUIVOCONTADORES.open("w",encoding="utf-8") as f:
            json.dump({"contadores":contadores},f,ensure_ascii=False, indent=2)

#Atualiza o arquivo de contadores com os contadores atuais
def salvarContadores():
    with state.ARQUIVOCONTADORES.open("w",encoding="utf-8") as f:
        json.dump({"contadores":contadores},f,ensure_ascii=False, indent=2)

#Busca e extrai a ação enviada no payload
def extrairAcao(body: dict) -> str:
    for campo in campos_acao:
        valor = body.get(campo)
        if isinstance(valor, str) and valor.strip():
            return valor.lower()
    return ""   # ou "não encontrado", ou string vazia

#Compara o texto recebido com a lista de possiveis ações
def detectarAcao(acaoRecebida: str)-> str:
    if acaoRecebida is None or not acaoRecebida.strip():
        return "nao_mapeado"
    acao_normalizada = remover_acentos(acaoRecebida.lower())
    for item in acoes_lista:
        if item["match"] in acao_normalizada:
            return item["contador"]
    return "nao_mapeado"