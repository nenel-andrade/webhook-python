import unicodedata
import json
from asyncio import Queue
from collections import deque
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi import Request
from fastapi.responses import PlainTextResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from sse_starlette.sse import EventSourceResponse

from api import estatisticas_router

# TODO PRIORITARIO LIMPAR MAIN QUEBRANDO EM MAIS ARQUIVOS

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
    version="0.2.0"
)
app.include_router(estatisticas_router)

# TODO encontar uma maneira de deixar o url do ngrok visivel no front, pelomenos no server local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou especifique seu ngrok URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

ARQUIVOCONTADORES = Path("contadores.json")


ultimo_webhook = None
horario_recebido = None


client_queues = []
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


# TODO criar a função de calculo de porcentagens
def calcular_porcentagens():
    tipos_mapeados = ["aprovado", "reprovado", "derivacao", "pendencia"]
    for i in tipos_mapeados:
        if i in contadores.items():
            print(i)


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
calcular_porcentagens()

# TODO fazer o reload automatico funcionar
@app.get("/events")
async def sse_events(request: Request):
    print("Novo cliente SSE conectado")
    queue = Queue()
    client_queues.append(queue)
    print(f"Clientes conectados agora: {len(client_queues)}")

    async def event_generator():
        try:
            while True:
                message = await queue.get()
                print(f"Enviando SSE: {message}")
                yield {"event": "update", "data": message}
                queue.task_done()
        finally:
            client_queues.remove(queue)
            print("Cliente SSE desconectado")
    
    return EventSourceResponse(event_generator())


@app.post("/webhook", response_class=PlainTextResponse)
async def webhook(request: Request):
    global ARQUIVOCONTADORES
    global client_queues
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
        for q in client_queues:
            await q.put(ultimo_webhook["payload"])
        print(f"Webhook recebido às: {timestamp}")
        print(body)
        print(f"Texto extraído: '{textoAcao}'")
        print(f"Ação detectada (raw): '{acaoEncontrada}'")
        print(f"Contadores após incremento: {contadores}")
        print(f"Contador sessão atual: {contador_sessao_atual}")
        return f"Retorno recebido com sucesso às: {timestamp}"
    except json.JSONDecodeError:
        return PlainTextResponse("Payload inválido", status_code=400)
    
@app.get("/contadores", response_class=HTMLResponse)
async def stats(request: Request):
    timestamp_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return templates.TemplateResponse(
        "contadoresPage.html",
        {
            "request": request,
            "contadores": contadores,
            "contador_sessao_atual": contador_sessao_atual,
            "timestamp_atual": timestamp_atual
        }
    )
# @app.get("/estatisticas", response_class=HTMLResponse)
# async def stats(request: Request):
#     timestamp_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
#     return templates.TemplateResponse(
#         "estatisticas.html",
#         {
#             "request": request,
#             "contadores": contadores,
#             "contador_sessao_atual": contador_sessao_atual,
#             "timestamp_atual": timestamp_atual
#         }
#     )

@app.get("/ultimo",response_class=HTMLResponse)
async def ultimo(request: Request):
    
    
    timestamp_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    if horario_recebido == None or ultimo_webhook == None:
        return templates.TemplateResponse(
        "ultimo.html",
        {
            "request": request,
            "timestamp_atual": timestamp_atual
        }
    )
    else:
        payload_pretty = json.dumps(ultimo_webhook["payload"], indent=2, ensure_ascii=False)
        return templates.TemplateResponse(
            "ultimo.html",
            {
                "request": request,
                "horario_recebimento": horario_recebido,
                "ultimo": payload_pretty,
                "ultima_acao":ultimo_webhook["acao"],
                "timestamp_atual": timestamp_atual
            }
        )