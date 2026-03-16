from pathlib import Path
from datetime import datetime
from asyncio import Queue
from typing import Dict, Any, List

ARQUIVOCONTADORES = Path("contadores.json")

ultimo_webhook = None
horario_recebido = None

client_queues = []
campos_acao = ["action_name","acao_final"]
contador_sessao_atual = 0
contadores ={
    "contadorGeral" : 0,
    "aprovado" : 0,
    "reprovado" : 0,
    "derivacao" : 0,
    "pendencia" : 0,
    "nao_mapeado" : 0
}

acoes_lista = [
    {"match":"aprov", "contador":"aprovado"},
    {"match":"recus", "contador":"reprovado"},
    {"match":"reprov", "contador":"reprovado"},
    {"match":"rejei", "contador":"reprovado"},
    {"match":"deriv", "contador":"derivacao"},
    {"match":"penden", "contador":"pendencia"}
]