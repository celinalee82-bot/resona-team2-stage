#!/usr/bin/env python3
"""RESONA 중계 — resona.html 이 보내는 값을 무대 시뮬레이터로 넘긴다.

resona.html 은 ws://localhost:9980 에 '클라이언트'로 접속해서 값을 보낸다
(원래 TouchDesigner WebSocket DAT 자리). 이 스크립트가 그 자리에 서서
받은 메시지를 접속한 다른 모든 창(stage_sim.html 등)에 그대로 뿌린다.

설치할 것 없음 — 파이썬 기본 기능만 쓴다.
실행:  python3 relay.py            (포트 9980)
       python3 relay.py 9981       (포트 바꾸기)
"""
import base64
import functools
import hashlib
import socket
import struct
import sys
import threading

print = functools.partial(print, flush=True)
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9980
GUID = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

clients = set()
lock = threading.Lock()


def handshake(conn):
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = conn.recv(4096)
        if not chunk:
            return False
        data += chunk
    key = None
    for line in data.split(b"\r\n"):
        if line.lower().startswith(b"sec-websocket-key:"):
            key = line.split(b":", 1)[1].strip()
    if not key:
        return False
    accept = base64.b64encode(hashlib.sha1(key + GUID).digest())
    conn.sendall(
        b"HTTP/1.1 101 Switching Protocols\r\n"
        b"Upgrade: websocket\r\nConnection: Upgrade\r\n"
        b"Sec-WebSocket-Accept: " + accept + b"\r\n\r\n"
    )
    return True


def recv_exact(conn, n):
    buf = b""
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            raise ConnectionError
        buf += chunk
    return buf


def read_frame(conn):
    b1, b2 = recv_exact(conn, 2)
    opcode = b1 & 0x0F
    masked = b2 & 0x80
    length = b2 & 0x7F
    if length == 126:
        length = struct.unpack(">H", recv_exact(conn, 2))[0]
    elif length == 127:
        length = struct.unpack(">Q", recv_exact(conn, 8))[0]
    mask = recv_exact(conn, 4) if masked else b""
    payload = recv_exact(conn, length)
    if masked:
        payload = bytes(c ^ mask[i % 4] for i, c in enumerate(payload))
    return opcode, payload


def make_frame(payload, opcode=0x1):
    n = len(payload)
    if n < 126:
        head = struct.pack(">BB", 0x80 | opcode, n)
    elif n < 65536:
        head = struct.pack(">BBH", 0x80 | opcode, 126, n)
    else:
        head = struct.pack(">BBQ", 0x80 | opcode, 127, n)
    return head + payload


def broadcast(sender, frame):
    with lock:
        targets = [c for c in clients if c is not sender]
    for c in targets:
        try:
            c.sendall(frame)
        except OSError:
            with lock:
                clients.discard(c)


def serve(conn, addr):
    try:
        if not handshake(conn):
            conn.close()
            return
        with lock:
            clients.add(conn)
        print(f"+ 접속 {addr[0]}:{addr[1]}  (현재 {len(clients)}개)")
        while True:
            opcode, payload = read_frame(conn)
            if opcode == 0x8:  # close
                break
            if opcode == 0x9:  # ping
                conn.sendall(make_frame(payload, 0xA))
            elif opcode in (0x1, 0x2):
                broadcast(conn, make_frame(payload, opcode))
    except (ConnectionError, OSError):
        pass
    finally:
        with lock:
            clients.discard(conn)
        try:
            conn.close()
        except OSError:
            pass
        print(f"- 해제 {addr[0]}:{addr[1]}  (현재 {len(clients)}개)")


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", PORT))
    srv.listen(16)
    print(f"RESONA 중계 대기 중 — ws://localhost:{PORT}")
    print("1) resona.html 에서 「WS 연결」  2) stage_sim.html 열기   (끄기: Ctrl+C)")
    try:
        while True:
            conn, addr = srv.accept()
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            threading.Thread(target=serve, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\n중계 종료")


if __name__ == "__main__":
    main()
