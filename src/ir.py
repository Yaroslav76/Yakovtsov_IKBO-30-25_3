"""Внутреннее представление команды УВМ (поля A и B)."""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Instruction:
    """Команда: имя, код операции A и операнд B (если он есть)."""

    name: str
    a: int
    b: Optional[int] = None

    def fields(self):
        """Поля и значения в формате спецификации, например 'A=63, B=61'."""
        if self.b is None:
            return f"A={self.a}"
        return f"A={self.a}, B={self.b}"
