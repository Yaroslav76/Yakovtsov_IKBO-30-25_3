"""Общие вспомогательные средства для модульных тестов."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
EXAMPLES = os.path.join(ROOT, "examples")
EXPECTED = os.path.join(ROOT, "tests", "expected")


def example(*parts):
    """Путь к файлу в каталоге examples."""
    return os.path.join(EXAMPLES, *parts)
