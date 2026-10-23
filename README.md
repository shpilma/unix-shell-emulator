# Эмулятор командной оболочки UNIX (Вариант №25)

## Описание
Эмулятор командной строки UNIX-подобной ОС.

Поддерживает:
- Приглашение `username@hostname:~$`
- Парсер команд по пробелам
- Команды-заглушки: `ls`, `cd`
- Команду `exit`
- Параметры командной строки: `--vfs`, `--script`, `--debug`
- Запуск стартового скрипта с остановкой при первой ошибке

## Запуск

Интерактивный режим:
python src/main.py

С отладочным выводом:
python src/main.py --debug

Запуск стартового скрипта:
python src/main.py --script scripts/start_basic.txt

## Скрипты
- `scripts/start_basic.txt` — базовый набор команд
- `scripts/start_errors.txt` — остановка при ошибке
- `scripts/run_windows.bat` — тестирование параметров из cmd
- `scripts/run_linux.sh` — то же для Linux/macOS