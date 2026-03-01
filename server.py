from __future__ import annotations

import threading
import time

from pyModbusTCP.server import DataBank, ModbusServer

HOST = "0.0.0.0"
PORT = 5020
DATABANK = DataBank()


def print_help() -> None:
    print(
        """
指令：
    help                       顯示說明
    show hr <start> <count>    顯示保持暫存器
    show coil <start> <count>  顯示線圈
    set hr <addr> <value>      設定一個保持暫存器
    set coil <addr> <0|1>      設定一個線圈
    auto_update coil <addr>    每 5 秒自動切換線圈
    stop_auto_update           停止自動更新線圈
    quit                       停止伺服器
""".strip()
    )


def show_holding_registers(start: int, count: int) -> None:
    values = DATABANK.get_holding_registers(start, count)
    if values is None:
        print("HR 範圍無效")
        return
    print(f"HR[{start}:{start + count}] = {values}")


def show_coils(start: int, count: int) -> None:
    values = DATABANK.get_coils(start, count)
    if values is None:
        print("Coil 範圍無效")
        return
    print(f"Coil[{start}:{start + count}] = {values}")


def set_holding_register(addr: int, value: int) -> None:
    ok = DATABANK.set_holding_registers(addr, [value])
    print("成功" if ok else "寫入失敗")


def set_coil(addr: int, value: int) -> None:
    ok = DATABANK.set_coils(addr, [bool(value)])
    print("成功" if ok else "寫入失敗")


def start_auto_update_coil(
    state: dict[str, threading.Event | threading.Thread | int | None], addr: int
) -> None:
    stop_auto_update_coil(state)

    stop_event = threading.Event()

    def worker() -> None:
        current = 0
        print(f"已啟用自動更新 coil {addr}（每 5 秒）")
        while not stop_event.is_set():
            current = 0 if current == 1 else 1
            ok = DATABANK.set_coils(addr, [bool(current)])
            if ok:
                print(f"[AUTO] coil[{addr}] -> {current}")
            else:
                print(f"[AUTO] 寫入失敗：coil[{addr}]")

            if stop_event.wait(5.0):
                break

    thread = threading.Thread(target=worker, daemon=True)
    state["addr"] = addr
    state["stop_event"] = stop_event
    state["thread"] = thread
    thread.start()


def stop_auto_update_coil(
    state: dict[str, threading.Event | threading.Thread | int | None],
) -> None:
    stop_event = state.get("stop_event")
    thread = state.get("thread")

    if isinstance(stop_event, threading.Event):
        stop_event.set()

    if isinstance(thread, threading.Thread) and thread.is_alive():
        thread.join(timeout=1.0)

    if state.get("stop_event") is not None or state.get("thread") is not None:
        print("已停止自動更新")

    state["stop_event"] = None
    state["thread"] = None
    state["addr"] = None


def main() -> None:
    server = ModbusServer(host=HOST, port=PORT, no_block=True, data_bank=DATABANK)
    auto_update_state: dict[str, threading.Event | threading.Thread | int | None] = {
        "addr": None,
        "stop_event": None,
        "thread": None,
    }

    DATABANK.set_holding_registers(0, [10, 20, 30, 40, 50])
    DATABANK.set_coils(0, [False, True, False, True, False])

    server.start()
    print(f"Modbus TCP 伺服器已啟動：{HOST}:{PORT}")
    print("請在另一個終端機執行 client.py。")
    print_help()

    try:
        while True:
            raw = input("server> ").strip()
            if not raw:
                continue

            parts = raw.split()
            cmd = parts[0].lower()

            if cmd in {"quit", "exit"}:
                break
            if cmd == "help":
                print_help()
                continue

            if cmd == "show" and len(parts) == 4:
                area, start, count = parts[1], int(parts[2]), int(parts[3])
                if area == "hr":
                    show_holding_registers(start, count)
                elif area == "coil":
                    show_coils(start, count)
                else:
                    print("區域必須是 hr 或 coil")
                continue

            if cmd == "set" and len(parts) == 4:
                area, addr, value = parts[1], int(parts[2]), int(parts[3])
                if area == "hr":
                    set_holding_register(addr, value)
                elif area == "coil":
                    if value not in (0, 1):
                        print("Coil 值必須是 0 或 1")
                        continue
                    set_coil(addr, value)
                else:
                    print("區域必須是 hr 或 coil")
                continue

            if cmd == "auto_update" and len(parts) == 3:
                area, addr = parts[1], int(parts[2])
                if area != "coil":
                    print("僅支援 coil：auto_update coil <addr>")
                    continue
                start_auto_update_coil(auto_update_state, addr)
                continue

            if cmd == "stop_auto_update" and len(parts) == 1:
                stop_auto_update_coil(auto_update_state)
                continue

            print("無效指令，請輸入 help。")
    except KeyboardInterrupt:
        pass
    finally:
        stop_auto_update_coil(auto_update_state)
        server.stop()
        print("伺服器已停止")


if __name__ == "__main__":
    main()
