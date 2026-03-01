# Modbus TCP Python 教學（1 個 Server + 1 個 Client）

本專案包含：
- `server.py`：Modbus TCP 伺服器，可在主控台互動式查看與修改資料。
- `client.py`：Modbus TCP 用戶端，可在主控台互動式讀寫伺服器資料。
- `main.py`：一鍵開啟兩個視窗，分別執行 Server 與 Client。

## 1) 安裝相依套件

```bash
pip install -r requirements.txt
```

## 2) 啟動方式

### 方式 A：一鍵開兩個視窗（建議）

```bash
python main.py
```

可選參數（延遲開啟 client 視窗秒數）：

```bash
python main.py --delay 1.5
```

### 方式 B：手動開兩個主控台

主控台 A（server）：

```bash
python server.py
```

主控台 B（client）：

```bash
python client.py
```

> 預設連線端點：`127.0.0.1:5020`

## 3) 基本指令示範

### Server 視窗

```text
show hr 0 5
show coil 0 5
set hr 1 123
set coil 2 1
```

### Client 視窗

```text
read hr 0 5
read coil 0 5
write hr 3 777
write coil 4 0
```

## 4) 自動更新 / 自動讀取（每 5 秒）

### Server：自動更新 coil

```text
auto_update coil 0
```

說明：每 5 秒切換一次 `coil[0]`（0/1 交替）。

停止自動更新：

```text
stop_auto_update
```

### Client：自動讀取 coil

```text
auto_read coil 0 5
```

說明：每 5 秒讀取一次 `coil[0:5]`。

停止自動讀取：

```text
stop_auto_read
```

## 5) 完整示範流程

1. 在 Server 輸入：`auto_update coil 0`
2. 在 Client 輸入：`auto_read coil 0 5`
3. 觀察 Client 視窗每 5 秒輸出的 `[AUTO]` 變化
4. 結束時輸入：
	- Server：`stop_auto_update`
	- Client：`stop_auto_read`

## 備註

- 本範例使用非特權埠 `5020`，避免使用 `502` 需要管理員權限。
- 本範例位址索引由 `0` 開始。
- 各視窗輸入 `help` 可查看指令說明。
