from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, PlainTextResponse

app = FastAPI(
    title="Webhook Contador",
    description="Contador de ações de webhook",
    version="0.1.0"
)

