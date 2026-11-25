@echo off
chcp 65001 >nul
echo === 1. Тесты из спецификации: поля и байты ===
py src/main.py --source programs/spec.csv --output out/spec.bin --test-mode
echo Код: %ERRORLEVEL%
echo === 2. Обычный режим: размер файла ===
py src/main.py --source programs/spec.csv --output out/spec.bin
echo Код: %ERRORLEVEL%
echo === 3. Пустая программа ===
py src/main.py --source programs/empty.csv --output out/empty.bin
echo Код: %ERRORLEVEL%
echo === 4. Ошибка: неизвестная команда ===
py src/main.py --source programs/bad_op.csv --output out/x.bin
echo Код: %ERRORLEVEL%