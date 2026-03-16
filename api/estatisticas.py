from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from ..core.utils import remover_acentos
from ..core.state import contadores, contador_sessao_atual, ultimo_webhook, client_queues

@app.get("/estatisticas", response_class=HTMLResponse)
async def stats(request: Request):
    timestamp_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return templates.TemplateResponse(
        "estatisticas.html",
        {
            "request": request,
            "contadores": contadores,
            "contador_sessao_atual": contador_sessao_atual,
            "timestamp_atual": timestamp_atual
        }
    )
