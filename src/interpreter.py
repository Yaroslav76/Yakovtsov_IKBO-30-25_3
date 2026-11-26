"""Интерпретатор УВМ: выполняет двоичную программу и сохраняет дамп памяти.

Запуск: python3 -m src.interpreter программа.bin дамп.json --range 0:99
"""
import argparse
import json
import re
import sys

from machine import MEMORY_SIZE, Machine, MachineError

STATUS_USAGE = 2
STATUS_RUNTIME = 1
RANGE = re.compile(r"^(\d+):(\d+)$")


class InterpreterError(Exception):
    """Ошибка аргументов или файлов интерпретатора."""


def parse_range(text):
    """Разбирает 'НАЧАЛО:КОНЕЦ' (оба адреса включительно)."""
    match = RANGE.match(text)
    if not match:
        raise InterpreterError(
            f"диапазон '{text}': ожидается вид НАЧАЛО:КОНЕЦ, например 0:99")
    start, end = int(match.group(1)), int(match.group(2))
    if end < start or end >= MEMORY_SIZE:
        raise InterpreterError(
            f"диапазон {start}:{end}: нужно НАЧАЛО <= КОНЕЦ <= "
            f"{MEMORY_SIZE - 1}")
    return start, end


def read_program(path):
    """Читает двоичный файл программы."""
    try:
        with open(path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        raise InterpreterError(f"файл не найден: {path}")
    except IsADirectoryError:
        raise InterpreterError(f"это каталог, а не файл: {path}")
    except OSError as e:
        raise InterpreterError(f"не удалось прочитать '{path}': {e}")


def write_dump(path, dump):
    """Сохраняет дамп памяти в JSON-файл."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dump, f, ensure_ascii=False, indent=2)
            f.write("\n")
    except OSError as e:
        raise InterpreterError(f"не удалось записать '{path}': {e.strerror}")


def parse_args(argv=None):
    """Разбирает параметры командной строки."""
    parser = argparse.ArgumentParser(
        description="Интерпретатор учебной виртуальной машины (УВМ)")
    parser.add_argument("program", help="двоичный файл программы")
    parser.add_argument("dump", help="файл для дампа памяти (JSON)")
    parser.add_argument("--range", required=True, dest="addresses",
                        metavar="НАЧАЛО:КОНЕЦ",
                        help="диапазон адресов дампа (включительно)")
    return parser.parse_args(argv)


def main(argv=None):
    """Точка входа интерпретатора; возвращает код завершения."""
    args = parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure") and not stream.isatty():
            stream.reconfigure(encoding="utf-8")
    try:
        start, end = parse_range(args.addresses)
        machine = Machine()
        machine.load(read_program(args.program))
        count = machine.run()
        write_dump(args.dump, machine.dump(start, end))
    except InterpreterError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return STATUS_USAGE
    except MachineError as e:
        print(f"Ошибка выполнения: {e}", file=sys.stderr)
        return STATUS_RUNTIME
    print(f"Выполнено команд: {count}; дамп {start}:{end} записан в "
          f"{args.dump}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
