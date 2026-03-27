from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from core.state import client_queues, templates, contadores
from core import state # <-- Importamos o módulo inteiro aqui também!
from datetime import datetime

router = APIRouter(
    prefix="/contadores",
    tags=["contadores"],
    responses={404: {"description": "Não encontrado"}}
)

@router.get("/", response_class=HTMLResponse)
async def stats(request: Request):
    # Lemos direto do state para pegar o valor exato daquele milissegundo
    print("Sessão atual:", state.contador_sessao_atual) 
    
    timestamp_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    return templates.TemplateResponse(
        "contadoresPage.html",
        {
            "request": request,
            "contadores": contadores, # Dicionários atualizam sozinhos, não tem problema!
            "contador_sessao_atual": state.contador_sessao_atual, # Passamos o valor fresco pro Jinja
            "timestamp_atual": timestamp_atual
        }
    )