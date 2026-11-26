"""Спецификация УВМ: команды, коды операций и размеры полей."""
from dataclasses import dataclass

COMMAND_SIZE = 3
OPCODE_BITS = 7
OPCODE_MASK = (1 << OPCODE_BITS) - 1
OPERAND_SHIFT = OPCODE_BITS
ADDRESS_BITS = 13
CONSTANT_BITS = 10


@dataclass(frozen=True)
class CommandSpec:
    """Описание команды: имя, код операции (поле A) и размер поля B."""

    name: str
    opcode: int
    operand_bits: int

    def max_operand(self):
        """Наибольшее допустимое значение поля B."""
        return (1 << self.operand_bits) - 1


COMMANDS = (
    CommandSpec("load_const", 63, CONSTANT_BITS),
    CommandSpec("read", 7, 0),
    CommandSpec("write", 3, ADDRESS_BITS),
    CommandSpec("sub", 44, ADDRESS_BITS),
)
BY_NAME = {spec.name: spec for spec in COMMANDS}
BY_OPCODE = {spec.opcode: spec for spec in COMMANDS}
