# Python Chat Application

A simple two-way chat app built with **Python sockets** and a **Tkinter GUI**. One person runs it as the *server*, another runs it as the *client* — they connect over the network and chat back and forth in real time.

---

## 1. Download the Project

**Option A — Download as ZIP**
1. Click the green **Code** button on the GitHub repo page.
2. Select **Download ZIP**.
3. Extract the ZIP file anywhere on your computer.

**Option B — Clone with Git**
```bash
git clone https://github.com/UnknownImmortal/PythonChatApplication-Shreeya.git
```

Either way, you'll end up with a folder containing:
```
PythonChatApplication-Shreeya/
├── server.py
├── client.py
├── layout.py
├── main.py
├── LICENSE
└── README.md
```

---

## 2. Requirements

- **Python 3.8 or newer** — check with:
  ```bash
  python --version
  ```
  (Download from [python.org](https://www.python.org/downloads/) if you don't have it.)
- **Tkinter** — usually comes bundled with Python.
  - On Windows/Mac: nothing extra needed.
  - On Linux, if you get a `No module named tkinter` error:
    ```bash
    sudo apt install python3-tk
    ```
- No other installs needed — the app only uses Python's built-in libraries (`socket`, `threading`, `tkinter`, `queue`).

---

## 3. How to Open and Run It

You need to run the app **twice** — once as the server, once as the client. This can be two terminal windows on the same computer, or two different computers on the same network.

### Step-by-step:

1. Open a terminal (Command Prompt, PowerShell, or Terminal app) and navigate into the project folder:
   ```bash
   cd path/to/PythonChatApplication-Shreeya
   ```

2. Run:
   ```bash
   python main.py
   ```

3. A small popup window appears asking **"Run as: Server / Client"**.
   - In your **first** terminal, click **Server**.
   - Open a **second** terminal, `cd` into the same folder, run `python main.py` again, and click **Client**.

   > ⚠️ Always start the **Server** first — the Client needs something to connect to.

4. Once connected, both chat windows will show:
   ```
   System: Connected!
   ```

5. Type a message in either window's text box and press **Enter** (or click **Send**) — it will appear instantly in the other window.

---

## 4. How to Check It's Working

**Fastest check — no GUI, just the terminal:**

Open two terminals in the project folder:
```bash
# Terminal 1
python server.py

# Terminal 2
python client.py
```
Type something and press Enter in either terminal — you should see it printed in the other one immediately. This confirms the core networking works, even before touching the GUI.

**Full check — with the GUI:**
1. Launch `main.py` in two terminals as described in Step 3.
2. Confirm both windows show `System: Connected!`.
3. Send a message from the **Client** window → it should appear in the **Server** window labeled `Client:`.
4. Send a message from the **Server** window → it should appear in the **Client** window labeled `Server:`.
5. Close one window — the other side should print a disconnect message in its terminal.

If nothing happens:
- Make sure the server was started **before** the client.
- Make sure no other program is using port `5555` (you can change the `PORT` value at the top of both `server.py` and `client.py` — just make sure they match).
- If running on two different computers, make sure they're on the same network and check your firewall settings.

---

## 5. Chatting Across Two Different Computers (Optional)

By default the app only works on one computer (`localhost`). To chat between two devices on the same Wi-Fi/network:

1. On the **server's** computer, open `server.py` and change:
   ```python
   HOST = "0.0.0.0"
   ```
2. Find the server computer's local IP address (e.g. `192.168.1.5`) — on Windows use `ipconfig`, on Mac/Linux use `ifconfig` or `ip addr`.
3. On the **client's** computer, open `client.py` and change:
   ```python
   HOST = "192.168.1.5"   # use the server's actual IP address here
   ```
4. Run the server first, then the client, as in Step 3 above.

---

## Project Structure

| File | Purpose |
|---|---|
| `server.py` | Creates the server socket, listens for a connection, sends/receives messages |
| `client.py` | Connects to the server, sends/receives messages |
| `layout.py` | Tkinter chat window — message log, text box, Send button |
| `main.py` | Entry point — lets you choose Server/Client and connects the GUI to the networking |

This app supports **one connection at a time** — it's designed to clearly demonstrate two-way socket communication, not to be a multi-user chat server.
