import unicodedata
import json
from fastapi import FastAPI, Request
from fastapi import Request
from fastapi.responses import PlainTextResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from datetime import datetime


 
""" 
Abrir o webhook
uvicorn main:app --reload
Abrir pra rede 
ngrok http 8000
"""

# inicia o FastAPI
app = FastAPI(
    title="Webhook Contador",
    description="Contador de ações de webhook",
    version="0.1.0"
)

templates = Jinja2Templates(directory="templates")

ARQUIVOCONTADORES = Path("contadores.json")


ultimo_webhook = None
horario_recebido = None

campos_acao = ["action_name","acao_final"]
contador_sessao_atual = 0
contadores ={
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

#Carrega o arquivo com os contadores, caso não exista cria uma
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

#Atualiza o arquivo de contadores com os contadores atuais
def salvarContadores():
    with ARQUIVOCONTADORES.open("w",encoding="utf-8") as f:
        json.dump({"contadores":contadores},f,ensure_ascii=False, indent=2)

#Busca e extrai a ação enviada no payload
def extrairAcao(body: dict) -> str:
    for campo in campos_acao:
        valor = body.get(campo)
        if isinstance(valor, str) and valor.strip():
            valor = valor.lower()
            return valor
        return None

#Compara o texto recebido com a lista de possiveis ações
def detectarAcao(acaoRecebida: str)-> str:
    if acaoRecebida is None or not acaoRecebida.strip():
        return "nao_mapeado"
    acao_normalizada = remover_acentos(acaoRecebida.lower())
    for item in acoes_lista:
        if item["match"] in acao_normalizada:
            return item["contador"]
    return "nao_mapeado"


#------------------- Funçoes auxiliares -------------------
#Remove acentos do texto enviado
def remover_acentos(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

#captaliza a letra inicial do texto enviado
def capitalizarAcao(texto: str) -> str:
    if isinstance(texto, str) and texto.strip():
        texto = texto.lower()
        texto = texto.replace("_", " ")
        palavras = texto.split()
        capitalizadas = [palavra[0].upper() + palavra[1:] for palavra in palavras]
        return " ".join(capitalizadas)
    return "Texto inválido"



carregarContadores()

@app.post("/webhook", response_class=PlainTextResponse)
async def webhook(request: Request):
    global ARQUIVOCONTADORES
    global horario_recebido
    global contador_sessao_atual
    global ultimo_webhook
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    try:
        horario_recebido = timestamp
        print(f"horario do recebimento {horario_recebido}")
        body = await request.json()
        textoAcao = extrairAcao(body)
        acaoEncontrada = detectarAcao(textoAcao)
        contadores[acaoEncontrada] += 1
        contadores["contadorGeral"] += 1
        contador_sessao_atual += 1
        salvarContadores()
        ultimo_webhook = {
            "timestamp": timestamp,
            "acao": capitalizarAcao(acaoEncontrada),
            "payload": body
        }
        print(f"Webhook recebido às: {timestamp}")
        print(body)
        print(f"Texto extraído: '{textoAcao}'")
        print(f"Ação detectada (raw): '{acaoEncontrada}'")
        print(f"Contadores após incremento: {contadores}")
        print(f"Contador sessão atual: {contador_sessao_atual}")
        return f"Retorno recebido com sucesso às: {timestamp}"
    except json.JSONDecodeError:
        return PlainTextResponse("Payload inválido", status_code=400)
    
@app.get("/stats", response_class=HTMLResponse)
async def stats(request: Request):
    timestamp_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "contadores": contadores,
            "contador_sessao_atual": contador_sessao_atual,
            "timestamp_atual": timestamp_atual
        }
    )

@app.get("/ultimo",response_class=HTMLResponse)
async def ultimo(request: Request):
    timestamp_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(horario_recebido)
    if horario_recebido == None or ultimo_webhook == None:
        return templates.TemplateResponse(
        "ultimo.html",
        {
            "request": request,
            "timestamp_atual": timestamp_atual
        }
    )
    else:
        return templates.TemplateResponse(
            "ultimo.html",
            {
                "request": request,
                "horario_recebimento": horario_recebido,
                "ultimo": ultimo_webhook["payload"],
                "ultima_acao":ultimo_webhook["acao"],
                "timestamp_atual": timestamp_atual
            }
        )