@echo off
chcp 65001 >nul
echo === 1. Ассемблирование программы popcnt ===
py src/main.py --source programs/popcnt.csv --output out/popcnt.bin
echo Код: %ERRORLEVEL%
echo === 2. Дамп результатов вычислений ===
py src/interpreter.py --binary out/popcnt.bin --dump out/popcnt.xml --start 200 --end 202
echo Код: %ERRORLEVEL%
echo === 3. Дамп исходных данных ===
py src/interpreter.py --binary out/popcnt.bin --dump out/popcnt_src.xml --start 100 --end 102
echo Код: %ERRORLEVEL%
echo === 4. Программа из спецификации теперь исполняется полностью ===
py src/main.py --source programs/spec.csv --output out/spec.bin
py src/interpreter.py --binary out/spec.bin --dump out/spec.xml --start 0 --end 5
echo Код: %ERRORLEVEL%