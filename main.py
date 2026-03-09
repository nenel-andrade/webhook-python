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
    # isso já é um dict Python arbitrário
    # Agora body é exatamente o que veio no JSON, sem validação rígida
    
    # Sua lógica aqui:
    # timestamp = ...
    # texto_da_acao = extrair_acao_body(body)
    # acao_encontrada = detectar_acao(texto_da_acao)
    # etc...

    return f"Retorno recebido com sucesso"