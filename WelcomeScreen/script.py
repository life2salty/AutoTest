"""Automated tests for a TCP signal-monitoring service."""

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
    """Read one newline-delimited JSON message, preserving extra bytes."""
    sock.settimeout(RECV_TIMEOUT)
    while b"\n" not in buffer:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("The server closed the connection")
        buffer += chunk

    line, buffer = buffer.split(b"\n", 1)
    return json.loads(line.decode("utf-8")), buffer


def read_signal_batch(sock: socket.socket) -> list[dict]:
    """Read the next 10 signal messages from the stream."""
    signals = []
    buffer = b""
    for _ in range(EXPECTED_SIGNALS):
        message, buffer = read_message(sock, buffer)
        signals.append(message)
    return signals


@pytest.fixture
def client():
    """Use a fresh TCP connection for each test."""
    with socket.create_connection((HOST, PORT), timeout=RECV_TIMEOUT) as sock:
        yield sock


def test_receive_ten_signals_with_full_structure(client):
    signals = read_signal_batch(client)

    assert len(signals) == EXPECTED_SIGNALS

    for signal in signals:
        missing = REQUIRED_FIELDS - signal.keys()
        assert not missing, (
            f"Signal {signal.get('id')} is missing fields: {missing}"
        )
        assert signal["quality"] in VALID_QUALITY, (
            f"Invalid quality {signal['quality']!r} for signal {signal['id']}"
        )


def test_signal_ids_are_unique(client):
    signals = read_signal_batch(client)
    ids = [signal["id"] for signal in signals]

    assert len(set(ids)) == EXPECTED_SIGNALS, (
        f"Duplicate signal IDs found: {ids}"
    )


def test_values_change_over_time(client):
    deadline = time.monotonic() + 3.0
    values_by_id = {}
    buffer = b""

    while time.monotonic() < deadline:
        message, buffer = read_message(client, buffer)
        signal_id = message["id"]
        values_by_id.setdefault(signal_id, set()).add(message["value"])

        if any(len(values) > 1 for values in values_by_id.values()):
            return

    pytest.fail("No signal value changed within 3 seconds")
