"""Модульные тесты интерпретатора: аргументы, дамп, ошибки."""
import contextlib
import io
import json
import os
import tempfile
import unittest

import helpers
from src.assembler import parse_program
from src.codec import encode_program
from src.interpreter import InterpreterError, main, parse_range

COPY = helpers.example("copy_array.yaml")


def program_file(text):
    """Записывает ассемблированную программу во временный файл."""
    handle, path = tempfile.mkstemp(suffix=".bin")
    with os.fdopen(handle, "wb") as f:
        f.write(encode_program(parse_program(text)))
    return path


class RangeTests(unittest.TestCase):
    """Разбор диапазона адресов."""

    def test_valid(self):
        """Корректный диапазон, включая одну ячейку и последнюю."""
        self.assertEqual(parse_range("200:209"), (200, 209))
        self.assertEqual(parse_range("5:5"), (5, 5))
        self.assertEqual(parse_range("0:8191"), (0, 8191))

    def test_invalid(self):
        """Неверный вид, обратный порядок, выход за память."""
        for text in ("abc", "1-5", "5:1", "0:8192", "-1:5", "1:"):
            with self.assertRaises(InterpreterError):
                parse_range(text)


class CliTests(unittest.TestCase):
    """Запуск интерпретатора из командной строки."""

    def run_main(self, *args):
        """Возвращает (код, вывод, ошибки)."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out):
            with contextlib.redirect_stderr(err):
                code = main(list(args))
        return code, out.getvalue(), err.getvalue()

    def dump_of(self, text, rng):
        """Выполняет программу text и возвращает дамп (словарь)."""
        program = program_file(text)
        self.addCleanup(os.remove, program)
        dump = program + ".json"
        self.addCleanup(os.remove, dump)
        code, _, err = self.run_main(program, dump, "--range", rng)
        self.assertEqual(code, 0, err)
        with open(dump, encoding="utf-8") as f:
            return json.load(f)

    def test_dump_format(self):
        """Дамп в JSON: диапазон и значения ячеек."""
        data = self.dump_of("- load_const: 7\n- write: 500\n", "499:501")
        self.assertEqual(data["range"], [499, 501])
        self.assertEqual(data["memory"], {"499": 0, "500": 7, "501": 0})

    def test_copy_array(self):
        """Массив копируется на новое место."""
        with open(COPY, encoding="utf-8") as f:
            data = self.dump_of(f.read(), "200:209")
        cells = [data["memory"][str(a)] for a in range(200, 210)]
        self.assertEqual(cells, [11, 22, 33, 44, 55] * 2)

    def test_runtime_error_code(self):
        """Ошибка выполнения: код 1."""
        program = program_file("- read\n")
        self.addCleanup(os.remove, program)
        code, _, err = self.run_main(program, os.devnull, "--range", "0:1")
        self.assertEqual(code, 1)
        self.assertIn("пустой стек", err)

    def test_usage_errors(self):
        """Нет файла программы, неверный диапазон: код 2."""
        code, _, err = self.run_main("no_such.bin", os.devnull,
                                     "--range", "0:1")
        self.assertEqual(code, 2)
        self.assertIn("не найден", err)
        code, _, err = self.run_main("no_such.bin", os.devnull,
                                     "--range", "9:1")
        self.assertEqual(code, 2)
        self.assertIn("диапазон", err)


if __name__ == "__main__":
    unittest.main()
