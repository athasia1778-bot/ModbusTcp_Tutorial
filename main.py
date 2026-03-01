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
        description="Open server.py and client.py in separate terminal windows"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Seconds to wait before opening client window (default: 1.0)",
    )
    args = parser.parse_args()

    if not SERVER_SCRIPT.exists() or not CLIENT_SCRIPT.exists():
        print("server.py or client.py not found next to main.py")
        sys.exit(1)

    open_cmd_window("Modbus Server", SERVER_SCRIPT)
    time.sleep(max(0.0, args.delay))
    open_cmd_window("Modbus Client", CLIENT_SCRIPT)

    print("Opened two terminals:")
    print("- Modbus Server")
    print("- Modbus Client")
    print("Close this launcher window if not needed.")


if __name__ == "__main__":
    main()
