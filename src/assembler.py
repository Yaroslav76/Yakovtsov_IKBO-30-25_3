"""Ассемблер УВМ: программа на YAML в машинный код.

Запуск: python3 -m src.assembler программа.yaml результат.bin [--test]
"""
import argparse
import sys

import yaml

from codec import encode, encode_program, format_bytes
from ir import Instruction
from spec import BY_NAME

STATUS_ERROR = 2
KEYS_PER_ITEM = 1


class AssemblerError(Exception):
    """Ошибка в тексте программы или при работе с файлами."""


def read_source(path):
    """Читает текст исходной программы."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise AssemblerError(f"файл не найден: {path}")
    except IsADirectoryError:
        raise AssemblerError(f"это каталог, а не файл: {path}")
    except (OSError, UnicodeDecodeError) as e:
        raise AssemblerError(f"не удалось прочитать '{path}': {e}")


def _split_item(number, item):
    """Разбирает элемент списка на (имя команды, операнд)."""
    if isinstance(item, str):
        return item, None
    if isinstance(item, dict) and len(item) == KEYS_PER_ITEM:
        return next(iter(item.items()))
    raise AssemblerError(
        f"команда №{number}: ожидается 'имя' или 'имя: значение'")

def _check_operand(number, spec, operand):
    """Проверяет операнд (поле B) и возвращает его."""
    where = f"команда №{number} ({spec.name})"
    if not spec.operand_bits:
        if operand is not None:
            raise AssemblerError(f"{where}: операнд не нужен")
        return None
    if operand is None:
        raise AssemblerError(f"{where}: требуется операнд (поле B)")
    if isinstance(operand, bool) or not isinstance(operand, int):
        raise AssemblerError(f"{where}: операнд должен быть целым числом")
    if operand not in range(spec.max_operand() + 1):
        raise AssemblerError(
            f"{where}: операнд {operand} вне диапазона "
            f"0..{spec.max_operand()}")
    return operand


def _parse_item(number, item):
    """Превращает элемент YAML-списка в Instruction."""
    name, operand = _split_item(number, item)
    spec = BY_NAME.get(name)
    if spec is None:
        known = ", ".join(BY_NAME)
        raise AssemblerError(
            f"команда №{number}: неизвестная команда '{name}' "
            f"(допустимые: {known})")
    return Instruction(spec.name, spec.opcode,
                       _check_operand(number, spec, operand))


def parse_program(text):
    """Разбирает текст YAML; возвращает список Instruction."""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise AssemblerError("некорректный YAML: " + " ".join(
            str(e).split()))
    if not isinstance(data, list) or not data:
        raise AssemblerError("программа должна быть непустым списком команд")
    return [_parse_item(number, item)
            for number, item in enumerate(data, 1)]


def write_binary(path, data):
    """Записывает машинный код в двоичный файл."""
    try:
        with open(path, "wb") as f:
            f.write(data)
    except OSError as e:
        raise AssemblerError(f"не удалось записать '{path}': {e.strerror}")


def print_test_output(program):
    """Режим тестирования: поля и байты каждой команды."""
    for instruction in program:
        print(instruction.fields())
        print(format_bytes(encode(instruction)))


def parse_args(argv=None):
    """Разбирает параметры командной строки."""
    parser = argparse.ArgumentParser(
        description="Ассемблер учебной виртуальной машины (УВМ)")
    parser.add_argument("source", help="исходный файл программы (YAML)")
    parser.add_argument("output", help="двоичный файл-результат")
    parser.add_argument("--test", action="store_true",
                        help="режим тестирования: вывод на экран")
    return parser.parse_args(argv)


def main(argv=None):
    """Точка входа ассемблера; возвращает код завершения."""
    args = parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure") and not stream.isatty():
            stream.reconfigure(encoding="utf-8")
    try:
        program = parse_program(read_source(args.source))
        data = encode_program(program)
        write_binary(args.output, data)
    except AssemblerError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return STATUS_ERROR
    if args.test:
        print_test_output(program)
    print(f"Размер двоичного файла: {len(data)} байт")
    return 0


if __name__ == "__main__":
    sys.exit(main())