from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from ..core.utils import extrairAcao, detectarAcao, salvarContadores
from ..core.state import contadores, contador_sessao_atual, ultimo_webhook, client_queues

@app.post("/webhook", response_class=PlainTextResponse)
async def webhook(request: Request):
    global ARQUIVOCONTADORES
    global client_queues
    global horario_recebido
    global contador_sessao_atual
    global ultimo_webhook
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    try:
        horario_recebido = timestamp
        print(f"horario do recebimento {horario_recebido}")
        body = await request.json()
        textoAcao = extrairAcao(body)
        acaoEncontrada = detectarAcao(textoAcao)
        contadores[acaoEncontrada] += 1
        contadores["contadorGeral"] += 1
        contador_sessao_atual += 1
        salvarContadores()
        ultimo_webhook = {
            "timestamp": timestamp,
            "acao": capitalizarAcao(acaoEncontrada),
            "payload": body
        }
        for q in client_queues:
            await q.put(ultimo_webhook["payload"])
        print(f"Webhook recebido às: {timestamp}")
        print(body)
        print(f"Texto extraído: '{textoAcao}'")
        print(f"Ação detectada (raw): '{acaoEncontrada}'")
        print(f"Contadores após incremento: {contadores}")
        print(f"Contador sessão atual: {contador_sessao_atual}")
        return f"Retorno recebido com sucesso às: {timestamp}"
    except json.JSONDecodeError:
        return PlainTextResponse("Payload inválido", status_code=400)