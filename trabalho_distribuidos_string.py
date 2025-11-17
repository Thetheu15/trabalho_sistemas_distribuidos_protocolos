import socket
import time
from datetime import datetime

server_ip = '3.88.99.255'
server_port = 8080
LOG_FILE = 'respostas_trab_distribuidos_string.txt'
TIMEOUT = 4

class ErroRede(Exception):
    pass

class ErroProtocolo(Exception):
    pass

# --------------------------
def registrar_respostas(resposta_str):
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(resposta_str + "\n")
    except Exception as e:
        print("Erro ao gravar log (string):", e)

def format_string_response(raw, elapsed=None):
    """Recebe a string no formato do servidor strings e retorna versão legível."""

    if not raw:
        return "Resposta vazia"
    raw = raw.strip()

    if raw.endswith("|FIM"):
        raw = raw[:-4]
    parts = raw.split("|")

    out = []
    if parts:
        out.append(f"Status: {parts[0]}")

    for p in parts[1:]:
        if '=' in p:
            k,v = p.split("=",1)
            out.append(f"{k}: {v}")
        else:
            out.append(p)
    if elapsed is not None:
        out.append(f"Tempo (ms): {round(elapsed*1000,2)}")
    return "\n".join(out)

def enviar_mensagem(sock, mensagem):
    try:
        sock.sendall((mensagem + "\n").encode('utf-8'))
    except Exception as e:
        raise ErroRede(f"Erro ao enviar (strings): {e}")

def receber_resposta(sock):
    try:
        sock.settimeout(TIMEOUT)
        data = sock.recv(4096).decode('utf-8')
        if not data:
            raise ErroRede("Nenhum dado recebido (strings).")
    except Exception as e:
        raise ErroRede(f"Erro ao receber (strings): {e}")
    if "|FIM" not in data:

        raise ErroProtocolo(f"Resposta strings sem terminador FIM: {data!r}")
    return data.strip()

# --------------------------
# comandos
# --------------------------
def autenticar(sock, timestamp):
    chave = '554229'
    msg = f'AUTH|aluno_id={chave}|TIMESTAMP={timestamp}|FIM'
    enviar_mensagem(sock, msg)
    t0 = time.time()
    resp = receber_resposta(sock)
    elapsed = time.time() - t0
    registrar_respostas("autenticar=" + resp)
    print("=== AUTENTICACAO (STRINGS) ===")
    print(format_string_response(resp, elapsed))
 
    parts = resp.split("|")
    if len(parts) < 2:
        raise ErroProtocolo("AUTH malformado (strings).")

    token_field = parts[1]
    if '=' in token_field:
        return token_field.split("=",1)[1]
    return token_field

def soma(sock, token, numeros):
    nums = numeros if isinstance(numeros, str) else ",".join(str(n) for n in numeros)
    msg = f'OP|{token}|operacao=soma|nums={nums}|FIM'
    enviar_mensagem(sock, msg)
    t0 = time.time()
    resp = receber_resposta(sock)
    elapsed = time.time() - t0
    registrar_respostas("soma=" + resp)
    print("=== SOMA (STRINGS) ===")
    print(format_string_response(resp, elapsed))

def echo(sock, token, conteudo):
    msg = f'OP|{token}|operacao=echo|mensagem={conteudo}|FIM'
    enviar_mensagem(sock, msg)
    t0 = time.time()
    resp = receber_resposta(sock)
    elapsed = time.time() - t0
    registrar_respostas("echo=" + resp)
    print("=== ECHO (STRINGS) ===")
    print(format_string_response(resp, elapsed))

def op_timestamp(sock, token):
    msg = f'OP|{token}|operacao=timestamp|FIM'
    enviar_mensagem(sock, msg)
    t0 = time.time()
    resp = receber_resposta(sock)
    elapsed = time.time() - t0
    registrar_respostas("timestamp=" + resp)
    print("=== TIMESTAMP (STRINGS) ===")
    print(format_string_response(resp, elapsed))

def status(sock, token):
    msg = f'OP|{token}|operacao=status|FIM'
    enviar_mensagem(sock, msg)
    t0 = time.time()
    resp = receber_resposta(sock)
    elapsed = time.time() - t0
    registrar_respostas("status=" + resp)
    print("=== STATUS (STRINGS) ===")
    print(format_string_response(resp, elapsed))

def historico(sock, token):
    msg = f'OP|{token}|operacao=historico|FIM'
    enviar_mensagem(sock, msg)
    t0 = time.time()
    resp = receber_resposta(sock)
    elapsed = time.time() - t0
    registrar_respostas("historico=" + resp)
    print("=== HISTORICO (STRINGS) ===")
    print(format_string_response(resp, elapsed))

def info(sock, token, tipo='basico'):
    msg = f'INFO|{token}|tipo={tipo}|FIM'
    enviar_mensagem(sock, msg)
    t0 = time.time()
    resp = receber_resposta(sock)
    elapsed = time.time() - t0
    registrar_respostas("info=" + resp)
    print("=== INFO (STRINGS) ===")
    print(format_string_response(resp, elapsed))

def logout(sock, token):
    msg = f'LOGOUT|{token}|FIM'
    enviar_mensagem(sock, msg)
    t0 = time.time()
    resp = receber_resposta(sock)
    elapsed = time.time() - t0
    registrar_respostas("logout=" + resp)
    print("=== LOGOUT (STRINGS) ===")
    print(format_string_response(resp, elapsed))

# --------------------------
# FUNCAO INTERFACE PARA O MENU
# --------------------------
def servidor_string(op_code, param=None):
    """op_code: 1=estatisticas(soma),2=echo,3=timestamp,4=status,5=historico,6=info"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server_ip, server_port))
        timestamp = datetime.now().isoformat()

        token = autenticar(sock, timestamp)
        if not token:
            print("Autenticação falhou (strings).")
            return

        if op_code == 1:
            nums = param
            if isinstance(nums, str):
                nums = nums
            soma(sock, token, nums)
        elif op_code == 2:
            msg = param if param is not None else "Hello"
            echo(sock, token, msg)
        elif op_code == 3:
            op_timestamp(sock, token)
        elif op_code == 4:
            status(sock, token)
        elif op_code == 5:
            historico(sock, token)
        elif op_code == 6:
            info(sock, token, 'basico')
        else:
            print("Operação desconhecida (strings).")

        logout(sock, token)
    except (ErroRede, ErroProtocolo) as e:
        print("Erro crítico (strings):", e)
    except Exception as e:
        print("Erro desconhecido (strings):", e)
    finally:
        try:
            sock.close()
        except:
            pass

