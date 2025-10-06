import socket
import json
import threading
import logging
import time
import uuid
from concurrent.futures import ProcessPoolExecutor

HOST = "127.0.0.1"
PORT = 5002
LOG_FILE = "server.log"
MAX_WORKERS = 4

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [SERVER] %(levelname)s %(message)s"
)
log_lock = threading.Lock()

def log_safe(msg: str):
    with log_lock:
        logging.info(msg)

def fib(n: int) -> int:
    if n < 0:
        raise ValueError("n deve ser >= 0")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def calcular(payload: dict):
    op = payload.get("operacao")
    if op in {"soma", "subtracao", "multiplicacao", "divisao"}:
        a = float(payload.get("a", 0))
        b = float(payload.get("b", 0))
        if op == "soma":
            return a + b
        elif op == "subtracao":
            return a - b
        elif op == "multiplicacao":
            return a * b
        elif op == "divisao":
            if b == 0:
                return "Erro: divisão por zero"
            return a / b
    elif op == "fib":
        n = int(payload.get("n", 0))
        return fib(n)
    return "Operação inválida"

def send_json(conn, obj: dict):
    data = json.dumps(obj, ensure_ascii=False) + "\n"
    conn.sendall(data.encode("utf-8"))

def recv_json_line(conn):
    f = conn.makefile("r", encoding="utf-8")
    line = f.readline()
    if not line:
        return None
    return json.loads(line)

def handle_client(conn, addr, executor: ProcessPoolExecutor):
    try:
        req = recv_json_line(conn)
        if not req:
            return
        req_id = req.get("request_id", str(uuid.uuid4()))
        t0 = time.time()
        future = executor.submit(calcular, req)
        result = future.result()
        elapsed_ms = int((time.time() - t0) * 1000)
        resp = {"request_id": req_id, "resultado": result, "elapsed_ms": elapsed_ms}
        send_json(conn, resp)
        log_safe(f"{addr} req_id={req_id} {req} -> {resp}")
    except Exception as e:
        err = {"erro": f"{type(e).__name__}: {e}"}
        try:
            send_json(conn, err)
        except:
            pass
        log_safe(f"ERROR {addr} {e}")
    finally:
        conn.close()

def serve():
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            print(f"[Servidor] Escutando em {HOST}:{PORT} ...")
            log_safe(f"Servidor iniciado em {HOST}:{PORT}")
            while True:
                conn, addr = s.accept()
                t = threading.Thread(target=handle_client, args=(conn, addr, executor), daemon=True)
                t.start()

if __name__ == "__main__":
    serve()
