import time


class StateManager:
    def __init__(self, toggle_window_s=3):
        self.original_text = ""
        self.translated_text = ""
        self.is_showing_translation = False
        self.is_processing = False
        self.last_trigger_time = 0
        self.toggle_window_s = toggle_window_s

    def has_cache(self):
        return bool(self.original_text and self.translated_text)

    def visible_text(self):
        """当前输入框里应该显示着的文本（原文或译文）。"""
        if not self.has_cache():
            return ""
        return self.translated_text if self.is_showing_translation else self.original_text

    def should_toggle(self):
        return time.time() - self.last_trigger_time < self.toggle_window_s

    def set_translation(self, original, translated):
        self.original_text = original
        self.translated_text = translated
        self.is_showing_translation = True
        self.last_trigger_time = time.time()

    def toggle(self):
        self.last_trigger_time = time.time()
        if self.is_showing_translation:
            self.is_showing_translation = False
            return self.original_text
        else:
            self.is_showing_translation = True
            return self.translated_text

    def clear_cache(self):
        self.original_text = ""
        self.translated_text = ""
        self.is_showing_translation = False
