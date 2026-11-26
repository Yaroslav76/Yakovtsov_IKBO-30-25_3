"""Модульные тесты разбора языка ассемблера (YAML)."""
import contextlib
import io
import os
import unittest

import helpers
from assembler import AssemblerError, main, parse_program, read_source
from ir import Instruction

SPEC_FIELDS = ["A=63, B=61", "A=7", "A=3, B=629", "A=44, B=975"]
SPEC_TEXT = "- load_const: 61\n- read\n- write: 629\n- sub: 975\n"


class ParseTests(unittest.TestCase):
    """Разбор допустимых программ."""

    def test_spec_program_fields(self):
        """Поля команд совпадают с тестами спецификации."""
        program = parse_program(SPEC_TEXT)
        self.assertEqual([i.fields() for i in program], SPEC_FIELDS)

    def test_instruction_values(self):
        """Внутреннее представление: имя, поле A, поле B."""
        program = parse_program(SPEC_TEXT)
        self.assertEqual(program[0], Instruction("load_const", 63, 61))
        self.assertEqual(program[1], Instruction("read", 7, None))

    def test_null_operand_for_read(self):
        """Запись 'read:' без значения допустима."""
        program = parse_program("- read:\n")
        self.assertEqual(program[0].name, "read")

    def test_operand_limits(self):
        """Граничные значения операндов принимаются."""
        program = parse_program(
            "- load_const: 0\n- load_const: 1023\n- write: 8191\n")
        self.assertEqual([i.b for i in program], [0, 1023, 8191])

    def test_yaml_comments_and_hex(self):
        """Комментарии YAML и шестнадцатеричные числа."""
        program = parse_program("- load_const: 0x1F   # тридцать один\n")
        self.assertEqual(program[0].b, 31)


class ErrorTests(unittest.TestCase):
    """Обработка ошибок в программе."""

    def fails(self, text):
        """Текст ошибки для некорректной программы."""
        with self.assertRaises(AssemblerError) as ctx:
            parse_program(text)
        return str(ctx.exception)

    def test_unknown_command(self):
        """Неизвестная команда с номером."""
        self.assertIn("№2", self.fails("- read\n- jump: 1\n"))

    def test_operand_problems(self):
        """Нет операнда, лишний операнд, неверный тип и диапазон."""
        self.assertIn("требуется", self.fails("- write\n"))
        self.assertIn("не нужен", self.fails("- read: 1\n"))
        self.assertIn("целым", self.fails("- write: abc\n"))
        self.assertIn("целым", self.fails("- load_const: true\n"))
        self.assertIn("диапазона", self.fails("- load_const: 1024\n"))
        self.assertIn("диапазона", self.fails("- write: 8192\n"))
        self.assertIn("диапазона", self.fails("- sub: -1\n"))

    def test_structure_problems(self):
        """Не список, пустая программа, неверные элементы, плохой YAML."""
        self.assertIn("списком", self.fails("load_const: 5\n"))
        self.assertIn("списком", self.fails(""))
        self.assertIn("ожидается", self.fails("- 42\n"))
        self.assertIn("ожидается", self.fails("- {read: null, sub: 1}\n"))
        self.assertIn("YAML", self.fails("- load_const: [\n"))

    def test_read_source_errors(self):
        """Нет файла и каталог вместо файла."""
        with self.assertRaises(AssemblerError):
            read_source("no_such_file.yaml")
        with self.assertRaises(AssemblerError):
            read_source(helpers.EXAMPLES)


class CliTests(unittest.TestCase):
    """Запуск ассемблера из командной строки (режим тестирования)."""

    def run_main(self, *args):
        """Возвращает (код, вывод, ошибки)."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out):
            with contextlib.redirect_stderr(err):
                code = main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_spec_fields_in_test_mode(self):
        """Режим --test печатает поля как в спецификации."""
        source = helpers.example("spec_tests.yaml")
        code, out, _ = self.run_main(source, os.devnull, "--test")
        self.assertEqual(code, 0)
        fields = [line for line in out.split("\n") if line.startswith("A=")]
        self.assertEqual(fields, SPEC_FIELDS)

    def test_error_exit_code(self):
        """Ошибка в программе: сообщение и код 2."""
        source = helpers.example("errors", "unknown_command.yaml")
        code, _, err = self.run_main(source, os.devnull)
        self.assertEqual(code, 2)
        self.assertIn("неизвестная команда", err)

    def test_missing_file(self):
        """Несуществующий исходный файл."""
        code, _, err = self.run_main("no_such.yaml", os.devnull)
        self.assertEqual(code, 2)
        self.assertIn("не найден", err)


if __name__ == "__main__":
    unittest.main()
