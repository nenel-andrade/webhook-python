from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import json
from pathlib import Path
from datetime import datetime


app = FastAPI(
    title="Webhook Contador",
    description="Contador de ações de webhook",
    version="0.1.0"
)

ARQUIVOCONTADORES = Path("contadores.json")


ultimoWebhook = None
campos_acao = ["action_name","acao_final"]

contadores ={
    "contadorSessaoAtual": 0,
    "contadorGeral" : 0,
    "aprovado" : 0,
    "reprovado" : 0,
    "derivacao" : 0,
    "pendencia" : 0,
    "nao_mapeado" : 0
}

acoes_lista = [
    {"match":"aprov", "contador":"aprovado"},
    {"match":"recus", "contador":"reprovado"},
    {"match":"reprov", "contador":"reprovado"},
    {"match":"rejei", "contador":"reprovado"},
    {"match":"deriv", "contador":"derivacao"},
    {"match":"penden", "contador":"pendencia"}
]




def carregarContadores():
    global contadores
    try:
        if ARQUIVOCONTADORES.exists():
            with ARQUIVOCONTADORES.open(encoding="utf-8") as f:
                data = json.load(f)
                contadores.update(data.get("contadores",{}))
    except:
        with ARQUIVOCONTADORES.open("w",encoding="utf-8") as f:
            json.dump({"contadores":contadores},f,ensure_ascii=False, indent=2)


def salvarContadores():
    with ARQUIVOCONTADORES.open("w",encoding="utf-8") as f:
        json.dump({"contadores":contadores},f,ensure_ascii=False, indent=2)
        
def extrairAcao(body: dict) -> str:
    for campo in campos_acao:
        valor = body.get(campo)
        if isinstance(valor, str) and valor.strip():
            valor = valor.lower()
            return valor
        return ""

def capitalizarAcao(texto: str) -> str:
    if isinstance(texto, str) and texto.strip():
        texto = texto.lower()
        texto = texto.replace("_", " ")
        palavras = texto.split()
        capitalizadas = [palavra[0].upper() + palavra[1:] for palavra in palavras]
        return " ".join(capitalizadas)
    return "Texto inválido"

def detectarAcao(acaoRecebida: str)-> str:
    for item in acoes_lista:
        if item["match"] in acaoRecebida:
            return item["contador"]
    return "nao_mapeado"





carregarContadores()

@app.post("/webhook", response_class=PlainTextResponse)
async def webhook(request: Request):
    global ARQUIVOCONTADORES
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    body = await request.json()  
    textoAcao = extrairAcao(body)
    acaoEncontrada = detectarAcao(textoAcao)
    contadores[acaoEncontrada] += 1
    contadores["contadorGeral"] += 1
    contadores["contadorSessaoAtual"] += 1
    salvarContadores()
    global ultimowebhook
    ultimowebhook = {
        "timestamp": timestamp,
        "acao": capitalizarAcao(acaoEncontrada),
        "payload": body
    }
    print(f"Webhook recebido às: {timestamp}")
    print(body)
    print(f"Ação recebida: {ultimowebhook["acao"]}")
    return f"Retorno recebido com sucesso às: {timestamp}"


""" 
Abrir o webhook
uvicorn main:app --reload

Abrir pra rede 
ngrok http 8000

"""