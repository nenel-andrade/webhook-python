from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, HTMLResponse
from core.utils import extrairAcao, detectarAcao, salvarContadores, capitalizarAcao
from core.state import templates
from datetime import datetime


router = APIRouter(
    tags=["Dashboard"],
    responses={404: {"description": "Não encontrado"}}
)

@router.get("/",response_class=HTMLResponse)
async def home(request: Request):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return templates.TemplateResponse(
        "dashboard.html",
        {
        "request": request, 
        "titulo": "Bem-vindo ao Meu Backlog",
        "timestamp_atual":timestamp
        }
    )