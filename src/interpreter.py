"""CLI интерпретатора TinyVM: исполнение кода и дамп памяти."""

import argparse
import os
import sys

from assembler import COMMAND_SIZE
from vm import (new_memory, run_program, check_bounds, dump_xml,
                MEMORY_SIZE)


def build_parser():
    """Создаёт парсер параметров интерпретатора."""
    parser = argparse.ArgumentParser(
        prog="tinyvm-vm",
        description="Интерпретатор учебной виртуальной машины.",
    )
    parser.add_argument("--binary", required=True, metavar="PATH",
                        help="путь к двоичному файлу с программой")
    parser.add_argument("--dump", required=True, metavar="PATH",
                        help="путь к файлу дампа памяти (XML)")
    parser.add_argument("--start", type=int, required=True,
                        metavar="ADDR", help="начальный адрес дампа")
    parser.add_argument("--end", type=int, required=True,
                        metavar="ADDR", help="конечный адрес дампа")
    return parser


def read_binary(path):
    """Читает машинный код; (байты, None) или (None, ошибка)."""
    try:
        with open(path, "rb") as source:
            return source.read(), None
    except OSError as exc:
        return None, f"не удалось прочитать программу: {exc}"


def write_text(path, text):
    """Записывает текстовый файл; возвращает ошибку или None."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as target:
            target.write(text)
    except OSError as exc:
        return f"не удалось записать дамп: {exc}"
    return None


def main():
    """Точка входа: чтение кода, исполнение, сохранение дампа."""
    args = build_parser().parse_args()
    error = check_bounds(args.start, args.end, MEMORY_SIZE)
    if error is not None:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise SystemExit(1)
    code, error = read_binary(args.binary)
    if error is not None:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise SystemExit(1)
    memory = new_memory()
    error = run_program(code, memory)
    if error is not None:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise SystemExit(1)
    error = write_text(args.dump, dump_xml(memory, args.start, args.end))
    if error is not None:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Выполнено команд: {len(code) // COMMAND_SIZE}")
    print(f"Дамп памяти сохранён: {args.dump}")
    raise SystemExit(0)


if __name__ == "__main__":
    main()