"""TinyVM: ассемблер и интерпретатор учебной виртуальной машины."""

import argparse
import sys

from assembler import parse_program, format_instruction


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
                        help="режим тестирования: вывод промежуточного кода")
    return parser


def read_source(path):
    """Читает исходный текст; (текст, None) или (None, ошибка)."""
    try:
        with open(path, encoding="utf-8") as source:
            return source.read(), None
    except OSError as exc:
        return None, f"не удалось прочитать исходный файл: {exc}"


def print_program(program):
    """Печатает промежуточное представление программы."""
    for instruction in program:
        print(format_instruction(instruction))


def main():
    """Точка входа: параметры, чтение, трансляция, вывод."""
    args = build_parser().parse_args()
    text, error = read_source(args.source)
    if error is not None:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise SystemExit(1)
    program, error = parse_program(text)
    if error is not None:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise SystemExit(1)
    if args.test_mode:
        print_program(program)
    else:
        print(f"Разобрано команд: {len(program)}")
    raise SystemExit(0)


if __name__ == "__main__":
    main()