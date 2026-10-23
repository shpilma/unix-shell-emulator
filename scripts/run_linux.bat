cd "$(dirname "$0")/.."

python3 src/main.py --vfs vfs.xml
python3 src/main.py --script scripts/start_basic.txt
python3 src/main.py --debug
python3 src/main.py --vfs vfs.xml --script scripts/start_basic.txt --debug
read -p "Нажмите Enter для выхода..."
pause