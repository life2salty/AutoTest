"""
Минимальный сервис-симулятор для проверки автотеста.
Отправляет 10 сигналов (JSON, разделённых \n) на порт 2001.
Значения меняются (синусоида), качество — GOOD.
Остановка: Ctrl+C.
"""

import json
import math
import socket
import time

HOST = "127.0.0.1"
PORT = 2001
SIGNALS = 10


def build_snapshot(tick: int) -> str:
    """Сформировать один снимок из 10 сигналов в виде строки JSON+\n."""
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


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"Симулятор слушает {HOST}:{PORT}. Ctrl+C для остановки.")

    conn, addr = server.accept()
    print(f"Клиент подключился: {addr}")

    tick = 0
    try:
        while True:
            conn.sendall(build_snapshot(tick).encode("utf-8"))
            tick += 1
            time.sleep(0.2)  # 5 снимков в секунду — достаточно для тестов
    except (BrokenPipeError, KeyboardInterrupt):
        print("Остановлено.")
    finally:
        conn.close()
        server.close()


if __name__ == "__main__":
    main()