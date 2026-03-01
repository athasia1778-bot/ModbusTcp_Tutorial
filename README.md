# Modbus TCP Python Tutorial (1 Server + 1 Client)

This tutorial contains:
- `server.py`: Modbus TCP server with interactive console commands to inspect and edit data.
- `client.py`: Modbus TCP client with interactive console commands to read/write server data.

## 1) Install dependencies

```bash
pip install -r requirements.txt
```

## 2) Run in two console windows

### Console A (server)

```bash
python server.py
```

### Console B (client)

```bash
python client.py
```

> Default endpoint: `127.0.0.1:5020`

## 3) Demo commands

### On server window

```text
show hr 0 5
show coil 0 5
set hr 1 123
set coil 2 1
```

### On client window

```text
read hr 0 5
read coil 0 5
write hr 3 777
write coil 4 0
```

After each write from client, use `show ...` on server to verify values changed.

## Notes

- Uses non-privileged port `5020` to avoid admin rights required by port 502.
- Address indexing starts at `0` in this example.
- Type `help` in each window for command usage.
