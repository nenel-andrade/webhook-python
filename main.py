from fastapi import FastAPI
from api.webhook import router as webhook_router
from api.dashboard import router as dashboard_router
from api.contadores import router as contadores_router
from core.utils import carregarContadores, salvarContadores,contador_atual


#from api import estatisticas

# TODO PRIORITARIO LIMPAR MAIN QUEBRANDO EM MAIS ARQUIVOS

""" 
Abrir o webhook
uvicorn main:app --reload
Abrir pra rede 
ngrok http 8000
"""

# inicia o FastAPI
app = FastAPI(
    title="Projeto Webhook",
    description="Projeto de recebimento de webhooks",
    version="0.1.1"
)
#app.include_router(estatisticas.estatisticas_router)
app.include_router(webhook_router)
app.include_router(dashboard_router)
app.include_router(contadores_router)
carregarContadores()
salvarContadores()
print("Contadores Carregados")
contador_atual()

# TODO encontar uma maneira de deixar o url do ngrok visivel no front, pelomenos no server local
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # ou especifique seu ngrok URL
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
