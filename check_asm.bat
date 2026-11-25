@echo off
chcp 65001 >nul
echo === 1. Тесты из спецификации ===
py src/main.py --source programs/spec.csv --output out/spec.bin --test-mode
echo Код: %ERRORLEVEL%
echo === 2. Обычный режим ===
py src/main.py --source programs/spec.csv --output out/spec.bin
echo Код: %ERRORLEVEL%
echo === 3. Ошибка: неизвестная команда ===
py src/main.py --source programs/bad_op.csv --output out/x.bin --test-mode
echo Код: %ERRORLEVEL%
echo === 4. Ошибка: значение вне диапазона ===
py src/main.py --source programs/bad_range.csv --output out/x.bin --test-mode
echo Код: %ERRORLEVEL%
echo === 5. Ошибка: неверный заголовок ===
py src/main.py --source programs/bad_header.csv --output out/x.bin --test-mode
echo Код: %ERRORLEVEL%
echo === 6. Ошибка: файл не найден ===
py src/main.py --source programs/nope.csv --output out/x.bin --test-mode
echo Код: %ERRORLEVEL%