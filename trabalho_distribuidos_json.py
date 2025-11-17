import socket
import json
import time
from datetime import datetime

server_ip = '3.88.99.255'
server_port = 8081
LOG_FILE = 'respostas_trab_distribuidos_json.txt'
TIMEOUT = 4

# ================================
# EXCEÇÕES PERSONALIZADAS
# ================================
class ErroRede(Exception):
    pass

class ErroProtocolo(Exception):
    pass

# --------------------------
# UTILITÁRIOS
# --------------------------
def registrar_respostas(resposta_str):
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as documento:
            documento.write(resposta_str + "\n")
    except Exception as e:
        print(f"Falha ao registrar no arquivo: {e}")

def format_json_response(resposta, elapsed=None):
    """Recebe o dict de resposta e retorna string formatada legível (com tempo se fornecido)."""
    lines = []
    if isinstance(resposta, dict):
    
        if 'status' in resposta:
            lines.append(f"Status: {resposta.get('status')}")
        if 'mensagem' in resposta:
            lines.append(f"Mensagem: {resposta.get('mensagem')}")
        if 'token' in resposta:
            lines.append(f"Token: {resposta.get('token')}")

        if 'resultado' in resposta and isinstance(resposta['resultado'], dict):
            lines.append("Resultado:")
            for k, v in resposta['resultado'].items():
                lines.append(f"  {k}: {v}")
   
        for key in resposta:
            if key in ('status','mensagem','token','resultado','sucesso','timestamp'):
                continue
  
            lines.append(f"{key}: {resposta[key]}")
        if 'timestamp' in resposta:
            lines.append(f"Timestamp: {resposta['timestamp']}")
        if elapsed is not None:
            lines.append(f"Tempo (ms): {round(elapsed*1000,2)}")
    else:
        lines.append(str(resposta))
        if elapsed is not None:
            lines.append(f"Tempo (ms): {round(elapsed*1000,2)}")
    return "\n".join(lines)

# --------------------------
# COMUNICAÇÃO (enviar/receber)
# --------------------------
def enviar_mensagem(sock, mensagem_obj):
    try:
        texto = json.dumps(mensagem_obj) + '\n'
        sock.sendall(texto.encode('utf-8'))
    except Exception as e:
        raise ErroRede(f"Erro ao enviar (json): {e}")

def receber_resposta(sock):
    try:
        sock.settimeout(TIMEOUT)
        data = sock.recv(4096).decode('utf-8')
        if not data:
            raise ErroRede("Nenhum dado recebido (socket fechado).")
    except socket.timeout:
        raise ErroRede("Timeout ao receber resposta do servidor.")
    except Exception as e:
        raise ErroRede(f"Erro ao receber dados: {e}")

    try:
        resposta = json.loads(data)
    except Exception:
        raise ErroProtocolo(f"JSON inválido recebido: {data!r}")

    if not isinstance(resposta, dict):
        raise ErroProtocolo("Resposta JSON malformada (esperado objeto).")

    return resposta

# --------------------------
# OPERACOES (mantendo estrutura original)
# --------------------------
def autenticar(sock, timestamp):
    msg = {'tipo':'autenticar','aluno_id':'554229','timestamp': timestamp}
    enviar_mensagem(sock, msg)
    t0 = time.time()
    resp = receber_resposta(sock)
    elapsed = time.time() - t0
    formatted = format_json_response(resp, elapsed)
    registrar_respostas("autenticacao=" + json.dumps(resp))
    print("=== AUTENTICACAO ===")
    print(formatted)
    return resp.get('token')

def soma(sock, token, timestamp, numeros):
    msg = {'tipo':'operacao','token':token,'operacao':'soma','parametros':{'numeros': numeros},'timestamp': timestamp}
    enviar_mensagem(sock, msg)
    t0 = time.time()
    resp = receber_resposta(sock)
    elapsed = time.time() - t0
    registrar_respostas("soma=" + json.dumps(resp))
    print("=== SOMA ===")
    print(format_json_response(resp, elapsed))

def echo(sock, token, timestamp, texto):
    msg = {'tipo':'operacao','token':token,'operacao':'echo','parametros':{'mensagem': texto},'timestamp': timestamp}
    enviar_mensagem(sock, msg)
    t0 = time.time()
    resp = receber_resposta(sock)
    elapsed = time.time() - t0
    registrar_respostas("echo=" + json.dumps(resp))
    print("=== ECHO ===")
    print(format_json_response(resp, elapsed))

def op_timestamp(sock, token, timestamp):
    msg = {'tipo':'operacao','token':token,'operacao':'timestamp','timestamp': timestamp}
    enviar_mensagem(sock, msg)
    t0 = time.time()
    resp = receber_resposta(sock)
    elapsed = time.time() - t0
    registrar_respostas("timestamp=" + json.dumps(resp))
    print("=== TIMESTAMP ===")
    print(format_json_response(resp, elapsed))

def status(sock, token, timestamp):
    msg = {'tipo':'operacao','token':token,'operacao':'status','timestamp': timestamp}
    enviar_mensagem(sock, msg)
    t0 = time.time()
    resp = receber_resposta(sock)
    elapsed = time.time() - t0
    registrar_respostas("status=" + json.dumps(resp))
    print("=== STATUS ===")
    print(format_json_response(resp, elapsed))

def historico(sock, token, timestamp):
    msg = {'tipo':'operacao','token':token,'operacao':'historico','timestamp': timestamp}
    enviar_mensagem(sock, msg)
    t0 = time.time()
    resp = receber_resposta(sock)
    elapsed = time.time() - t0
    registrar_respostas("historico=" + json.dumps(resp))
    print("=== HISTORICO ===")
    print(format_json_response(resp, elapsed))

def info(sock, token, timestamp):
    msg = {'tipo':'info','token':token,'timestamp': timestamp}
    enviar_mensagem(sock, msg)
    t0 = time.time()
    resp = receber_resposta(sock)
    elapsed = time.time() - t0
    registrar_respostas("info=" + json.dumps(resp))
    print("=== INFO ===")
    print(format_json_response(resp, elapsed))

def logout(sock, token, timestamp):
    msg = {'tipo':'logout','token':token,'timestamp': timestamp}
    enviar_mensagem(sock, msg)
    t0 = time.time()
    resp = receber_resposta(sock)
    elapsed = time.time() - t0
    registrar_respostas("logout=" + json.dumps(resp))
    print("=== LOGOUT ===")
    print(format_json_response(resp, elapsed))

# --------------------------
# FUNCAO INTERFACE PARA O MENU
# --------------------------
def servidor_json(op_code, param=None):
    """op_code: 1=estatisticas(soma),2=echo,3=timestamp,4=status,5=historico,6=info"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server_ip, server_port))
        timestamp = datetime.now().isoformat()

        token = autenticar(sock, timestamp)
        if not token:
            print("Autenticação falhou.")
            return

        if op_code == 1:
      
            nums = param
            if isinstance(nums, str):
                nums = [float(x.strip()) for x in nums.split(",") if x.strip()]
            soma(sock, token, timestamp, nums)
        elif op_code == 2:
            msg = param if param is not None else "Hello"
            echo(sock, token, timestamp, msg)
        elif op_code == 3:
            op_timestamp(sock, token, timestamp)
        elif op_code == 4:
            status(sock, token, timestamp)
        elif op_code == 5:
            historico(sock, token, timestamp)
        elif op_code == 6:
            info(sock, token, timestamp)
        else:
            print("Operação desconhecida.")

        logout(sock, token, timestamp)
    except (ErroRede, ErroProtocolo) as e:
        print("Erro crítico:", e)
    except Exception as e:
        print("Erro desconhecido:", e)
    finally:
        try:
            sock.close()
        except:
            pass
