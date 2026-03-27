from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from ..core.utils import extrairAcao, detectarAcao, salvarContadores
from ..core.state import contadores, client_queues