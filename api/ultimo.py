from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from ..core.utils import extrairAcao, detectarAcao, salvarContadores
from ..core.state import contadores, contador_sessao_atual, ultimo_webhook, client_queues

router = APIRouter(prefix="/ultimo", tags=["ultimo"])

@router.get("/", response_class=PlainTextResponse)

@app.get("/ultimo",response_class=HTMLResponse)
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