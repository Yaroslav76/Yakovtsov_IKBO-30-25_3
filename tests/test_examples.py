"""Тесты примеров: вычитание векторов длины 10 и проверка дампов."""
import unittest

import helpers
import make_examples
from assembler import parse_program
from codec import encode_program
from machine import Machine

LENGTH = make_examples.VECTOR_LENGTH
FIRST = make_examples.FIRST_VECTOR
SECOND = make_examples.SECOND_VECTOR
ZERO = 0


def run_example(name):
    """Выполняет examples/<name>.yaml и возвращает машину."""
    with open(helpers.example(name + ".yaml"), encoding="utf-8") as f:
        program = encode_program(parse_program(f.read()))
    machine = Machine()
    machine.load(program)
    machine.run()
    return machine


class VectorTests(unittest.TestCase):
    """Поэлементное вычитание для всех трёх примеров."""

    def test_each_example(self):
        """Второй вектор равен разности, первый вектор не изменился."""
        for name, (_, first, second) in make_examples.VECTORS.items():
            memory = run_example(name).memory
            expected = [a - b for a, b in zip(first, second)]
            self.assertEqual(memory[FIRST:FIRST + LENGTH], first, name)
            self.assertEqual(memory[SECOND:SECOND + LENGTH], expected, name)

    def test_program_size(self):
        """20 записей по 2 команды и 10 вычитаний по 3 команды."""
        with open(helpers.example("vector_sub_1.yaml"),
                  encoding="utf-8") as f:
            self.assertEqual(len(parse_program(f.read())), 70)

    def test_sub_demo(self):
        """Пример вычитания этапа 4."""
        memory = run_example("sub_demo").memory
        self.assertEqual(memory[300:306], [100, 58, 42, -42, 0, 84])

    def test_negative_results_present(self):
        """Во втором примере все результаты отрицательные или нулевые."""
        memory = run_example("vector_sub_2").memory
        self.assertTrue(all(v <= ZERO for v in memory[SECOND:SECOND + LENGTH]))


if __name__ == "__main__":
    unittest.main()
