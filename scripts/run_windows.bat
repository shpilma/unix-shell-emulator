@echo off
cd /d "%~dp0\.."
py src/main.py --vfs vfs.xml --script scripts/start_basic.txt
py src/main.py --script scripts/start_basic.txt
py src/main.py --debug --script scripts/start_debug.txt
py src/main.py --script scripts/start_errors.txt
py src/main.py --vfs vfs.xml --script scripts/start_basic.txt --debug
pause