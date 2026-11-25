"""Язык ассемблера TinyVM и трансляция в промежуточное представление."""

import csv

OPCODES = {"const": 4, "load": 0, "store": 7, "popcnt": 5}
FIELDS = ["op", "b", "c"]
B_BITS = 13
CONST_BITS = 29
B_LIMIT = 2 ** B_BITS
CONST_LIMIT = 2 ** CONST_BITS


def parse_number(text):
    """Преобразует текст в число; (число, None) или (None, ошибка)."""
    try:
        return int(text), None
    except (TypeError, ValueError):
        return None, f"ожидалось целое число, получено: {text!r}"


def check_range(name, value, limit):
    """Проверяет, что значение помещается в поле команды."""
    if value < 0 or value >= limit:
        return f"значение {name}={value} вне диапазона 0..{limit - 1}"
    return None


def make_instruction(op, b_text, c_text):
    """Собирает команду из полей CSV; (словарь, None) или (None, ошибка)."""
    if op not in OPCODES:
        return None, f"неизвестная команда: {op}"
    b, error = parse_number(b_text)
    if error is not None:
        return None, f"поле b: {error}"
    c, error = parse_number(c_text)
    if error is not None:
        return None, f"поле c: {error}"
    error = check_range("b", b, B_LIMIT)
    if error is not None:
        return None, error
    c_limit = CONST_LIMIT if op == "const" else B_LIMIT
    error = check_range("c", c, c_limit)
    if error is not None:
        return None, error
    return {"a": OPCODES[op], "b": b, "c": c}, None


def parse_program(text):
    """Транслирует CSV-текст в список команд; (список, None) или (None, ошибка)."""
    reader = csv.DictReader(text.splitlines())
    if reader.fieldnames != FIELDS:
        return None, f"ожидался заголовок {','.join(FIELDS)}"
    program = []
    for row in reader:
        if row.get(None) is not None:
            return None, f"строка {reader.line_num}: лишние поля"
        instruction, error = make_instruction(
            row["op"], row["b"], row["c"])
        if error is not None:
            return None, f"строка {reader.line_num}: {error}"
        program.append(instruction)
    return program, None


def format_instruction(instruction):
    """Форматирует команду как в тестах спецификации УВМ."""
    return (f"A={instruction['a']}, "
            f"B={instruction['b']}, C={instruction['c']}")