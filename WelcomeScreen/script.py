"""
Автотест для десктоп-приложения мониторинга сигналов.

Критичный сценарий:
    Подключиться к сервису-симулятору на порту 2001 и проверить,
    что приходят 10 сигналов с корректной структурой и что
    значения обновляются со временем.

Зависимости:
    pip install pytest

Перед запуском:
    Симулятор должен быть запущен на 127.0.0.1:2001.
    Запуск: pytest -v script.py
"""

import json
import socket
import time

import pytest

HOST = "127.0.0.1"
PORT = 2001
EXPECTED_SIGNALS = 10
REQUIRED_FIELDS = {"id", "name", "value", "quality", "time"}
VALID_QUALITY = {"GOOD", "BAD", "UNCERTAIN"}
RECV_TIMEOUT = 5.0


def read_message(sock: socket.socket, buffer: bytes = b"") -> tuple[dict, bytes]:
    sock.settimeout(RECV_TIMEOUT)
    while b"\n" not in buffer:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("Соединение закрыто сервером")
        buffer += chunk
    line, buffer = buffer.split(b"\n", 1)
    return json.loads(line.decode("utf-8").strip()), buffer


def read_signal_batch(sock: socket.socket) -> list[dict]:
    signals = []
    buffer = b""
    for _ in range(EXPECTED_SIGNALS):
        message, buffer = read_message(sock, buffer)
        signals.append(message)
    return signals


@pytest.fixture(scope="module")
def client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    yield sock
    sock.close()


def test_receive_ten_signals_with_full_structure(client):
    signals = read_signal_batch(client)

    assert len(signals) == EXPECTED_SIGNALS, (
        f"Ожидалось {EXPECTED_SIGNALS} сигналов, получено {len(signals)}"
    )

    for signal in signals:
        missing = REQUIRED_FIELDS - signal.keys()
        assert not missing, (
            f"У сигнала id={signal.get('id')} отсутствуют поля: {missing}"
        )
        assert signal["quality"] in VALID_QUALITY, (
            f"Некорректное качество '{signal['quality']}' у сигнала id={signal['id']}"
        )


def test_signal_ids_are_unique(client):
    signals = read_signal_batch(client)
    ids = [s["id"] for s in signals]
    assert len(set(ids)) == EXPECTED_SIGNALS, f"Дублирующиеся ID сигналов: {ids}"


def test_values_change_over_time(client):
    seen_values: dict[int, set] = {}
    start = time.time()
    buffer = b""

    while time.time() - start < 2.0:
        try:
            message, buffer = read_message(client, buffer)
        except socket.timeout:
            break
        seen_values.setdefault(message["id"], set()).add(message["value"])

    changing = [sid for sid, values in seen_values.items() if len(values) > 1]
    assert changing, (
        "Ни один сигнал не изменил значение за 2 секунды — "
        "возможно, сервис завис или значения статичны"
    )