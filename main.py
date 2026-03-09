from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI(
    title="Webhook Contador",
    description="Contador de ações de webhook",
    version="0.1.0"
)

@app.post("/webhook", response_class=PlainTextResponse)
async def webhook(request: Request):
    body = await request.json()  
    print(body)
    return f"Retorno recebido com sucesso"