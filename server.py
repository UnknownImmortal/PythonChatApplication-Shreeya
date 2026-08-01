"""
server.py
----------
Server-side socket logic for the Python Chat Application.

Responsibilities:
- Create a TCP server socket that listens for an incoming client connection.
- Accept exactly one client connection.
- Provide send/receive helpers that the GUI (layout.py via main.py) can call.
- Run the "listen for incoming messages" loop on a background thread so the
  Tkinter GUI never freezes while waiting for data.
"""

import socket
import threading

HOST = "127.0.0.1"   # localhost - change to "0.0.0.0" to accept LAN connections
PORT = 5555           # port used by both client and server


class ChatServer:
    """
    Wraps a TCP server socket.

    Usage:
        server = ChatServer(on_message_received=some_function)
        server.start()          # blocks until a client connects
        server.send("hello")    # send a message to the connected client
        server.close()          # shut everything down
    """

    def __init__(self, host=HOST, port=PORT, on_message_received=None):
        self.host = host
        self.port = port
        # Callback the GUI provides; called with the received text whenever
        # a new message arrives from the client.
        self.on_message_received = on_message_received

        self.server_socket = None
        self.client_socket = None
        self.client_address = None
        self.running = False

    def start(self):
        """
        Create the listening socket, wait for a client to connect,
        then start a background thread that continuously listens
        for incoming messages.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow quick restart of the server on the same port during testing.
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)

        print(f"[SERVER] Listening on {self.host}:{self.port} ...")

        # This blocks until a client connects.
        self.client_socket, self.client_address = self.server_socket.accept()
        print(f"[SERVER] Client connected from {self.client_address}")

        self.running = True

        # Start listening for messages from the client in the background
        # so this doesn't block the GUI's main loop.
        listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        listener_thread.start()

    def _listen_loop(self):
        """Continuously receive messages from the client until disconnect."""
        while self.running:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    # Empty data means the client closed the connection.
                    print("[SERVER] Client disconnected.")
                    break

                message = data.decode("utf-8")
                print(f"[SERVER] Received: {message}")

                if self.on_message_received:
                    self.on_message_received(message)

            except (ConnectionResetError, OSError):
                # Socket closed or connection lost.
                break

        self.running = False

    def send(self, message: str):
        """Send a message to the connected client."""
        if self.client_socket:
            try:
                self.client_socket.sendall(message.encode("utf-8"))
            except OSError as e:
                print(f"[SERVER] Failed to send message: {e}")

    def close(self):
        """Close both the client and server sockets cleanly."""
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except OSError:
                pass
        if self.server_socket:
            try:
                self.server_socket.close()
            except OSError:
                pass
        print("[SERVER] Shut down.")


if __name__ == "__main__":
    # Simple standalone test: run the server on its own (no GUI),
    # print incoming messages, and let you type replies from the terminal.
    def print_message(msg):
        print(f"\n[Client says]: {msg}\n> ", end="")

    server = ChatServer(on_message_received=print_message)
    server.start()

    print("Type messages to send to the client. Type 'exit' to quit.")
    while True:
        text = input("> ")
        if text.lower() == "exit":
            break
        server.send(text)

    server.close()
