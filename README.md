# Эмулятор командной оболочки UNIX (Вариант №25)

## Описание
Эмулятор командной строки UNIX-подобной ОС.

## Параметры командной строки
- `--vfs PATH` — путь к XML-файлу VFS
- `--script PATH` — путь к стартовому скрипту
- `--debug` — отладочный вывод

## Команды
- `ls` — вывод содержимого (заглушка)
- `cd` — смена директории (заглушка)
- `vfs-save PATH` — сохранение VFS в XML
- `exit` — выход

## Примеры VFS
- `scripts/vfs_examples/minimal.xml` — минимальный
- `scripts/vfs_examples/several_files.xml` — несколько файлов
- `scripts/vfs_examples/deep_tree.xml` — глубокая иерархия

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