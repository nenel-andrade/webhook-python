import unicodedata
import json
from .state import contadores, acoes_lista, campos_acao ,contador_sessao_atual # import relativo
from core.state import ARQUIVOCONTADORES

def remover_acentos(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def contador_atual():
    global contador_sessao_atual 
    if contador_sessao_atual == 0:
        print("Contador iniciado")
    else:
        print("contador somado")
        contador_sessao_atual += 1

#captaliza a letra inicial do texto enviado
def capitalizarAcao(texto: str) -> str:
    if isinstance(texto, str) and texto.strip():
        texto = texto.lower()
        texto = texto.replace("_", " ")
        palavras = texto.split()
        capitalizadas = [palavra[0].upper() + palavra[1:] for palavra in palavras]
        return " ".join(capitalizadas)
    return "Texto inválido"

def carregarContadores():
    global contadores
    try:
        if ARQUIVOCONTADORES.exists():
            with ARQUIVOCONTADORES.open(encoding="utf-8") as f:
                data = json.load(f)
                contadores.update(data.get("contadores",{}))
    except:
        with ARQUIVOCONTADORES.open("w",encoding="utf-8") as f:
            json.dump({"contadores":contadores},f,ensure_ascii=False, indent=2)

#Atualiza o arquivo de contadores com os contadores atuais
def salvarContadores():
    with ARQUIVOCONTADORES.open("w",encoding="utf-8") as f:
        json.dump({"contadores":contadores},f,ensure_ascii=False, indent=2)

#Busca e extrai a ação enviada no payload
def extrairAcao(body: dict) -> str:
    for campo in campos_acao:
        valor = body.get(campo)
        if isinstance(valor, str) and valor.strip():
            return valor.lower()
    return ""   # ou "não encontrado", ou string vazia

#Compara o texto recebido com a lista de possiveis ações
def detectarAcao(acaoRecebida: str)-> str:
    if acaoRecebida is None or not acaoRecebida.strip():
        return "nao_mapeado"
    acao_normalizada = remover_acentos(acaoRecebida.lower())
    for item in acoes_lista:
        if item["match"] in acao_normalizada:
            return item["contador"]
    return "nao_mapeado"