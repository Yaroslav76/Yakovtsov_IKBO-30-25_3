"""Преобразование команд УВМ в машинный код и обратно."""
from ir import Instruction
from spec import BY_OPCODE, COMMAND_SIZE, OPCODE_MASK, OPERAND_SHIFT

BYTE_ORDER = "little"


class CodecError(Exception):
    """Недопустимый машинный код."""


def encode(instruction):
    """Команда -> 3 байта: поле A в битах 0-6, поле B начиная с бита 7."""
    word = instruction.a | ((instruction.b or 0) << OPERAND_SHIFT)
    return word.to_bytes(COMMAND_SIZE, BYTE_ORDER)


def encode_program(program):
    """Программа (список Instruction) -> двоичный код."""
    return b"".join(encode(instruction) for instruction in program)


def decode(data):
    """3 байта -> команда во внутреннем представлении."""
    word = int.from_bytes(data, BYTE_ORDER)
    opcode = word & OPCODE_MASK
    spec = BY_OPCODE.get(opcode)
    if spec is None:
        raise CodecError(f"неизвестный код операции A={opcode}")
    if not spec.operand_bits:
        return Instruction(spec.name, opcode)
    operand = (word >> OPERAND_SHIFT) & spec.max_operand()
    return Instruction(spec.name, opcode, operand)


def format_bytes(data):
    """Байты в формате спецификации: '0xBF, 0x1E, 0x00'."""
    return ", ".join(f"0x{byte:02X}" for byte in data)
