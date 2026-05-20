from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core import state
from core.database import get_db, WebhookModel
from core.utils import extrairAcao, detectarAcao, capitalizarAcao, registrar_log
from core.state import contadores, client_queues, templates 
from core.config import TOKEN_SECRETO
from datetime import datetime
import json

security = HTTPBearer()

def extrair_headers(request: Request) -> str:
    headers_filtrados = dict(request.headers)
    if "authorization" in headers_filtrados:
        headers_filtrados["authorization"] = "Bearer **********"
    return json.dumps(headers_filtrados, ensure_ascii=False)

def extrair_ip(request: Request) -> str:
    return request.headers.get("x-forwarded-for", request.client.host)

async def verificar_token(request: Request):
    """Inspeção profunda de segurança antes de liberar o acesso"""
    registrar_log("Webhook recebido na rota segura","SEGURANCA")
    registrar_log("Inspeção de segurança iniciada...", "INFO")
    print("\n" + "🕵️‍♂️ " + "="*48)
    print("INSPEÇÃO DE SEGURANÇA - HEADERS RECEBIDOS")
    print("="*52)

    for chave, valor in request.headers.items():
        print(f"{chave}: {valor}")
    print("="*52 + "\n")

    auth_header = request.headers.get("authorization")
    
    if not auth_header:
        print("❌ FALHA: O sistema não enviou o header 'Authorization'.")
        registrar_log("FALHA: Header 'Authorization' ausente.", "ERRO")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header 'Authorization' ausente"
        )

    if not auth_header.startswith("Bearer "):
        print(f"❌ FALHA: O header veio errado. Esperado 'Bearer <token>', recebido: '{auth_header}'")
        registrar_log(f"Header invalido","ERRO")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato inválido. Use 'Bearer <token>'"
        )

    token = auth_header.split(" ")[1]
    if token != TOKEN_SECRETO:
        print(f"❌ FALHA: O token recebido ('{token}') é diferente do TOKEN_SECRETO.")
        registrar_log(f"Token incorreto,token recebido {token}","ERRO")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token incorreto"
        )

    print("✅ Segurança aprovada! Liberando acesso para a rota...")
    registrar_log("Segurança aprovada! Liberando acesso.", "SUCESSO")
    return token

router = APIRouter(
    prefix="/webhook",
    tags=["Enpoint webhook"],
    responses={404: {"description": "Não encontrado"}}
)
ultimo_webhook = None
horario_recebido = None
@router.post("/", response_class=PlainTextResponse)
@router.api_route("/", methods=["GET", "POST", "PUT", "PATCH"], response_class=PlainTextResponse)
async def webhook(request: Request, db: Session = Depends(get_db)):
    global client_queues
    global horario_recebido
    global ultimo_webhook
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    print("\n" + "="*50)
    print(f"🚨 REQUISIÇÃO RECEBIDA - MÉTODO: {request.method} 🚨")
    print("="*50)
    registrar_log("Requisição recebida, iniciando tratativa","INFO")

    try:
        horario_recebido = timestamp
        body = {}
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
            except json.JSONDecodeError:
                texto_bruto = await request.body()
                print(f"⚠️ Aviso: O corpo não é um JSON válido. Texto bruto: {texto_bruto}")
                registrar_log("Payload em formato invalido, não é um JSON","AVISO")
        elif request.method == "GET":
            body = dict(request.query_params)
            print(f"🔎 Parâmetros da URL (GET): {body}")
            registrar_log("Payload em formato invalido, madaram get por algum motivo","AVISO")
        textoAcao = extrairAcao(body)
        acaoEncontrada = detectarAcao(textoAcao)
        contadores[acaoEncontrada] += 1
        contadores["contadorGeral"] += 1
        state.contador_sessao_atual += 1
        ultimo_webhook = {
            "timestamp": timestamp,
            "acao": capitalizarAcao(acaoEncontrada),
            "payload": body,
            "metodo": request.method  
        }
        for q in client_queues:
            await q.put(ultimo_webhook["payload"])
        registrar_log("Webhook processado","INFO")
        print(f"Webhook processado às: {timestamp}")
        print(f"Payload final: {body}")
        print(f"Texto extraído: '{textoAcao}'")
        print(f"Ação detectada (raw): '{acaoEncontrada}'")
        print(f"Contadores após incremento: {contadores}")
        print("="*50 + "\n")
                # SALVANDO NO BANCO DE DADOS 🚀
        novo_registro = WebhookModel(
            timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            metodo=request.method,
            acao=capitalizarAcao(acaoEncontrada),
            payload=json.dumps(body, ensure_ascii=False),
            headers=extrair_headers(request),
            ip_origem=extrair_ip(request) 
        )
        db.add(novo_registro)
        db.commit()
        for q in state.client_queues:
            await q.put(body)
        print("Processado e salvo no banco!")
        registrar_log("Processamento do webhook finalizado","SUCESSO")
        return f"Retorno recebido com sucesso via {request.method} às: {timestamp}"
        
    except Exception as e:
        print(f"❌ Erro ao processar: {e}")
        registrar_log("Erro no processamento do webhook","ERROR")
        return PlainTextResponse(f"Erro no processamento do webhook", status_code=400)
        
    except Exception as f:
        db.rollback()
        raise f
    
@router.get("/ultimo", response_class=HTMLResponse)
async def ultimo(request: Request):
    timestamp_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    if horario_recebido == None or ultimo_webhook == None:
        return templates.TemplateResponse(
            request=request,
            name="ultimo.html",
            context={
                "timestamp_atual": timestamp_atual
            }
        )
    else:
        payload_pretty = json.dumps(ultimo_webhook["payload"], indent=2, ensure_ascii=False)
        return templates.TemplateResponse(
            request=request,
            name="ultimo.html",
            context={
                "horario_recebimento": horario_recebido,
                "ultimo": payload_pretty,
                "ultima_acao": ultimo_webhook["acao"],
                "timestamp_atual": timestamp_atual
            }
        )
    
@router.post("/secure/", dependencies=[Depends(verificar_token)])
async def webhook_protegido(request: Request, db: Session = Depends(get_db)):
    global client_queues
    global horario_recebido
    global ultimo_webhook
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print("\n" + "🔐 " + "="*48)
    print(f"RAIO-X SEGURO - MÉTODO: {request.method}")
    print("="*52)
    print("\n--- 📝 HEADERS ---")
    for chave, valor in request.headers.items():
        if chave.lower() == "authorization":
            print(f"{chave}: Bearer **********")
        else:
            print(f"{chave}: {valor}")

    try:
        horario_recebido = timestamp
        body = await request.json()
        print("\n--- 📦 PAYLOAD ---")
        print(json.dumps(body, indent=2, ensure_ascii=False))
        registrar_log(f"Payload Recebido \n {json.dumps(body, indent=2, ensure_ascii=False)}")
        textoAcao = extrairAcao(body)
        acaoEncontrada = detectarAcao(textoAcao)
        
        contadores[acaoEncontrada] += 1
        contadores["contadorGeral"] += 1
        state.contador_sessao_atual += 1
        
        ultimo_webhook = {
            "timestamp": timestamp,
            "acao": capitalizarAcao(acaoEncontrada),
            "payload": body,
            "metodo": "POST (SECURE)"
        }
        for q in client_queues:
            await q.put(ultimo_webhook["payload"])
            
        print("\n✅ Webhook seguro processado com sucesso.")
        print("="*52 + "\n")
        novo_registro = WebhookModel(
            timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            metodo=request.method,
            acao=capitalizarAcao(acaoEncontrada),
            payload=json.dumps(body, ensure_ascii=False),
            headers=extrair_headers(request),
            ip_origem=extrair_ip(request)       
        )
        db.add(novo_registro)
        db.commit() 
        for q in state.client_queues:
            await q.put(body)
        print("Processado e salvo no banco!")
        return f"Acesso seguro processado com sucesso às: {timestamp}"
        
    except json.JSONDecodeError:
        print("⚠️ Erro: Payload seguro não é um JSON válido.")
        return PlainTextResponse("JSON inválido", status_code=400)
    except Exception as e:
        print(f"❌ Erro interno na rota segura: {e}")
        return PlainTextResponse("Erro no processamento", status_code=500)
    except Exception as f:
        db.rollback() 
        raise f
    
@router.get("/historico", response_class=HTMLResponse)
async def ver_historico(request: Request, db: Session = Depends(get_db)):
    registros = db.query(WebhookModel).order_by(WebhookModel.id.desc()).limit(50).all()

    historico_formatado = []
    for r in registros:
        historico_formatado.append({
            "timestamp": r.timestamp,
            "metodo": r.metodo,
            "acao": r.acao,
            "payload": json.loads(r.payload) 
        })

    return templates.TemplateResponse(
        request=request,
        name="historico.html",
        context={
            "historico": historico_formatado,
            "timestamp_atual": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
    )