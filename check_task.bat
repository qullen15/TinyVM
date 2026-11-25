@echo off
chcp 65001 >nul
echo === 1. Тестовая задача: вектор 5, результат на месте ===
py src/main.py --source programs/task.csv --output out/task.bin
py src/interpreter.py --binary out/task.bin --dump out/task.xml --start 100 --end 104
echo Код: %ERRORLEVEL%
echo === 2. Пример 1: степени двойки ===
py src/main.py --source programs/example1.csv --output out/ex1.bin
py src/interpreter.py --binary out/ex1.bin --dump out/ex1.xml --start 100 --end 104
echo Код: %ERRORLEVEL%
echo === 3. Пример 2: числа из сплошных единиц ===
py src/main.py --source programs/example2.csv --output out/ex2.bin
py src/interpreter.py --binary out/ex2.bin --dump out/ex2.xml --start 100 --end 104
echo Код: %ERRORLEVEL%
echo === 4. Пример 3: результат в новый вектор ===
py src/main.py --source programs/example3.csv --output out/ex3.bin
py src/interpreter.py --binary out/ex3.bin --dump out/ex3.xml --start 200 --end 202
echo Код: %ERRORLEVEL%
echo === 5. Дамп тестовой задачи ===
type out\task.xml