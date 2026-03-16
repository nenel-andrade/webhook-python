from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from ..core.utils import extrairAcao, detectarAcao, salvarContadores
from ..core.state import contadores, contador_sessao_atual, ultimo_webhook, client_queues