from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from datetime import datetime
from fastapi.templating import Jinja2Templates
from core.utils import remover_acentos
from core.state import contadores, client_queues
from core import state

router = APIRouter(
    prefix="/estatisticas",
    tags=["estatisticas"],
    responses={404: {"description": "Não encontrado"}}
)

templates = Jinja2Templates(directory="templates")

ACOES = ["aprovado", "reprovado", "derivacao", "pendencia", "nao_mapeado"]

@router.get("/", response_class=HTMLResponse)
async def stats(request: Request):
    total = contadores["contadorGeral"]
    percentuais = {
        acao: round(contadores[acao] / total * 100, 1) if total > 0 else 0
        for acao in ACOES
    }
    return templates.TemplateResponse(
        request=request,
        name="estatisticas.html",
        context={
            "contadores": contadores,
            "percentuais": percentuais,
            "timestamp_atual": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
    )
