from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, HTMLResponse
from core.utils import contador_sessao_atual
from core.state import  client_queues, templates, contadores, contador_sessao_atual
from api.webhook import contador_somar
from datetime import datetime


router = APIRouter(
    prefix="/contadores",
    tags=["contadores"],
    responses={404: {"description": "Não encontrado"}}
)


@router.get("/", response_class=HTMLResponse)
async def stats(request: Request):
    print("cessao", contador_somar)
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