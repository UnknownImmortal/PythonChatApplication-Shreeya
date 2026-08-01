"""
client.py
----------
Client-side socket logic for the Python Chat Application.

Responsibilities:
- Connect to the chat server over TCP.
- Provide send/receive helpers that the GUI (layout.py via main.py) can call.
- Run the "listen for incoming messages" loop on a background thread so the
  Tkinter GUI never freezes while waiting for data.
"""

import socket
import threading

HOST = "127.0.0.1"   # server address to connect to
PORT = 5555           # must match the port the server is listening on


class ChatClient:
    """
    Wraps a TCP client socket.

    Usage:
        client = ChatClient(on_message_received=some_function)
        client.connect()          # connects to the server
        client.send("hello")      # send a message to the server
        client.close()            # shut everything down
    """

    def __init__(self, host=HOST, port=PORT, on_message_received=None):
        self.host = host
        self.port = port
        # Callback the GUI provides; called with the received text whenever
        # a new message arrives from the server.
        self.on_message_received = on_message_received

        self.client_socket = None
        self.running = False

    def connect(self):
        """Connect to the server and start listening for messages."""
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.running = True

        print(f"[CLIENT] Connected to server at {self.host}:{self.port}")

        # Start listening for messages from the server in the background
        # so this doesn't block the GUI's main loop.
        listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        listener_thread.start()

    def _listen_loop(self):
        """Continuously receive messages from the server until disconnect."""
        while self.running:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    # Empty data means the server closed the connection.
                    print("[CLIENT] Server disconnected.")
                    break

                message = data.decode("utf-8")
                print(f"[CLIENT] Received: {message}")

                if self.on_message_received:
                    self.on_message_received(message)

            except (ConnectionResetError, OSError):
                # Socket closed or connection lost.
                break

        self.running = False

    def send(self, message: str):
        """Send a message to the server."""
        if self.client_socket:
            try:
                self.client_socket.sendall(message.encode("utf-8"))
            except OSError as e:
                print(f"[CLIENT] Failed to send message: {e}")

    def close(self):
        """Close the client socket cleanly."""
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except OSError:
                pass
        print("[CLIENT] Disconnected.")


if __name__ == "__main__":
    # Simple standalone test: run the client on its own (no GUI),
    # print incoming messages, and let you type messages to send.
    # Run server.py first in another terminal before running this.
    def print_message(msg):
        print(f"\n[Server says]: {msg}\n> ", end="")

    client = ChatClient(on_message_received=print_message)
    client.connect()

    print("Type messages to send to the server. Type 'exit' to quit.")
    while True:
        text = input("> ")
        if text.lower() == "exit":
            break
        client.send(text)

    client.close()
