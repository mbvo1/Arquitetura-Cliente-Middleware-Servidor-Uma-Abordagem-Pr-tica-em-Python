import socket
import json
import argparse
import threading
import uuid
import time

HOST = "127.0.0.1"
PORT = 5000

def send_json(conn, obj: dict):
    data = json.dumps(obj, ensure_ascii=False) + "\n"
    conn.sendall(data.encode("utf-8"))

def recv_json_line(conn):
    f = conn.makefile("r", encoding="utf-8")
    line = f.readline()
    if not line:
        return None
    return json.loads(line)

def requisicao(payload):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
            c.connect((HOST, PORT))
            send_json(c, payload)
            resp = recv_json_line(c)
            print("→ Req:", payload, "\n← Resp:", resp, "\n")
    except Exception as e:
        print("Erro na requisição:", e)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--op", default="multiplicacao", choices=["soma","subtracao","multiplicacao","divisao","fib"])
    parser.add_argument("--a", type=float, default=10.0)
    parser.add_argument("--b", type=float, default=5.0)
    parser.add_argument("--n", type=int, default=35)
    parser.add_argument("--paralelo", type=int, default=1)
    parser.add_argument("--chave", default="12345")
    args = parser.parse_args()

    base = {"chave": args.chave, "operacao": args.op, "request_id": str(uuid.uuid4())}
    if args.op == "fib":
        base["n"] = args.n
    else:
        base["a"] = args.a
        base["b"] = args.b

    threads = []
    t0 = time.time()
    for i in range(args.paralelo):
        payload = dict(base)
        payload["request_id"] = f"{base['request_id']}-{i}"
        t = threading.Thread(target=requisicao, args=(payload,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    print(f"Tempo total (cliente) para {args.paralelo} reqs: {int((time.time()-t0)*1000)} ms")

if __name__ == "__main__":
    main()
