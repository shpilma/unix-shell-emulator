@echo off
cd /d "%~dp0\.."

py src/main.py --vfs scripts/vfs_examples/several_files.xml --script scripts/start_advanced.txt
py src/main.py --vfs scripts/vfs_examples/several_files.xml --script scripts/start_commands.txt
py src/main.py --vfs scripts/vfs_examples/minimal.xml --script scripts/start_vfs.txt
py src/main.py --script scripts/start_errors.txt
pause