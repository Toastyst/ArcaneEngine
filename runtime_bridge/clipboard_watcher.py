import pyperclip
import time

class ClipboardWatcher:
    def __init__(self, poll_interval=0.1):
        self.poll_interval = poll_interval
        self.last_clipboard = pyperclip.paste()

    def watch(self):
        while True:
            current = pyperclip.paste()
            if current != self.last_clipboard:
                self.last_clipboard = current
                if "[[ARCANE_REQUEST]]" in current:
                    return current
            time.sleep(self.poll_interval)