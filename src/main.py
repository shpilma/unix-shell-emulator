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
    def __init__(self):
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

    def run(self) -> None:
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


def main():
    shell = Shell()
    shell.run()


if __name__ == "__main__":
    main()