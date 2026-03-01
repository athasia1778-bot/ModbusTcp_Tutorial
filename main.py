from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SERVER_SCRIPT = ROOT / "server.py"
CLIENT_SCRIPT = ROOT / "client.py"


def open_cmd_window(title: str, script_path: Path) -> None:
    run_cmd = subprocess.list2cmdline([sys.executable, str(script_path)])
    subprocess.Popen(
        ["cmd", "/d", "/k", f"title {title} && {run_cmd}"],
        cwd=str(ROOT),
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="在不同終端視窗開啟 server.py 與 client.py"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="開啟 client 視窗前等待秒數（預設：1.0）",
    )
    args = parser.parse_args()

    if not SERVER_SCRIPT.exists() or not CLIENT_SCRIPT.exists():
        print("在 main.py 同層找不到 server.py 或 client.py")
        sys.exit(1)

    open_cmd_window("Modbus Server", SERVER_SCRIPT)
    time.sleep(max(0.0, args.delay))
    open_cmd_window("Modbus Client", CLIENT_SCRIPT)

    print("已開啟兩個終端視窗：")
    print("- Modbus Server")
    print("- Modbus Client")
    print("若不需要，可關閉此啟動器視窗。")


if __name__ == "__main__":
    main()
