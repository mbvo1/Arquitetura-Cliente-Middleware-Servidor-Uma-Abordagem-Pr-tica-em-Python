import socket
import json
import threading
import logging
import time
import uuid

HOST = "127.0.0.1"
PORT_CLIENTE = 5000
PORT_SERVIDOR = 5002
CHAVE_SECRETA = "12345"
LOG_FILE = "middleware.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [MIDDLEWARE] %(levelname)s %(message)s"
)
log_lock = threading.Lock()

def log_safe(msg: str):
    with log_lock:
        logging.info(msg)

def send_json(conn, obj: dict):
    data = json.dumps(obj, ensure_ascii=False) + "\n"
    conn.sendall(data.encode("utf-8"))

def recv_json_line(conn):
    f = conn.makefile("r", encoding="utf-8")
    line = f.readline()
    if not line:
        return None
    return json.loads(line)

def forward_to_server(payload: dict):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT_SERVIDOR))
        send_json(s, payload)
        return recv_json_line(s)

def handle_client(conn_cliente, addr):
    try:
        req = recv_json_line(conn_cliente)
        if not req:
            return
        if req.get("chave") != CHAVE_SECRETA:
            send_json(conn_cliente, {"erro": "Acesso negado"})
            log_safe(f"{addr} acesso negado: {req}")
            return
        req_id = req.get("request_id") or str(uuid.uuid4())
        req["request_id"] = req_id
        req["via"] = "middleware"
        t0 = time.time()
        resp = forward_to_server(req)
        elapsed_ms = int((time.time() - t0) * 1000)
        if isinstance(resp, dict):
            resp["middleware_elapsed_ms"] = elapsed_ms
            resp["request_id"] = req_id
        else:
            resp = {"request_id": req_id, "erro": "Resposta inválida do servidor"}
        send_json(conn_cliente, resp)
        log_safe(f"{addr} req_id={req_id} {req} -> {resp}")
    except Exception as e:
        try:
            send_json(conn_cliente, {"erro": f"{type(e).__name__}: {e}"})
        except:
            pass
        log_safe(f"ERROR {addr} {e}")
    finally:
        conn_cliente.close()

def serve():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as m:
        m.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        m.bind((HOST, PORT_CLIENTE))
        m.listen()
        print(f"[Middleware] Escutando clientes em {HOST}:{PORT_CLIENTE} ...")
        log_safe(f"Middleware iniciado em {HOST}:{PORT_CLIENTE}")
        while True:
            conn, addr = m.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()

if __name__ == "__main__":
    serve()
