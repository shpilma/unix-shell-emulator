@echo off
cd /d "%~dp0\.."

py src/main.py --vfs scripts/vfs_examples/minimal.xml --script scripts/start_vfs.txt
py src/main.py --vfs scripts/vfs_examples/several_files.xml --debug
py src/main.py --script scripts/start_errors.txt
py src/main.py --vfs scripts/vfs_examples/deep_tree.xml --script scripts/start_basic.txt
pause