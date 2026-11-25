@echo off
chcp 65001 >nul
echo === 1. Ассемблирование программы копирования ===
py src/main.py --source programs/copy.csv --output out/copy.bin
echo Код: %ERRORLEVEL%
echo === 2. Исполнение и дамп приёмника ===
py src/interpreter.py --binary out/copy.bin --dump out/copy.xml --start 200 --end 202
echo Код: %ERRORLEVEL%
echo === 3. Дамп источника ===
py src/interpreter.py --binary out/copy.bin --dump out/src.xml --start 100 --end 102
echo Код: %ERRORLEVEL%
echo === 4. Ошибка: popcnt ещё не реализован ===
py src/main.py --source programs/spec.csv --output out/spec.bin
py src/interpreter.py --binary out/spec.bin --dump out/x.xml --start 0 --end 5
echo Код: %ERRORLEVEL%
echo === 5. Ошибка: неверный диапазон ===
py src/interpreter.py --binary out/copy.bin --dump out/x.xml --start 10 --end 5
echo Код: %ERRORLEVEL%
echo === 6. Ошибка: файл не найден ===
py src/interpreter.py --binary out/nope.bin --dump out/x.xml --start 0 --end 5
echo Код: %ERRORLEVEL%