Как запустить

Шаг 1. Запустить симулятор

Симулятор должен быть запущен до запуска тестов — иначе соединение
на порту 2001 будет отклонено с ошибкой ConnectionRefusedError.

Открой первый терминал и запусти:

bash
python simulator.py
Должно появиться сообщение вида:

text
Симулятор слушает 127.0.0.1:2001. Ctrl+C для остановки.
Оставь этот терминал открытым.

Шаг 2. Запустить тесты

Открой второй терминал и выполни:

bash
pytest -v script.py
Флаг -v включает подробный вывод.

Ожидаемый результат

text
collected 3 items

script.py::test_receive_ten_signals_with_full_structure PASSED   [ 33%]
script.py::test_signal_ids_are_unique PASSED                     [ 66%]
script.py::test_values_change_over_time PASSED                   [100%]

========================= 3 passed in 2.43s =========================
