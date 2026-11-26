"""Генератор примеров программ УВМ (файлы examples/*.yaml).

Запуск: python3 tests/make_examples.py
"""
import os

import helpers


def init_array(base, values):
    """Команды, записывающие значения в память начиная с адреса base."""
    commands = []
    for offset, value in enumerate(values):
        commands += [f"- load_const: {value}", f"- write: {base + offset}"]
    return commands


def copy_array(source, target, length):
    """Команды копирования length ячеек с адреса source на адрес target."""
    commands = []
    for offset in range(length):
        commands += [f"- load_const: {source + offset}", "- read",
                     f"- write: {target + offset}"]
    return commands


def save(name, title, commands):
    """Записывает программу в examples/<name>.yaml с заголовком-описанием."""
    lines = [f"# {line}" for line in title] + commands
    path = helpers.example(name + ".yaml")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"создан {os.path.relpath(path, helpers.ROOT)}")


def make_copy_array():
    """Этап 3: копирование массива из 5 элементов с адреса 200 на 205."""
    values = [11, 22, 33, 44, 55]
    title = ["Копирование массива: ячейки 200..204 -> 205..209",
             "Сначала массив записывается в память командами load_const и",
             "write, затем каждый элемент копируется: адрес -> read -> write."]
    commands = init_array(200, values) + copy_array(200, 205, len(values))
    save("copy_array", title, commands)


def subtract(first, second, target):
    """Команды: память[first] - память[second] -> память[target]."""
    return [f"- load_const: {second}", f"- sub: {first}",
            f"- write: {target}"]


def make_sub_demo():
    """Этап 4: вычитание с сохранением результатов в память 302..305."""
    title = ["Вычитание: ячейки 300 и 301 содержат 100 и 58",
             "302 = 300 - 301 = 42; 303 = 301 - 300 = -42;",
             "304 = 300 - 300 = 0; 305 = 302 - 303 = 84"]
    commands = init_array(300, [100, 58])
    commands += subtract(300, 301, 302) + subtract(301, 300, 303)
    commands += subtract(300, 300, 304) + subtract(302, 303, 305)
    save("sub_demo", title, commands)


VECTOR_LENGTH = 10
FIRST_VECTOR = 400
SECOND_VECTOR = 410
VECTORS = {
    "vector_sub_1": ("положительные разности",
                     [90, 80, 70, 60, 50, 40, 30, 20, 10, 100],
                     [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
    "vector_sub_2": ("отрицательные разности",
                     [5, 4, 3, 2, 1, 0, 7, 8, 9, 6],
                     [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]),
    "vector_sub_3": ("нули, равные элементы и граничные значения",
                     [0, 1023, 500, 512, 1, 0, 1023, 255, 256, 1000],
                     [0, 0, 500, 513, 1023, 1023, 1023, 1, 255, 999]),
}


def vector_sub(first_base, second_base, length):
    """Поэлементное вычитание: вторая[i] = первая[i] - вторая[i]."""
    commands = []
    for offset in range(length):
        commands += subtract(first_base + offset, second_base + offset,
                             second_base + offset)
    return commands


def make_vector_sub(name, kind, first, second):
    """Этап 5: вычитание векторов длины 10 (данные first и second)."""
    title = [f"Вектор1[400..409] - Вектор2[410..419]: {kind}",
             "Результат записывается во второй вектор (ячейки 410..419).",
             f"Вектор1 = {first}",
             f"Вектор2 = {second}"]
    commands = init_array(FIRST_VECTOR, first)
    commands += init_array(SECOND_VECTOR, second)
    commands += vector_sub(FIRST_VECTOR, SECOND_VECTOR, VECTOR_LENGTH)
    save(name, title, commands)


def main():
    """Создаёт все примеры."""
    make_copy_array()
    make_sub_demo()
    for name, (kind, first, second) in VECTORS.items():
        make_vector_sub(name, kind, first, second)


if __name__ == "__main__":
    main()
