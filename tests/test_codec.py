"""Модульные тесты перевода команд в машинный код."""
import unittest

import helpers
from src.assembler import parse_program
from src.codec import encode, encode_program, format_bytes
from src.ir import Instruction

SPEC_BYTES = [
    (Instruction("load_const", 63, 61), "0xBF, 0x1E, 0x00"),
    (Instruction("read", 7), "0x07, 0x00, 0x00"),
    (Instruction("write", 3, 629), "0x83, 0x3A, 0x01"),
    (Instruction("sub", 44, 975), "0xAC, 0xE7, 0x01"),
]


class EncodeTests(unittest.TestCase):
    """Тесты из спецификации УВМ."""

    def test_spec_bytes(self):
        """Каждая команда даёт байты из спецификации."""
        for instruction, expected in SPEC_BYTES:
            data = encode(instruction)
            self.assertEqual(format_bytes(data), expected)

    def test_size(self):
        """Каждая команда занимает 3 байта."""
        for instruction, _ in SPEC_BYTES:
            self.assertEqual(len(encode(instruction)), 3)

    def test_program(self):
        """Программа кодируется подряд, без разделителей."""
        program = [instruction for instruction, _ in SPEC_BYTES]
        self.assertEqual(len(encode_program(program)), 12)

    def test_field_boundaries(self):
        """Границы полей: наибольшая константа и наибольший адрес."""
        top_const = encode(Instruction("load_const", 63, 1023))
        top_address = encode(Instruction("write", 3, 8191))
        self.assertEqual(format_bytes(top_const), "0xBF, 0xFF, 0x01")
        self.assertEqual(format_bytes(top_address), "0x83, 0xFF, 0x0F")

    def test_example_file(self):
        """Файл spec_tests.yaml даёт все тестовые последовательности."""
        with open(helpers.example("spec_tests.yaml"), encoding="utf-8") as f:
            program = parse_program(f.read())
        got = [format_bytes(encode(item)) for item in program]
        self.assertEqual(got, [expected for _, expected in SPEC_BYTES])


if __name__ == "__main__":
    unittest.main()
