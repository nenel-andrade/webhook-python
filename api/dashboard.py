import asyncio
import json
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from core import state # Importando o módulo inteiro
from datetime import datetime

router = APIRouter(
    tags=["Dashboard"],
    responses={404: {"description": "Não encontrado"}}
)

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Garantimos que a variável ngrok_url exista no state, mesmo se falhar
    url_publica = getattr(state, 'ngrok_url', 'Ngrok não detectado ou inativo')
    
    return state.templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request, 
            "titulo": "Centro de Comando - Webhooks",
            "timestamp_atual": timestamp,
            "ngrok_url": url_publica
        }
    )

# A ROTA MÁGICA DO TEMPO REAL (SSE)
@router.get("/stream")
async def sse_stream(request: Request):
    """Mantém uma conexão aberta com o navegador enviando os novos webhooks"""
    
    # Cria uma fila exclusiva para a aba do navegador que acabou de abrir
    fila = asyncio.Queue()
    state.client_queues.append(fila)

    async def event_generator():
        try:
            while True:
                # Se o usuário fechar a aba, saímos do loop
                if await request.is_disconnected():
                    break
                
                # O código fica "pausado" aqui esperando o webhook.py dar o 'put' na fila
                payload_novo = await fila.get()
                
                # O padrão SSE exige que a mensagem comece com "data: " e termine com "\n\n"
                yield f"data: {json.dumps(payload_novo)}\n\n"
                
        except asyncio.CancelledError:
            pass
        finally:
            # Limpeza: remove a fila da memória quando a aba é fechada
            if fila in state.client_queues:
                state.client_queues.remove(fila)

    return StreamingResponse(event_generator(), media_type="text/event-stream")