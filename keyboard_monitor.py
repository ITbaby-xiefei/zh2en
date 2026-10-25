import time
import threading
import keyboard


class KeyboardMonitor:
    def __init__(self, time_window_ms=500, on_trigger=None):
        self.time_window = time_window_ms / 1000.0
        self.on_trigger = on_trigger
        self.space_times = []
        self.lock = threading.Lock()
        self._is_sending = False

    def start(self):
        keyboard.on_press_key("space", self._on_space)

    def set_sending(self, value):
        self._is_sending = value

    def _on_space(self, event):
        if self._is_sending:
            return

        with self.lock:
            now = time.time()
            self.space_times = [t for t in self.space_times if now - t < self.time_window]
            self.space_times.append(now)

            if len(self.space_times) >= 3:
                self.space_times = []
                if self.on_trigger:
                    threading.Thread(target=self.on_trigger, daemon=True).start()
