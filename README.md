# TCP Signal Monitoring — Automated Tests

An educational QA automation project that tests a local TCP service streaming JSON signal data.

## What is tested

- Receiving 10 signal records with the required fields.
- Checking that signal IDs are unique within a snapshot.
- Checking that signal values change over time.
- Validating the `quality` field against the supported values: `GOOD`, `BAD`, and `UNCERTAIN`.

## Tech stack

- Python
- pytest
- TCP sockets
- JSON
- GitHub Actions

## Project structure

```text
WelcomeScreen/
├── script.py       # Automated tests
└── simulator.py   # Local TCP test-data simulator
```

## Run locally

Use Python 3.10 or newer.

1. Install the dependency:

   ```bash
   python -m pip install -r requirements.txt
   ```

2. In the first terminal, start the simulator from the repository root:

   ```bash
   python -u WelcomeScreen/simulator.py
   ```

3. Keep the simulator running. In a second terminal, run:

   ```bash
   python -m pytest -v WelcomeScreen/script.py
   ```

The simulator listens on `127.0.0.1:2001`. Stop it with `Ctrl+C`.

## Limitations

This project uses a local simulator, not a production monitoring service. The tests cover the data stream and basic message validation; they do not test a graphical user interface.

This is a learning portfolio project, not commercial QA experience.
