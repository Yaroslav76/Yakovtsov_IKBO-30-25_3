"""Модель УВМ: общая память команд и данных, стек, выполнение команд."""
from codec import CodecError, decode
from spec import ADDRESS_BITS, COMMAND_SIZE

MEMORY_SIZE = 1 << ADDRESS_BITS
CELL_BITS = 32
CELL_MASK = (1 << CELL_BITS) - 1
SIGN_BIT = 1 << (CELL_BITS - 1)
BYTE_MAX = 255


class MachineError(Exception):
    """Ошибка выполнения программы на УВМ."""


def wrap(value):
    """Значение ячейки: 32-битное целое со знаком."""
    value &= CELL_MASK
    return value - (1 << CELL_BITS) if value >= SIGN_BIT else value


class Machine:
    """УВМ: одна память для команд и данных и стек значений.

    Двоичная программа загружается с адреса 0, по одному байту в ячейку;
    остальные ячейки свободны для данных. Команды выбираются из той же
    памяти, поэтому запись по адресам программы меняет сами команды.
    """

    def __init__(self):
        """Создаёт машину с нулевой памятью и пустым стеком."""
        self.memory = [0] * MEMORY_SIZE
        self.stack = []
        self.pc = 0
        self.size = 0
        self.handlers = {
            "load_const": self.load_const,
            "read": self.read,
            "write": self.write,
            "sub": self.sub,
        }

    def load(self, program):
        """Загружает двоичную программу в начало памяти."""
        if len(program) % COMMAND_SIZE:
            raise MachineError(
                f"размер программы {len(program)} не кратен {COMMAND_SIZE}")
        if len(program) > MEMORY_SIZE:
            raise MachineError("программа не помещается в память")
        self.memory[:len(program)] = list(program)
        self.size = len(program)

    def push(self, value):
        """Кладёт значение на стек."""
        self.stack.append(value)

    def pop(self):
        """Снимает значение со стека."""
        if not self.stack:
            raise MachineError(f"пустой стек (команда по адресу {self.pc})")
        return self.stack.pop()

    def cell(self, address):
        """Значение ячейки памяти; адрес проверяется."""
        self.check_address(address)
        return self.memory[address]

    def check_address(self, address):
        """Проверяет, что адрес лежит в памяти."""
        if address not in range(MEMORY_SIZE):
            raise MachineError(
                f"адрес {address} вне памяти 0..{MEMORY_SIZE - 1} "
                f"(команда по адресу {self.pc})")

    def fetch(self):
        """Читает из памяти и декодирует команду по адресу pc."""
        cells = self.memory[self.pc:self.pc + COMMAND_SIZE]
        if len(cells) < COMMAND_SIZE or any(
                value not in range(BYTE_MAX + 1) for value in cells):
            raise MachineError(
                f"по адресу {self.pc} нет корректной команды "
                "(код испорчен записью в память?)")
        try:
            return decode(bytes(cells))
        except CodecError as e:
            raise MachineError(f"адрес {self.pc}: {e}")

    def load_const(self, instruction):
        """Загрузка константы: B кладётся на стек."""
        self.push(instruction.b)

    def read(self, instruction):
        """Чтение: адрес снимается со стека, значение кладётся на стек."""
        self.push(self.cell(self.pop()))

    def write(self, instruction):
        """Запись: значение снимается со стека, пишется по адресу B."""
        value = self.pop()
        self.check_address(instruction.b)
        self.memory[instruction.b] = wrap(value)

    def sub(self, instruction):
        """Вычитание: память[B] - память[снятый со стека адрес] -> стек."""
        address = self.pop()
        first = self.cell(instruction.b)
        second = self.cell(address)
        self.push(wrap(first - second))

    def step(self):
        """Выполняет одну команду и сдвигает pc."""
        instruction = self.fetch()
        handler = self.handlers.get(instruction.name)
        if handler is None:
            raise MachineError(
                f"команда {instruction.name} (адрес {self.pc}) "
                "не поддерживается")
        handler(instruction)
        self.pc += COMMAND_SIZE

    def run(self):
        """Выполняет программу до конца; возвращает число команд."""
        count = 0
        while self.pc < self.size:
            self.step()
            count += 1
        return count

    def dump(self, start, end):
        """Дамп памяти start..end (включительно) как словарь для JSON."""
        return {
            "range": [start, end],
            "memory": {str(a): self.memory[a] for a in range(start, end + 1)},
        }
