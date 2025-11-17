import socket
import struct
import time
from datetime import datetime
import mensagens_pb2

# ---------------------------------------
# Configurações gerais
# ---------------------------------------
SERVER_IP = "3.88.99.255"
SERVER_PORT = 8082
LOG_FILE = "respostas_trab_distribuidos_protobuf.txt"
TIMEOUT = 5


# ---------------------------------------
# Exceções
# ---------------------------------------
class ErroRede(Exception):
    pass


class ErroProtocolo(Exception):
    pass


# ---------------------------------------
# Utilidades
# ---------------------------------------
def registrar_respostas(texto):
    """Salva resposta crua no arquivo de log."""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(texto + "\n")
    except Exception as e:
        print("Erro ao registrar log (protobuf):", e)


def format_protobuf_response(resp, elapsed=None):
    """Converte mensagens_pb2.Resposta em uma string legível."""

    if resp is None:
        return "Resposta vazia"

    linhas = []

    if resp.HasField("ok"):
        ok = resp.ok
        linhas.append(f"Comando: {ok.comando}")

        if ok.dados:
            linhas.append("Dados:")

            for key in ok.dados:
                linhas.append(f"  {key}: {ok.dados[key]}")

        if ok.timestamp:
            linhas.append(f"Timestamp: {ok.timestamp}")

    elif resp.HasField("erro"):
        er = resp.erro
        linhas.append(f"ERRO - Comando: {er.comando}")
        linhas.append(f"Mensagem: {er.mensagem}")

        if er.detalhes:
            linhas.append("Detalhes:")
            for key in er.detalhes:
                linhas.append(f"  {key}: {er.detalhes[key]}")

        if er.timestamp:
            linhas.append(f"Timestamp: {er.timestamp}")

    else:
        linhas.append(str(resp))

    if elapsed is not None:
        linhas.append(f"Tempo de resposta: {round(elapsed*1000, 2)} ms")

    return "\n".join(linhas)


# ---------------------------------------
# Comunicação via Protobuf
# ---------------------------------------
def enviar(sock, msg):
    """Envia mensagem protobuf com framing de 4 bytes."""
    try:
        payload = msg.SerializeToString()
        header = struct.pack(">I", len(payload))
        sock.sendall(header + payload)
    except Exception as e:
        raise ErroRede(f"Erro ao enviar (protobuf): {e}")


def receber(sock):
    """Recebe resposta protobuf usando framing de 4 bytes."""
    try:
        sock.settimeout(TIMEOUT)

        header = sock.recv(4)
        if len(header) < 4:
            raise ErroRede("Header incompleto ao receber (protobuf).")

        tamanho = struct.unpack(">I", header)[0]
        buffer = b""

        while len(buffer) < tamanho:
            parte = sock.recv(tamanho - len(buffer))
            if not parte:
                raise ErroRede("Conexão fechada antes de completar payload.")
            buffer += parte

    except socket.timeout:
        raise ErroRede("Timeout ao receber resposta (protobuf).")
    except Exception as e:
        raise ErroRede(f"Erro ao receber (protobuf): {e}")

    resp = mensagens_pb2.Resposta()
    try:
        resp.ParseFromString(buffer)
    except Exception:
        raise ErroProtocolo("Falha ao decodificar protobuf (payload inválido).")

    return resp


# ---------------------------------------
# Comandos do Protocolo
# ---------------------------------------

def autenticar(sock, timestamp):
    req = mensagens_pb2.Requisicao()
    req.auth.aluno_id = "554229"
    req.auth.timestamp_cliente = timestamp

    enviar(sock, req)
    t0 = time.time()
    resp = receber(sock)
    elapsed = time.time() - t0

    registrar_respostas("autenticacao=" + str(resp))

    print("\n=== AUTENTICAÇÃO (PROTOBUF) ===")
    print(format_protobuf_response(resp, elapsed))

    if not resp.HasField("ok"):
        raise ErroProtocolo("Resposta AUTH não possui campo OK.")

    dados = resp.ok.dados
    if "token" not in dados:
        raise ErroProtocolo("Token não encontrado na resposta de autenticação.")

    return dados["token"]


def soma(sock, token, numeros):
    req = mensagens_pb2.Requisicao()
    req.operacao.token = token
    req.operacao.operacao = "soma"
    req.operacao.parametros["numeros"] = ",".join(str(n) for n in numeros)

    enviar(sock, req)
    t0 = time.time()
    resp = receber(sock)
    elapsed = time.time() - t0

    registrar_respostas("soma=" + str(resp))

    print("\n=== SOMA (PROTOBUF) ===")
    print(format_protobuf_response(resp, elapsed))


def echo(sock, token, texto):
    req = mensagens_pb2.Requisicao()
    req.operacao.token = token
    req.operacao.operacao = "echo"
    req.operacao.parametros["mensagem"] = texto

    enviar(sock, req)
    t0 = time.time()
    resp = receber(sock)
    elapsed = time.time() - t0

    registrar_respostas("echo=" + str(resp))

    print("\n=== ECHO (PROTOBUF) ===")
    print(format_protobuf_response(resp, elapsed))


def op_timestamp(sock, token):
    req = mensagens_pb2.Requisicao()
    req.operacao.token = token
    req.operacao.operacao = "timestamp"

    enviar(sock, req)
    t0 = time.time()
    resp = receber(sock)
    elapsed = time.time() - t0

    registrar_respostas("timestamp=" + str(resp))

    print("\n=== TIMESTAMP (PROTOBUF) ===")
    print(format_protobuf_response(resp, elapsed))


def status(sock, token):
    req = mensagens_pb2.Requisicao()
    req.operacao.token = token
    req.operacao.operacao = "status"

    enviar(sock, req)
    t0 = time.time()
    resp = receber(sock)
    elapsed = time.time() - t0

    registrar_respostas("status=" + str(resp))

    print("\n=== STATUS (PROTOBUF) ===")
    print(format_protobuf_response(resp, elapsed))


def historico(sock, token):
    req = mensagens_pb2.Requisicao()
    req.operacao.token = token
    req.operacao.operacao = "historico"

    enviar(sock, req)
    t0 = time.time()
    resp = receber(sock)
    elapsed = time.time() - t0

    registrar_respostas("historico=" + str(resp))

    print("\n=== HISTÓRICO (PROTOBUF) ===")
    print(format_protobuf_response(resp, elapsed))


def info(sock):
    req = mensagens_pb2.Requisicao()
    req.info.tipo = "basico"

    enviar(sock, req)
    t0 = time.time()
    resp = receber(sock)
    elapsed = time.time() - t0

    registrar_respostas("info=" + str(resp))

    print("\n=== INFO (PROTOBUF) ===")
    print(format_protobuf_response(resp, elapsed))


def logout(sock, token):
    req = mensagens_pb2.Requisicao()
    req.logout.token = token

    enviar(sock, req)
    t0 = time.time()
    resp = receber(sock)
    elapsed = time.time() - t0

    registrar_respostas("logout=" + str(resp))

    print("\n=== LOGOUT (PROTOBUF) ===")
    print(format_protobuf_response(resp, elapsed))


# ---------------------------------------
# Interface para o MENU
# ---------------------------------------

def servidor_protobuf(op_code, param=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((SERVER_IP, SERVER_PORT))
        timestamp = datetime.now().isoformat()

        token = autenticar(sock, timestamp)

        if op_code == 1:
            nums = param
            if isinstance(nums, str):
                nums = [float(x.strip()) for x in nums.split(",") if x.strip()]
            soma(sock, token, nums)

        elif op_code == 2:
            echo(sock, token, param or "Hello")

        elif op_code == 3:
            op_timestamp(sock, token)

        elif op_code == 4:
            status(sock, token)

        elif op_code == 5:
            historico(sock, token)

        elif op_code == 6:
            info(sock)

        else:
            print("Operação inválida.")

        logout(sock, token)

    except (ErroRede, ErroProtocolo) as e:
        print("Erro (protobuf):", e)

    finally:
        sock.close()
