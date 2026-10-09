import argparse
import os
import sys


class CommandError(Exception):
    """Ошибка выполнения команды."""


def cmd_ls(args: list) -> str:
    """Заглушка ls: выводит имя команды и аргументы."""
    if args:
        return "ls - " + " ".join(args)
    return "ls"


def cmd_cd(args: list) -> str:
    """Заглушка cd: выводит имя команды и аргументы."""
    if args:
        return "cd - " + " ".join(args)
    return "cd"


class Shell:
    def __init__(self, vfs_path: str = None, debug: bool = False):
        self.vfs_path = vfs_path
        self.debug = debug
        self.running = True
        self.commands = {
            "ls": cmd_ls,
            "cd": cmd_cd,
        }

    def get_prompt(self) -> str:
        user = os.getenv("USER", "user")
        host = os.uname().nodename if hasattr(os, "uname") else "host"
        return f"{user}@{host}:~$ "

    def execute_line(self, line: str) -> str:
        line = line.strip()
        if not line:
            return ""
        parts = line.split()
        if not parts:
            return ""
        cmd_name = parts[0]
        args = parts[1:]

        if cmd_name == "exit":
            self.running = False
            return "Выход."

        if cmd_name not in self.commands:
            raise CommandError(f"{cmd_name}: команда не найдена")

        return self.commands[cmd_name](args)

    def run_repl(self) -> None:
        """Интерактивный цикл REPL."""
        while self.running:
            try:
                line = input(self.get_prompt())
            except (EOFError, KeyboardInterrupt):
                print()
                break
            try:
                output = self.execute_line(line)
                if output:
                    print(output)
            except CommandError as e:
                print(f"Ошибка: {e}", file=sys.stderr)

    def run_script(self, script_path: str) -> None:
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Скрипт не найден: {script_path}", file=sys.stderr)
            sys.exit(1)

        for i, line in enumerate(lines, 1):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            # имитация диалога: приглашение + введённая строка
            print(f"{self.get_prompt()}{line}")
            try:
                output = self.execute_line(line)
                if output:
                    print(output)
            except CommandError as e:
                print(f"Ошибка в строке {i}: {e}", file=sys.stderr)
                print("Скрипт остановлен из-за ошибки.", file=sys.stderr)
                sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Эмулятор командной оболочки UNIX"
    )
    parser.add_argument(
        "--vfs", help="Путь к физическому расположению VFS"
    )
    parser.add_argument(
        "--script", help="Путь к стартовому скрипту"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Отладочный вывод"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.debug:
        print("=== Параметры эмулятора ===")
        print(f"VFS: {args.vfs or 'не указан'}")
        print(f"Стартовый скрипт: {args.script or 'не указан'}")
        print(f"Отладка: {args.debug}")
        print("===========================")

    shell = Shell(vfs_path=args.vfs, debug=args.debug)

    if args.script:
        shell.run_script(args.script)
    else:
        shell.run_repl()


if __name__ == "__main__":
    main()