import argparse
import os
import sys
import xml.etree.ElementTree as ET
from typing import Dict, Optional


class VFSNode:
    def __init__(self, name: str, is_dir: bool = False, content: str = ""):
        self.name = name
        self.is_dir = is_dir
        self.content = content
        self.children: Dict[str, "VFSNode"] = {}
        self.mode = 0o755 if is_dir else 0o644


class VFS:
    def __init__(self):
        self.root = VFSNode("/", is_dir=True)

    def load_from_xml(self, path: str) -> None:
        try:
            tree = ET.parse(path)
        except FileNotFoundError:
            raise FileNotFoundError(f"VFS файл не найден: {path}")
        except ET.ParseError as e:
            raise ValueError(f"Ошибка парсинга XML: {e}")

        root_elem = tree.getroot()
        if root_elem.tag != "vfs":
            raise ValueError("Корневой элемент должен быть <vfs>")

        self.root = VFSNode("/", is_dir=True)
        self._parse_children(root_elem, self.root)

    def _parse_children(self, elem: ET.Element, parent: VFSNode) -> None:
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
        root_elem = ET.Element("vfs")
        self._build_xml(self.root, root_elem)
        tree = ET.ElementTree(root_elem)
        ET.indent(tree, space="  ")
        tree.write(path, encoding="utf-8", xml_declaration=True)

    def _build_xml(self, node: VFSNode, parent_elem: ET.Element) -> None:
        for child in node.children.values():
            if child.is_dir:
                elem = ET.SubElement(parent_elem, "dir", name=child.name)
                self._build_xml(child, elem)
            else:
                elem = ET.SubElement(parent_elem, "file", name=child.name)
                elem.text = child.content

    def resolve(self, path: str, cwd: str = "/") -> Optional[VFSNode]:
        if path.startswith("/"):
            parts = [p for p in path.split("/") if p]
            node = self.root
        else:
            base = [p for p in cwd.split("/") if p]
            extra = [p for p in path.split("/") if p]
            parts = base + extra
            node = self.root

        for part in parts:
            if part in (".", ""):
                continue
            if part == "..":
                continue
            if not node.is_dir or part not in node.children:
                return None
            node = node.children[part]
        return node


class CommandError(Exception):
    pass

def cmd_ls(vfs: VFS, cwd: str, args: list) -> str:
    if args:
        return "ls - " + " ".join(args)
    return "ls"


def cmd_cd(vfs: VFS, cwd: str, args: list) -> str:
    if args:
        return "cd - " + " ".join(args)
    return "cd"


def cmd_vfs_save(vfs: VFS, cwd: str, args: list) -> str:
    if len(args) != 1:
        raise CommandError("vfs-save: требуется путь")
    vfs.save_to_xml(args[0])
    return f"VFS сохранена в {args[0]}"


class Shell:
    def __init__(self, vfs: VFS, debug: bool = False):
        self.vfs = vfs
        self.cwd = "/"
        self.running = True
        self.debug = debug
        self.commands = {
            "ls": cmd_ls,
            "cd": cmd_cd,
            "vfs-save": cmd_vfs_save,
        }

    def get_prompt(self) -> str:
        user = os.getenv("USER", "user")
        host = os.uname().nodename if hasattr(os, "uname") else "host"
        return f"{user}@{host}:{self.cwd}$ "

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

        handler = self.commands[cmd_name]
        if cmd_name == "cd":
            new_cwd = handler(self.vfs, self.cwd, args)
            self.cwd = new_cwd
            return ""
        return handler(self.vfs, self.cwd, args)

    def run_repl(self) -> None:
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
            return
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
                break

def parse_args():
    parser = argparse.ArgumentParser(description="Эмулятор командной оболочки UNIX")
    parser.add_argument("--vfs", help="Путь к XML-файлу VFS")
    parser.add_argument("--script", help="Путь к стартовому скрипту")
    parser.add_argument("--debug", action="store_true", help="Отладочный вывод")
    return parser.parse_args()


def main():
    args = parse_args()
    vfs = VFS()
    if args.vfs:
        try:
            vfs.load_from_xml(args.vfs)
        except (FileNotFoundError, ValueError) as e:
            print(f"Ошибка загрузки VFS: {e}", file=sys.stderr)
            sys.exit(1)

    if args.debug:
        print("=== Параметры эмулятора ===")
        print(f"VFS: {args.vfs or 'не указан (по умолчанию пустая)'}")
        print(f"Стартовый скрипт: {args.script or 'не указан'}")
        print("===========================")

    shell = Shell(vfs, debug=args.debug)

    if args.script:
        shell.run_script(args.script)
    else:
        shell.run_repl()


if __name__ == "__main__":
    main()
