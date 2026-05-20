import asyncio
import json
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from core import state
from datetime import datetime

router = APIRouter(
    tags=["Dashboard"],
    responses={404: {"description": "Não encontrado"}}
)

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    url_publica = getattr(state, 'ngrok_url', 'Ngrok não detectado ou inativo')
    return state.templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "titulo": "Centro de Comando - Webhooks",
            "timestamp_atual": timestamp,
            "ngrok_url": url_publica
        }
    )

@router.get("/stream")
async def sse_stream(request: Request):
    fila = asyncio.Queue()
    state.client_queues.append(fila)

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    payload_novo = await asyncio.wait_for(fila.get(), timeout=1.0)
                    yield f"data: {json.dumps(payload_novo)}\n\n"
                except asyncio.TimeoutError:
                    continue
        except asyncio.CancelledError:
            pass
        finally:
            if fila in state.client_queues:
                state.client_queues.remove(fila)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/logs", response_class=HTMLResponse)
async def pagina_logs(request: Request):
    return state.templates.TemplateResponse(
        request=request,
        name="logs.html",
        context={
            "logs": state.sistema_logs,
            "timestamp_atual": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
    )