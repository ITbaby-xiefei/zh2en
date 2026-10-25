import sys
import threading
import pyautogui
import keyboard
import requests

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05

sys.stdout.reconfigure(encoding='utf-8')

from config import load_config
from keyboard_monitor import KeyboardMonitor
from text_extractor import extract_text_before_cursor, replace_text
from translation_engine import TranslationEngine
from state_manager import StateManager


class TranslatorApp:
    def __init__(self):
        self.config = load_config()
        self.engine = TranslationEngine(self.config)
        self.state = StateManager(toggle_window_s=self.config.get('toggle_window_s', 3))
        self.monitor = KeyboardMonitor(
            time_window_ms=self.config['time_window_ms'],
            on_trigger=self._on_trigger
        )

    def start(self):
        print("=" * 50)
        print("Zh2En Translator - 中文转英文翻译工具")
        print("=" * 50)
        print(f"API类型: {self.config['api_type']}")
        print(f"模型: {self.config['model']}")
        print(f"端点: {self.config['endpoint']}")
        print("-" * 50)
        print("使用方法:")
        print("  1. 在任意输入框输入中文")
        print("  2. 快速按3次空格键 → 翻译为英文")
        print("  3. 再快速按3次空格键 → 切回原文")
        print("  4. 按 Ctrl+Q → 退出程序")
        print("=" * 50)

        self.monitor.start()
        keyboard.add_hotkey('ctrl+q', lambda: self.stop())

        try:
            keyboard.wait()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        print("\n正在退出...")
        keyboard.unhook_all()
        import os
        os._exit(0)

    def _on_trigger(self):
        if self.state.is_processing:
            return

        self.state.is_processing = True
        self.monitor.set_sending(True)

        try:
            # 触发用的 3 个空格会落在光标前，截取时一并被选中，
            # 替换为译文时就顺带覆盖掉了，不再单独盲删退格
            original = extract_text_before_cursor()

            if not original:
                print("[提示] 无法截取文本：请确认输入框有焦点，且光标前已有文字")
                self.state.clear_cache()
                return

            if (self.state.has_cache() and self.state.should_toggle()
                    and original == self.state.visible_text()):
                target = self.state.toggle()
                if replace_text(original, target):
                    status = "英文" if self.state.is_showing_translation else "原文"
                    print(f"[切换] → {status}")
                else:
                    self.state.toggle()  # 替换失败，回滚状态
                    print("[提示] 无法替换文本，已保持原样")
                return

            if not self._contains_chinese(original):
                print("[提示] 未检测到中文")
                self.state.clear_cache()
                return

            print(f"[翻译] {original}")

            try:
                translated = self.engine.translate(original)
                print(f"[结果] {translated}")
            except requests.exceptions.RequestException as e:
                print(f"[错误] API请求失败: {e}")
                return
            except Exception as e:
                print(f"[错误] 翻译失败: {e}")
                return

            if replace_text(original, translated):
                self.state.set_translation(original, translated)
            else:
                self.state.clear_cache()
                print("[提示] 无法替换文本，已保持原样")

        except Exception as e:
            print(f"[错误] {e}")
        finally:
            self.monitor.set_sending(False)
            self.state.is_processing = False

    def _contains_chinese(self, text):
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                return True
        return False


if __name__ == "__main__":
    app = TranslatorApp()
    app.start()
