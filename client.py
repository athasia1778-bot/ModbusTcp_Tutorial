from __future__ import annotations

import threading

from pyModbusTCP.client import ModbusClient

HOST = "127.0.0.1"
PORT = 5020


def print_help() -> None:
    print(
        """
Commands:
  help                       Show this help
  read hr <start> <count>    Read holding registers
  read coil <start> <count>  Read coils
  write hr <addr> <value>    Write one holding register
  write coil <addr> <0|1>    Write one coil
    auto_read coil <s> <n>     Read coils every 5 seconds
    stop_auto_read             Stop auto coil reading
  quit                       Exit client
""".strip()
    )


def read_holding_registers(client: ModbusClient, start: int, count: int) -> None:
    values = client.read_holding_registers(start, count)
    print(values if values is not None else "Read failed")


def read_coils(client: ModbusClient, start: int, count: int) -> None:
    values = client.read_coils(start, count)
    print(values if values is not None else "Read failed")


def write_holding_register(client: ModbusClient, addr: int, value: int) -> None:
    ok = client.write_single_register(addr, value)
    print("OK" if ok else "Write failed")


def write_coil(client: ModbusClient, addr: int, value: int) -> None:
    ok = client.write_single_coil(addr, bool(value))
    print("OK" if ok else "Write failed")


def start_auto_read_coils(
    state: dict[str, threading.Event | threading.Thread | tuple[int, int] | None],
    client: ModbusClient,
    start: int,
    count: int,
) -> None:
    stop_auto_read_coils(state)

    stop_event = threading.Event()

    def worker() -> None:
        print(f"Auto read started for coils {start}..{start + count - 1} (every 5 seconds)")
        while not stop_event.is_set():
            values = client.read_coils(start, count)
            if values is None:
                print(f"[AUTO] read failed for coil[{start}:{start + count}]")
            else:
                print(f"[AUTO] coil[{start}:{start + count}] = {values}")

            if stop_event.wait(5.0):
                break

    thread = threading.Thread(target=worker, daemon=True)
    state["range"] = (start, count)
    state["stop_event"] = stop_event
    state["thread"] = thread
    thread.start()


def stop_auto_read_coils(
    state: dict[str, threading.Event | threading.Thread | tuple[int, int] | None],
) -> None:
    stop_event = state.get("stop_event")
    thread = state.get("thread")

    if isinstance(stop_event, threading.Event):
        stop_event.set()

    if isinstance(thread, threading.Thread) and thread.is_alive():
        thread.join(timeout=1.0)

    if state.get("stop_event") is not None or state.get("thread") is not None:
        print("Auto read stopped")

    state["range"] = None
    state["stop_event"] = None
    state["thread"] = None


def main() -> None:
    client = ModbusClient(host=HOST, port=PORT, auto_open=True, auto_close=False)
    auto_read_state: dict[str, threading.Event | threading.Thread | tuple[int, int] | None] = {
        "range": None,
        "stop_event": None,
        "thread": None,
    }

    print(f"Modbus TCP client ready for {HOST}:{PORT}")
    print_help()

    try:
        while True:
            raw = input("client> ").strip()
            if not raw:
                continue

            parts = raw.split()
            cmd = parts[0].lower()

            if cmd in {"quit", "exit"}:
                break
            if cmd == "help":
                print_help()
                continue

            if cmd == "read" and len(parts) == 4:
                area, start, count = parts[1], int(parts[2]), int(parts[3])
                if area == "hr":
                    read_holding_registers(client, start, count)
                elif area == "coil":
                    read_coils(client, start, count)
                else:
                    print("Area must be hr or coil")
                continue

            if cmd == "write" and len(parts) == 4:
                area, addr, value = parts[1], int(parts[2]), int(parts[3])
                if area == "hr":
                    write_holding_register(client, addr, value)
                elif area == "coil":
                    if value not in (0, 1):
                        print("Coil value must be 0 or 1")
                        continue
                    write_coil(client, addr, value)
                else:
                    print("Area must be hr or coil")
                continue

            if cmd == "auto_read" and len(parts) == 4:
                area, start, count = parts[1], int(parts[2]), int(parts[3])
                if area != "coil":
                    print("Only coil is supported: auto_read coil <start> <count>")
                    continue
                start_auto_read_coils(auto_read_state, client, start, count)
                continue

            if cmd == "stop_auto_read" and len(parts) == 1:
                stop_auto_read_coils(auto_read_state)
                continue

            print("Invalid command. Type 'help'.")
    except KeyboardInterrupt:
        pass
    finally:
        stop_auto_read_coils(auto_read_state)
        client.close()
        print("Client closed")


if __name__ == "__main__":
    main()
