"""TinyVM: ассемблер и интерпретатор учебной виртуальной машины."""

import argparse
import os
import sys

from assembler import (parse_program, assemble, encode_instruction,
                       format_instruction, format_bytes)


def build_parser():
    """Создаёт парсер параметров командной строки."""
    parser = argparse.ArgumentParser(
        prog="tinyvm",
        description="Ассемблер и интерпретатор учебной ВМ.",
    )
    parser.add_argument("--source", required=True, metavar="PATH",
                        help="путь к исходному файлу с текстом программы")
    parser.add_argument("--output", required=True, metavar="PATH",
                        help="путь к двоичному файлу-результату")
    parser.add_argument("--test-mode", action="store_true",
                        help="режим тестирования: вывод полей и байтов")
    return parser


def read_source(path):
    """Читает исходный текст; (текст, None) или (None, ошибка)."""
    try:
        with open(path, encoding="utf-8") as source:
            return source.read(), None
    except OSError as exc:
        return None, f"не удалось прочитать исходный файл: {exc}"


def write_binary(path, data):
    """Записывает машинный код в файл; возвращает ошибку или None."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    try:
        with open(path, "wb") as target:
            target.write(data)
    except OSError as exc:
        return f"не удалось записать файл: {exc}"
    return None


def print_code(program):
    """Печатает поля и байты каждой команды как в тестах спецификации."""
    for instruction in program:
        data = encode_instruction(instruction)
        print(f"{format_instruction(instruction)}: {format_bytes(data)}")


def main():
    """Точка входа: параметры, трансляция, запись и вывод результата."""
    args = build_parser().parse_args()
    text, error = read_source(args.source)
    if error is not None:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise SystemExit(1)
    program, error = parse_program(text)
    if error is not None:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise SystemExit(1)
    code = assemble(program)
    error = write_binary(args.output, code)
    if error is not None:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise SystemExit(1)
    if args.test_mode:
        print_code(program)
    print(f"Размер двоичного файла: {len(code)} байт")
    raise SystemExit(0)


if __name__ == "__main__":
    main()