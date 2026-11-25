"""Интерпретатор учебной ВМ: декодирование, память, исполнение."""

import xml.etree.ElementTree as ET

from assembler import (COMMAND_SIZE, B_SHIFT, C_SHIFT, OPCODES,
                       B_LIMIT, CONST_LIMIT)

A_MASK = 0b111
B_MASK = B_LIMIT - 1
CONST_MASK = CONST_LIMIT - 1
MEMORY_SIZE = B_LIMIT
NAMES = {code: name for name, code in OPCODES.items()}


def decode_instruction(data):
    """Декодирует 6 байт в поля; (словарь, None) или (None, ошибка)."""
    if len(data) != COMMAND_SIZE:
        return None, f"ожидалось {COMMAND_SIZE} байт, получено {len(data)}"
    value = int.from_bytes(data, "little")
    a = value & A_MASK
    if a not in NAMES:
        return None, f"неизвестный код операции: {a}"
    b = (value >> B_SHIFT) & B_MASK
    mask = CONST_MASK if a == OPCODES["const"] else B_MASK
    c = (value >> C_SHIFT) & mask
    return {"a": a, "b": b, "c": c}, None


def new_memory():
    """Создаёт память данных, заполненную нулями."""
    return [0] * MEMORY_SIZE


def read_cell(memory, address):
    """Читает ячейку памяти; (значение, None) или (None, ошибка)."""
    if address < 0 or address >= len(memory):
        return None, f"адрес вне памяти: {address}"
    return memory[address], None


def write_cell(memory, address, value):
    """Записывает ячейку памяти; возвращает ошибку или None."""
    if address < 0 or address >= len(memory):
        return f"адрес вне памяти: {address}"
    memory[address] = value
    return None


def do_const(memory, b, c):
    """mem[b] = c — загрузка константы."""
    return write_cell(memory, b, c)


def do_load(memory, b, c):
    """mem[c] = mem[mem[b]] — чтение через указатель."""
    pointer, error = read_cell(memory, b)
    if error is not None:
        return error
    value, error = read_cell(memory, pointer)
    if error is not None:
        return error
    return write_cell(memory, c, value)


def do_store(memory, b, c):
    """mem[mem[c]] = mem[b] — запись через указатель."""
    value, error = read_cell(memory, b)
    if error is not None:
        return error
    pointer, error = read_cell(memory, c)
    if error is not None:
        return error
    return write_cell(memory, pointer, value)


def popcount(value):
    """Считает число единиц в двоичной записи числа."""
    return bin(value).count("1")


def do_popcnt(memory, b, c):
    """mem[mem[c]] = popcount(mem[b]) — число единиц."""
    value, error = read_cell(memory, b)
    if error is not None:
        return error
    pointer, error = read_cell(memory, c)
    if error is not None:
        return error
    return write_cell(memory, pointer, popcount(value))


HANDLERS = {
    OPCODES["const"]: do_const,
    OPCODES["load"]: do_load,
    OPCODES["store"]: do_store,
    OPCODES["popcnt"]: do_popcnt,
}


def execute(instruction, memory):
    """Выполняет команду над памятью; возвращает ошибку или None."""
    handler = HANDLERS.get(instruction["a"])
    if handler is None:
        return f"команда не реализована: {NAMES.get(instruction['a'])}"
    return handler(memory, instruction["b"], instruction["c"])


def run_program(code, memory):
    """Цикл интерпретации: чтение, декодирование, выполнение."""
    for offset in range(0, len(code), COMMAND_SIZE):
        instruction, error = decode_instruction(
            code[offset:offset + COMMAND_SIZE])
        if error is not None:
            return f"смещение {offset}: {error}"
        error = execute(instruction, memory)
        if error is not None:
            return f"смещение {offset}: {error}"
    return None


def check_bounds(start, end, size):
    """Проверяет диапазон адресов дампа; возвращает ошибку или None."""
    if start < 0 or end < start or end >= size:
        return f"некорректный диапазон адресов: {start}..{end}"
    return None


def dump_xml(memory, start, end):
    """Формирует XML-дамп памяти в диапазоне адресов."""
    root = ET.Element("memory", start=str(start), end=str(end))
    for address in range(start, end + 1):
        cell = ET.SubElement(root, "cell", address=str(address))
        cell.text = str(memory[address])
    ET.indent(root)
    return ET.tostring(root, encoding="unicode")