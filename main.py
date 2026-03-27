from fastapi import FastAPI
from contextlib import asynccontextmanager

from api.webhook import router as webhook_router
from api.dashboard import router as dashboard_router
from api.contadores import router as contadores_router

from core.utils import carregarContadores, salvarContadores, contador_atual, obter_url_ngrok

# O Gerenciador de Ciclo de Vida do Servidor
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- O QUE RODA AO LIGAR O SERVIDOR ---
    print("🚀 Iniciando o Motor de Webhooks...")
    carregarContadores()
    print("✅ Contadores Carregados")
    contador_atual()
    
    # Tenta pescar a URL do Ngrok se ele já estiver aberto
    obter_url_ngrok()
    
    yield # O servidor fica online e rodando neste ponto!
    
    # --- O QUE RODA AO DESLIGAR O SERVIDOR (Ctrl+C) ---
    print("\n🛑 Desligando servidor e salvando estado...")
    salvarContadores()
    print("💾 Contadores salvos com sucesso!")

# Inicializa o FastAPI com o Lifespan
app = FastAPI(
    title="Motor de Webhooks",
    description="Receptor central focado em performance e tempo real",
    version="1.0.0",
    lifespan=lifespan
)

# Registra as rotas
app.include_router(dashboard_router)
app.include_router(webhook_router)
app.include_router(contadores_router)