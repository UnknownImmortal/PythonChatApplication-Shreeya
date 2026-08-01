"""
main.py
--------
Entry point for the Python Chat Application.

Asks the user whether to run as SERVER or CLIENT, then launches the
Tkinter GUI (layout.py) wired up to the matching networking module
(server.py or client.py).

Threading note:
    Tkinter is NOT thread-safe. Network data arrives on a background
    thread (started inside server.py / client.py), so we never touch
    Tkinter widgets directly from that thread. Instead, incoming
    messages are pushed into a thread-safe queue, and the GUI polls
    that queue every 100ms on the main thread via root.after(). This
    is the standard safe pattern for combining sockets + Tkinter.
"""

import tkinter as tk
import queue

from layout import ChatWindow
from server import ChatServer
from client import ChatClient


class ChatApp:
    def __init__(self, root, mode: str):
        """
        mode: "server" or "client"
        """
        self.root = root
        self.mode = mode
        self.incoming_queue = queue.Queue()

        title = "Python Chat Application - Server" if mode == "server" \
            else "Python Chat Application - Client"
        self.window = ChatWindow(root, title=title, on_send=self._on_send)

        self.network = None
        self._start_networking()

        # Poll the queue for incoming messages every 100ms.
        self.root.after(100, self._process_incoming)

        # Make sure sockets close cleanly when the window is closed.
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _start_networking(self):
        """
        Create the ChatServer or ChatClient. The actual connect/listen
        call can block, so we run it on a background thread to keep
        the GUI responsive while waiting for a connection.
        """
        import threading

        self.window.display_message(
            "System",
            "Waiting for connection..." if self.mode == "server" else "Connecting to server...",
            tag="system",
        )

        def on_message_received(message):
            # Called from the networking background thread -
            # just queue it, don't touch the GUI here directly.
            self.incoming_queue.put(message)

        if self.mode == "server":
            self.network = ChatServer(on_message_received=on_message_received)
        else:
            self.network = ChatClient(on_message_received=on_message_received)

        def start_connection():
            try:
                if self.mode == "server":
                    self.network.start()
                else:
                    self.network.connect()
                self.incoming_queue.put(("__system__", "Connected!"))
            except OSError as e:
                self.incoming_queue.put(("__system__", f"Connection failed: {e}"))

        threading.Thread(target=start_connection, daemon=True).start()

    def _on_send(self, text: str):
        """Called by layout.py whenever the user sends a message."""
        if self.network:
            self.network.send(text)

    def _process_incoming(self):
        """Runs on the main thread; safely updates the GUI."""
        while not self.incoming_queue.empty():
            item = self.incoming_queue.get()

            # System messages are pushed as a ("__system__", text) tuple.
            if isinstance(item, tuple) and item[0] == "__system__":
                self.window.display_message("System", item[1], tag="system")
            else:
                other = "Server" if self.mode == "client" else "Client"
                self.window.display_message(other, item, tag="received")

        # Keep polling.
        self.root.after(100, self._process_incoming)

    def _on_close(self):
        if self.network:
            self.network.close()
        self.root.destroy()


def choose_mode() -> str:
    """Small startup dialog asking whether to run as server or client."""
    chooser = tk.Tk()
    chooser.title("Python Chat Application")
    chooser.geometry("300x150")

    result = {"mode": None}

    def pick(mode):
        result["mode"] = mode
        chooser.destroy()

    tk.Label(chooser, text="Run as:", font=("Segoe UI", 12)).pack(pady=(20, 10))
    tk.Button(chooser, text="Server", width=15, command=lambda: pick("server")).pack(pady=5)
    tk.Button(chooser, text="Client", width=15, command=lambda: pick("client")).pack(pady=5)

    chooser.mainloop()
    return result["mode"]


def main():
    mode = choose_mode()
    if mode is None:
        return  # user closed the chooser window without picking

    root = tk.Tk()
    ChatApp(root, mode)
    root.mainloop()


if __name__ == "__main__":
    main()
