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