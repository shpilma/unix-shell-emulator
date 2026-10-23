#!/usr/bin/env bash
cd "$(dirname "$0")/.."

python3 src/main.py --vfs scripts/vfs_examples/minimal.xml --script scripts/start_vfs.txt
python3 src/main.py --vfs scripts/vfs_examples/several_files.xml --debug
python3 src/main.py --script scripts/start_errors.txt
python3 src/main.py --vfs scripts/vfs_examples/deep_tree.xml --script scripts/start_basic.txt
read -p "Нажмите Enter для выхода..."