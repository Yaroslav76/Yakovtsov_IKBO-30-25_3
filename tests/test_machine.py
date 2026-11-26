"""Модульные тесты модели УВМ и команд загрузки и памяти."""
import unittest

import helpers
from assembler import parse_program
from codec import encode_program
from machine import MEMORY_SIZE, Machine, MachineError, wrap


def run(text):
    """Ассемблирует и выполняет программу; возвращает машину."""
    machine = Machine()
    machine.load(encode_program(parse_program(text)))
    machine.run()
    return machine


class CommandTests(unittest.TestCase):
    """Выполнение команд."""

    def test_load_const(self):
        """Константа кладётся на стек."""
        machine = run("- load_const: 61\n- load_const: 5\n")
        self.assertEqual(machine.stack, [61, 5])

    def test_write(self):
        """Запись снимает значение со стека и пишет по адресу B."""
        machine = run("- load_const: 77\n- write: 500\n")
        self.assertEqual(machine.memory[500], 77)
        self.assertEqual(machine.stack, [])

    def test_read(self):
        """Чтение снимает адрес и кладёт значение по этому адресу."""
        machine = run("- load_const: 9\n- write: 500\n"
                      "- load_const: 500\n- read\n")
        self.assertEqual(machine.stack, [9])

    def test_unified_memory(self):
        """Программа лежит в той же памяти, что и данные."""
        machine = run("- load_const: 0\n- read\n")
        self.assertEqual(machine.stack, [63])
        self.assertEqual(machine.size, 6)

    def test_wrap(self):
        """Значения ячеек - 32-битные со знаком."""
        self.assertEqual(wrap(2 ** 31), -2 ** 31)
        self.assertEqual(wrap(-1), -1)


class SubTests(unittest.TestCase):
    """Команда вычитания."""

    PREFIX = ("- load_const: 100\n- write: 300\n"
              "- load_const: 58\n- write: 301\n")

    def test_order_of_operands(self):
        """Результат: память[B] - память[снятый со стека адрес]."""
        machine = run(self.PREFIX + "- load_const: 301\n- sub: 300\n")
        self.assertEqual(machine.stack, [42])
        machine = run(self.PREFIX + "- load_const: 300\n- sub: 301\n")
        self.assertEqual(machine.stack, [-42])

    def test_result_to_memory(self):
        """Результат вычитания записывается в память."""
        machine = run(self.PREFIX + "- load_const: 301\n- sub: 300\n"
                      "- write: 302\n")
        self.assertEqual(machine.memory[302], 42)
        self.assertEqual(machine.stack, [])

    def test_same_cell(self):
        """Вычитание ячейки из самой себя даёт ноль."""
        machine = run(self.PREFIX + "- load_const: 300\n- sub: 300\n")
        self.assertEqual(machine.stack, [0])

    def test_wraps_to_32_bits(self):
        """Переполнение 32-битного значения оборачивается."""
        machine = Machine()
        machine.memory[300] = -2 ** 31
        machine.memory[301] = 1
        machine.load(encode_program(parse_program(
            "- load_const: 301\n- sub: 300\n")))
        machine.run()
        self.assertEqual(machine.stack, [2 ** 31 - 1])

    def test_errors(self):
        """Пустой стек и адрес вне памяти (в том числе отрицательный)."""
        failure = ErrorTests().fails
        self.assertIn("пустой стек", failure("- sub: 300\n"))
        negative = self.PREFIX + "- load_const: 300\n- sub: 301\n- read\n"
        self.assertIn("вне памяти", failure(negative))


class ErrorTests(unittest.TestCase):
    """Ошибки выполнения и загрузки."""

    def fails(self, program):
        """Текст ошибки выполнения программы (байты или YAML)."""
        machine = Machine()
        try:
            if isinstance(program, str):
                program = encode_program(parse_program(program))
            machine.load(program)
            machine.run()
        except MachineError as e:
            return str(e)
        return ""

    def test_empty_stack(self):
        """Чтение и запись при пустом стеке."""
        self.assertIn("пустой стек", self.fails("- read\n"))
        self.assertIn("пустой стек", self.fails("- write: 5\n"))

    def test_bad_binary(self):
        """Размер не кратен 3 и неизвестный код операции."""
        self.assertIn("не кратен", self.fails(b"\x07\x00"))
        self.assertIn("A=1", self.fails(b"\x01\x00\x00"))

    def test_too_big(self):
        """Программа больше памяти."""
        self.assertIn("не помещается", self.fails(bytes(MEMORY_SIZE + 1)))

    def test_overwritten_code(self):
        """Запись числа не из диапазона байта в ячейку кода портит команду."""
        program = "- load_const: 300\n- write: 6\n- read\n"
        self.assertIn("нет корректной команды", self.fails(program))

    def test_copy_example(self):
        """Файл-пример копирования не портит собственный код."""
        path = helpers.example("copy_array.yaml")
        with open(path, encoding="utf-8") as f:
            machine = run(f.read())
        self.assertEqual(machine.memory[200:205], machine.memory[205:210])


if __name__ == "__main__":
    unittest.main()
