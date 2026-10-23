"""Эмулятор командной оболочки UNIX. Этап 4: Основные команды."""
import argparse
import os
import sys
from typing import Dict, Optional
from xml.etree import ElementTree as element_tree


class CommandError(Exception):
    """Ошибка выполнения команды."""


class VFSNode:
    """Узел VFS: директория или файл."""

    def __init__(self, name: str, is_dir: bool = False, content: str = ""):
        """Инициализация узла."""
        self.name = name
        self.is_dir = is_dir
        self.content = content
        self.children: Dict[str, "VFSNode"] = {}


def _normalize_parts(path: str, cwd: str) -> list:
    """Нормализует путь и возвращает список компонентов."""
    parts = [p for p in cwd.split("/") if p]
    if path.startswith("/"):
        parts = [p for p in path.split("/") if p]
    else:
        parts.extend([p for p in path.split("/") if p])

    norm_parts = []
    for p in parts:
        if p == ".." and norm_parts:
            norm_parts.pop()
        elif p not in (".", ".."):
            norm_parts.append(p)
    return norm_parts


class VFS:
    """Виртуальная файловая система (XML)."""

    def __init__(self):
        """Инициализация VFS."""
        self.root = VFSNode("/", is_dir=True)

    def load_from_xml(self, path: str) -> None:
        """Загружает VFS из XML."""
        try:
            tree = element_tree.parse(path)
        except FileNotFoundError:
            raise FileNotFoundError(f"VFS файл не найден: {path}")
        except element_tree.ParseError as e:
            raise ValueError(f"Ошибка парсинга XML: {e}")

        root_elem = tree.getroot()
        if root_elem.tag != "vfs":
            raise ValueError("Корневой элемент должен быть <vfs>")

        self.root = VFSNode("/", is_dir=True)
        self._parse_children(root_elem, self.root)

    def _parse_children(
        self, elem: element_tree.Element, parent: VFSNode
    ) -> None:
        """Рекурсивный обход XML."""
        for child in elem:
            name = child.get("name")
            if not name:
                continue
            if child.tag == "dir":
                node = VFSNode(name, is_dir=True)
                parent.children[name] = node
                self._parse_children(child, node)
            elif child.tag == "file":
                content = child.text or ""
                node = VFSNode(name, is_dir=False, content=content)
                parent.children[name] = node

    def save_to_xml(self, path: str) -> None:
        """Сохраняет VFS в XML."""
        root_elem = element_tree.Element("vfs")
        self._build_xml(self.root, root_elem)
        tree = element_tree.ElementTree(root_elem)
        element_tree.indent(tree, space="  ")
        tree.write(path, encoding="utf-8", xml_declaration=True)

    def _build_xml(
        self, node: VFSNode, parent_elem: element_tree.Element
    ) -> None:
        """Рекурсивная сборка XML."""
        for child in node.children.values():
            if child.is_dir:
                elem = element_tree.SubElement(
                    parent_elem, "dir", name=child.name
                )
                self._build_xml(child, elem)
            else:
                elem = element_tree.SubElement(
                    parent_elem, "file", name=child.name
                )
                elem.text = child.content

    def resolve(self, path: str, cwd: str = "/") -> Optional[VFSNode]:
        """Возвращает узел по пути с учётом cwd."""
        norm_parts = _normalize_parts(path, cwd)
        node = self.root
        for part in norm_parts:
            if not node.is_dir or part not in node.children:
                return None
            node = node.children[part]
        return node


def cmd_ls(vfs: VFS, cwd: str, args: list) -> str:
    """Вывод содержимого директории."""
    if len(args) > 1:
        raise CommandError("ls: слишком много аргументов")
    path = args[0] if args else "."
    node = vfs.resolve(path, cwd)
    if node is None:
        raise CommandError(f"ls: {path}: нет такого файла или каталога")
    if not node.is_dir:
        return node.name
    return "  ".join(sorted(node.children.keys()))


def cmd_cd(vfs: VFS, cwd: str, args: list) -> str:
    """Смена текущей директории."""
    if len(args) > 1:
        raise CommandError("cd: слишком много аргументов")
    path = args[0] if args else "/"
    node = vfs.resolve(path, cwd)
    if node is None:
        raise CommandError(f"cd: {path}: нет такого каталога")
    if not node.is_dir:
        raise CommandError(f"cd: {path}: не является каталогом")

    norm_parts = _normalize_parts(path, cwd)
    return "/" if not norm_parts else "/" + "/".join(norm_parts)


def cmd_pwd(vfs: VFS, cwd: str, args: list) -> str:
    """Вывод текущей директории."""
    if args:
        raise CommandError("pwd: не принимает аргументов")
    return cwd


def cmd_echo(vfs: VFS, cwd: str, args: list) -> str:
    """Вывод аргументов."""
    return " ".join(args)


def cmd_vfs_save(vfs: VFS, cwd: str, args: list) -> str:
    """Сохранение VFS."""
    if len(args) != 1:
        raise CommandError("vfs-save: требуется путь")
    vfs.save_to_xml(args[0])
    return f"VFS сохранена в {args[0]}"


class Shell:
    """Основной цикл оболочки."""

    def __init__(self, vfs: VFS, debug: bool = False):
        """Инициализация оболочки."""
        self.vfs = vfs
        self.cwd = "/"
        self.debug = debug
        self.running = True
        self.commands = {
            "ls": cmd_ls,
            "cd": cmd_cd,
            "pwd": cmd_pwd,
            "echo": cmd_echo,
            "vfs-save": cmd_vfs_save,
        }

    def get_prompt(self) -> str:
        """Приглашение к вводу."""
        user = os.getenv("USER", "user")
        host = os.uname().nodename if hasattr(os, "uname") else "host"
        return f"{user}@{host}:{self.cwd}$ "

    def execute_line(self, line: str) -> str:
        """Выполнение одной строки."""
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

        handler = self.commands[cmd_name]

        if cmd_name == "cd":
            new_cwd = handler(self.vfs, self.cwd, args)
            self.cwd = new_cwd
            return ""
        return handler(self.vfs, self.cwd, args)

    def run_repl(self) -> None:
        """Интерактивный цикл."""
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
        """Выполнение стартового скрипта."""
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
    """Разбор аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Эмулятор командной оболочки UNIX (Вариант №25)"
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
    """Точка входа."""
    args = parse_args()

    if args.debug:
        print("=== Параметры эмулятора ===")
        print(f"VFS: {args.vfs or 'не указан'}")
        print(f"Стартовый скрипт: {args.script or 'не указан'}")
        print(f"Отладка: {args.debug}")
        print("===========================")

    vfs = VFS()
    if args.vfs:
        try:
            vfs.load_from_xml(args.vfs)
        except (FileNotFoundError, ValueError) as e:
            print(f"Ошибка загрузки VFS: {e}", file=sys.stderr)
            sys.exit(1)

    shell = Shell(vfs, debug=args.debug)

    if args.script:
        shell.run_script(args.script)
    else:
        shell.run_repl()


if __name__ == "__main__":
    main()