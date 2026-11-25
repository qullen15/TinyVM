"""Юнит-тесты этапа 1: разбор CSV-программы в промежуточный код."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from assembler import (parse_program, make_instruction, check_range,
                       format_instruction, B_LIMIT, CONST_LIMIT)
from main import main

SPEC = (
    "op,b,c\n"
    "const,312,685\n"
    "load,778,797\n"
    "store,249,499\n"
    "popcnt,333,3\n"
)
EXPECTED = [
    {"a": 4, "b": 312, "c": 685},
    {"a": 0, "b": 778, "c": 797},
    {"a": 7, "b": 249, "c": 499},
    {"a": 5, "b": 333, "c": 3},
]
USAGE_ERROR = 2


class TestParseProgram:
    """Трансляция CSV-текста в промежуточное представление."""

    def test_spec_vectors(self):
        program, error = parse_program(SPEC)
        assert error is None
        assert program == EXPECTED

    def test_empty_program(self):
        program, error = parse_program("op,b,c\n")
        assert error is None
        assert program == []

    def test_bad_header(self):
        program, error = parse_program("cmd,x,y\nconst,1,2\n")
        assert program is None
        assert "заголовок" in error

    def test_unknown_op(self):
        program, error = parse_program("op,b,c\njump,1,2\n")
        assert program is None
        assert "неизвестная команда" in error

    def test_not_number(self):
        program, error = parse_program("op,b,c\nconst,abc,2\n")
        assert program is None
        assert "целое число" in error

    def test_extra_fields(self):
        program, error = parse_program("op,b,c\nconst,1,2,3\n")
        assert program is None
        assert "лишние поля" in error


class TestRanges:
    """Проверка диапазонов полей команды."""

    def test_b_limit(self):
        assert check_range("b", B_LIMIT - 1, B_LIMIT) is None
        assert check_range("b", B_LIMIT, B_LIMIT) is not None

    def test_negative(self):
        assert check_range("b", -1, B_LIMIT) is not None

    def test_const_wide_field(self):
        result, error = make_instruction("const", "1", str(CONST_LIMIT - 1))
        assert error is None
        assert result["c"] == CONST_LIMIT - 1

    def test_load_narrow_field(self):
        result, error = make_instruction("load", "1", str(CONST_LIMIT - 1))
        assert result is None
        assert "вне диапазона" in error


class TestFormat:
    """Форматирование как в спецификации УВМ."""

    def test_format(self):
        text = format_instruction({"a": 4, "b": 312, "c": 685})
        assert text == "A=4, B=312, C=685"


class TestMain:
    """Точка входа: тест-режим и ошибки."""

    def test_test_mode(self, tmp_path, capsys, monkeypatch):
        source = tmp_path / "spec.csv"
        source.write_text(SPEC, encoding="utf-8")
        monkeypatch.setattr(sys, "argv", [
            "main.py", "--source", str(source),
            "--output", str(tmp_path / "out.bin"), "--test-mode"])
        with pytest.raises(SystemExit) as exc:
            main()
        out = capsys.readouterr().out
        assert exc.value.code == 0
        assert "A=4, B=312, C=685" in out

    def test_missing_source(self, tmp_path, capsys, monkeypatch):
        monkeypatch.setattr(sys, "argv", [
            "main.py", "--source", str(tmp_path / "nope.csv"),
            "--output", str(tmp_path / "out.bin"), "--test-mode"])
        with pytest.raises(SystemExit) as exc:
            main()
        err = capsys.readouterr().err
        assert exc.value.code == 1
        assert "не удалось прочитать" in err

    def test_missing_required(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["main.py"])
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == USAGE_ERROR