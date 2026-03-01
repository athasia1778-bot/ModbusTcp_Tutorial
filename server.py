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
Commands:
  help                       Show this help
  show hr <start> <count>    Show holding registers
  show coil <start> <count>  Show coils
  set hr <addr> <value>      Set one holding register
  set coil <addr> <0|1>      Set one coil
    auto_update coil <addr>    Toggle one coil every 5 seconds
    stop_auto_update           Stop auto coil update
  quit                       Stop server
""".strip()
    )


def show_holding_registers(start: int, count: int) -> None:
    values = DATABANK.get_holding_registers(start, count)
    if values is None:
        print("Invalid HR range")
        return
    print(f"HR[{start}:{start + count}] = {values}")


def show_coils(start: int, count: int) -> None:
    values = DATABANK.get_coils(start, count)
    if values is None:
        print("Invalid coil range")
        return
    print(f"Coil[{start}:{start + count}] = {values}")


def set_holding_register(addr: int, value: int) -> None:
    ok = DATABANK.set_holding_registers(addr, [value])
    print("OK" if ok else "Write failed")


def set_coil(addr: int, value: int) -> None:
    ok = DATABANK.set_coils(addr, [bool(value)])
    print("OK" if ok else "Write failed")


def start_auto_update_coil(
    state: dict[str, threading.Event | threading.Thread | int | None], addr: int
) -> None:
    stop_auto_update_coil(state)

    stop_event = threading.Event()

    def worker() -> None:
        current = 0
        print(f"Auto update started for coil {addr} (every 5 seconds)")
        while not stop_event.is_set():
            current = 0 if current == 1 else 1
            ok = DATABANK.set_coils(addr, [bool(current)])
            if ok:
                print(f"[AUTO] coil[{addr}] -> {current}")
            else:
                print(f"[AUTO] write failed for coil[{addr}]")

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
        print("Auto update stopped")

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
    print(f"Modbus TCP server started on {HOST}:{PORT}")
    print("Try with client.py in another terminal.")
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
                    print("Area must be hr or coil")
                continue

            if cmd == "set" and len(parts) == 4:
                area, addr, value = parts[1], int(parts[2]), int(parts[3])
                if area == "hr":
                    set_holding_register(addr, value)
                elif area == "coil":
                    if value not in (0, 1):
                        print("Coil value must be 0 or 1")
                        continue
                    set_coil(addr, value)
                else:
                    print("Area must be hr or coil")
                continue

            if cmd == "auto_update" and len(parts) == 3:
                area, addr = parts[1], int(parts[2])
                if area != "coil":
                    print("Only coil is supported: auto_update coil <addr>")
                    continue
                start_auto_update_coil(auto_update_state, addr)
                continue

            if cmd == "stop_auto_update" and len(parts) == 1:
                stop_auto_update_coil(auto_update_state)
                continue

            print("Invalid command. Type 'help'.")
    except KeyboardInterrupt:
        pass
    finally:
        stop_auto_update_coil(auto_update_state)
        server.stop()
        print("Server stopped")


if __name__ == "__main__":
    main()
