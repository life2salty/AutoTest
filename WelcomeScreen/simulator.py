"""Local TCP simulator that streams changing JSON signal values."""

import json
import math
import socket
import time

HOST = "127.0.0.1"
PORT = 2001
SIGNALS = 10
SNAPSHOT_INTERVAL = 0.2


def build_snapshot(tick: int) -> str:
    """Return 10 newline-delimited JSON signal records."""
    lines = []
    for i in range(SIGNALS):
        signal = {
            "id": i + 1,
            "name": f"Signal_{i + 1}",
            "value": round(math.sin(tick / 10 + i) * 100, 2),
            "quality": "GOOD",
            "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        lines.append(json.dumps(signal))
    return "\n".join(lines) + "\n"


def handle_client(conn: socket.socket, addr) -> None:
    print(f"Client connected: {addr}")
    tick = 0
    try:
        while True:
            conn.sendall(build_snapshot(tick).encode("utf-8"))
            tick += 1
            time.sleep(SNAPSHOT_INTERVAL)
    except (BrokenPipeError, ConnectionResetError):
        print(f"Client disconnected: {addr}")
    finally:
        conn.close()


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"Simulator listening on {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            handle_client(conn, addr)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSimulator stopped.")
