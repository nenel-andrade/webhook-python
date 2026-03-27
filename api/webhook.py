from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, HTMLResponse
from core.utils import extrairAcao, detectarAcao, capitalizarAcao
from core.state import contadores, client_queues, templates
from core.state import contador_sessao_atual as contador_somar
from datetime import datetime
from fastapi.templating import Jinja2Templates
import json

router = APIRouter(
    prefix="/webhook",
    tags=["Enpoint webhook"],
    responses={404: {"description": "Não encontrado"}}
)
ultimo_webhook = None
horario_recebido = None
@router.post("/", response_class=PlainTextResponse)
async def webhook(request: Request):
    global client_queues
    global horario_recebido
    global contador_somar
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
        print(contador_somar)
        contador_somar += 1
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
        #print(f"Contador sessão atual: {contador_sessao_atual}")
        
        return f"Retorno recebido com sucesso às: {timestamp}"
        
    except json.JSONDecodeError:
        return PlainTextResponse("Payload inválido", status_code=400)
    
@router.get("/ultimo",response_class=HTMLResponse)
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