"""
layout.py
----------
Tkinter GUI layout for the Python Chat Application.

This module defines a reusable ChatWindow class that provides:
- A scrollable message display area (shows sent + received messages).
- A text entry box for typing a new message.
- A Send button (and Enter key) to send the message.

layout.py only handles the VISUAL side of things. It does NOT know about
sockets directly — instead, main.py gives it an `on_send` callback function
to call whenever the user sends a message, and main.py calls
`chat_window.display_message(...)` whenever a new message arrives over the
network. This keeps networking and GUI code cleanly separated.
"""

import tkinter as tk
from tkinter import scrolledtext


class ChatWindow:
    """
    A Tkinter chat window with a message display area and an input box.

    Usage:
        root = tk.Tk()
        window = ChatWindow(root, title="Chat - Server", on_send=my_send_function)
        window.display_message("System", "Waiting for connection...")
        root.mainloop()
    """

    def __init__(self, root, title="Python Chat Application", on_send=None):
        self.root = root
        self.on_send = on_send  # function to call when the user sends a message

        self.root.title(title)
        self.root.geometry("500x600")
        self.root.minsize(400, 400)

        self._build_widgets()

    def _build_widgets(self):
        # --- Message display area (read-only, scrollable) ---
        self.message_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            state="disabled",   # user can't type directly into the log
            font=("Segoe UI", 11),
            bg="#f5f5f5",
        )
        self.message_area.pack(padx=10, pady=(10, 5), fill=tk.BOTH, expand=True)

        # Tag colors: messages we sent vs. messages we received.
        self.message_area.tag_config("sent", foreground="#0b5fff", justify="right")
        self.message_area.tag_config("received", foreground="#000000", justify="left")
        self.message_area.tag_config("system", foreground="#888888")

        # --- Bottom frame: entry box + Send button ---
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

        self.entry = tk.Entry(bottom_frame, font=("Segoe UI", 11))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entry.bind("<Return>", lambda event: self._handle_send())
        self.entry.focus()

        self.send_button = tk.Button(
            bottom_frame, text="Send", width=10, command=self._handle_send
        )
        self.send_button.pack(side=tk.RIGHT)

    def _handle_send(self):
        """Called when the user presses Enter or clicks Send."""
        text = self.entry.get().strip()
        if not text:
            return

        self.entry.delete(0, tk.END)

        # Show it in our own chat window immediately.
        self.display_message("You", text, tag="sent")

        # Let main.py know a message needs to go out over the network.
        if self.on_send:
            self.on_send(text)

    def display_message(self, sender: str, message: str, tag: str = "received"):
        """
        Add a message to the scrollable display area.

        tag: "sent" (our own messages), "received" (from the other side),
             or "system" (connection status messages).
        """
        self.message_area.config(state="normal")
        self.message_area.insert(tk.END, f"{sender}: {message}\n", tag)
        self.message_area.config(state="disabled")
        self.message_area.see(tk.END)  # auto-scroll to the latest message


if __name__ == "__main__":
    # Quick visual test of the layout with no real networking behind it.
    def fake_send(text):
        print(f"[layout.py test] Would send: {text}")

    root = tk.Tk()
    window = ChatWindow(root, title="Layout Preview", on_send=fake_send)
    window.display_message("System", "This is a layout preview.", tag="system")
    root.mainloop()
