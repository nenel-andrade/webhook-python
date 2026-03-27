from fastapi import APIRouter, Request, FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime
from fastapi.responses import PlainTextResponse
from pathlib import Path
from fastapi.templating import Jinja2Templates
from core.utils import remover_acentos
from core.state import contadores, client_queues
from api.webhook import contador_sessao_atual

app = FastAPI(
    title="Webhook Contador",
    description="Contador de ações de webhook",
    version="0.2.0"
)

router = APIRouter(
    prefix="/estatisticas",           # prefixo opcional para todas as rotas desse router
    tags=["estatisticas"],            # aparece bonitinho no Swagger
    responses={404: {"description": "Não encontrado"}}
)

templates = Jinja2Templates(directory="templates")
@router.get("/estatisticas", response_class=HTMLResponse)
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
