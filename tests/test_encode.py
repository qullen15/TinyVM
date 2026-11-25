"""Юнит-тесты этапа 2: кодирование команд в машинный код."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from assembler import (encode_instruction, assemble, format_bytes,
                       COMMAND_SIZE)
from main import main

INSTRUCTIONS = [
    {"a": 4, "b": 312, "c": 685},
    {"a": 0, "b": 778, "c": 797},
    {"a": 7, "b": 249, "c": 499},
    {"a": 5, "b": 333, "c": 3},
]
EXPECTED = [
    bytes([0xC4, 0x09, 0xAD, 0x02, 0x00, 0x00]),
    bytes([0x50, 0x18, 0x1D, 0x03, 0x00, 0x00]),
    bytes([0xCF, 0x07, 0xF3, 0x01, 0x00, 0x00]),
    bytes([0x6D, 0x0A, 0x03, 0x00, 0x00, 0x00]),
]
SPEC_CSV = (
    "op,b,c\n"
    "const,312,685\n"
    "load,778,797\n"
    "store,249,499\n"
    "popcnt,333,3\n"
)


class TestEncode:
    """Кодирование одной команды."""

    def test_spec_vectors(self):
        for instruction, expected in zip(INSTRUCTIONS, EXPECTED):
            assert encode_instruction(instruction) == expected

    def test_command_size(self):
        data = encode_instruction(INSTRUCTIONS[0])
        assert len(data) == COMMAND_SIZE

    def test_zero_fields(self):
        data = encode_instruction({"a": 0, "b": 0, "c": 0})
        assert data == bytes(COMMAND_SIZE)


class TestAssemble:
    """Склейка машинного кода всей программы."""

    def test_concatenation(self):
        assert assemble(INSTRUCTIONS) == b"".join(EXPECTED)

    def test_empty_program(self):
        assert assemble([]) == b""

    def test_total_size(self):
        code = assemble(INSTRUCTIONS)
        assert len(code) == COMMAND_SIZE * len(INSTRUCTIONS)


class TestFormatBytes:
    """Форматирование байтов как в спецификации."""

    def test_format(self):
        text = format_bytes(EXPECTED[0])
        assert text == "0xC4, 0x09, 0xAD, 0x02, 0x00, 0x00"


class TestMain:
    """Точка входа: запись файла и вывод."""

    def test_writes_file(self, tmp_path, capsys, monkeypatch):
        source = tmp_path / "spec.csv"
        source.write_text(SPEC_CSV, encoding="utf-8")
        target = tmp_path / "out" / "spec.bin"
        monkeypatch.setattr(sys, "argv", [
            "main.py", "--source", str(source), "--output", str(target)])
        with pytest.raises(SystemExit) as exc:
            main()
        out = capsys.readouterr().out
        assert exc.value.code == 0
        assert target.read_bytes() == b"".join(EXPECTED)
        assert "байт" in out

    def test_test_mode_shows_bytes(self, tmp_path, capsys, monkeypatch):
        source = tmp_path / "spec.csv"
        source.write_text(SPEC_CSV, encoding="utf-8")
        monkeypatch.setattr(sys, "argv", [
            "main.py", "--source", str(source),
            "--output", str(tmp_path / "spec.bin"), "--test-mode"])
        with pytest.raises(SystemExit) as exc:
            main()
        out = capsys.readouterr().out
        assert exc.value.code == 0
        assert "0xC4, 0x09, 0xAD, 0x02, 0x00, 0x00" in out