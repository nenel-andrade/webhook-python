from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from core.state import client_queues, templates, contadores
from core import state 
from datetime import datetime

router = APIRouter(
    prefix="/contadores",
    tags=["contadores"],
    responses={404: {"description": "Não encontrado"}}
)

@router.get("/", response_class=HTMLResponse)
async def stats(request: Request):
    print("Sessão atual:", state.contador_sessao_atual) 
    timestamp_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return templates.TemplateResponse(
        request=request,
        name="contadoresPage.html",
        context={
            "contadores": contadores,
            "contador_sessao_atual": state.contador_sessao_atual,
            "timestamp_atual": timestamp_atual
        }
    )