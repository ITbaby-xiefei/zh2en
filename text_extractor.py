import time
import pyperclip
import pyautogui


# Disable pyautogui fail-safe (move mouse to corner to abort)
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05

COPY_TIMEOUT = 0.5
POLL_INTERVAL = 0.05

# 上一次成功截取文本所用的选区方式，替换时需要沿用同一方式
_last_strategy = None


def _read_clipboard():
    try:
        return pyperclip.paste()
    except Exception:
        return ""


def _write_clipboard(text):
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False


def _copy_with_verification(old_clipboard, timeout=COPY_TIMEOUT):
    """按 Ctrl+C，并确认剪贴板真的被改写。

    先把剪贴板写成哨兵值，再发 Ctrl+C：只有剪贴板发生变化才说明复制成功。
    这样绝不会把上一次残留的剪贴板内容误当作刚截取的文本。
    """
    sentinel = "\x00zh2en-sentinel-%d" % time.time_ns()
    if not _write_clipboard(sentinel):
        return ""

    pyautogui.hotkey('ctrl', 'c')

    text = ""
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(POLL_INTERVAL)
        current = _read_clipboard()
        if current != sentinel:
            text = current
            break

    _write_clipboard(old_clipboard)
    return text


def _select(strategy):
    if strategy == "all":
        pyautogui.hotkey('ctrl', 'a')
    else:
        pyautogui.hotkey('shift', 'home')
    time.sleep(0.2)


def extract_text_before_cursor():
    """截取光标前的文本。

    先按行首选区（Shift+Home），复制失败时退回到全选（Ctrl+A）——
    某些控件/输入法下 Shift+Home 无法建立选区，全选是可用的兜底方案。
    两种方式都失败时返回空字符串，调用方据此提示，而不是拿旧剪贴板顶替。
    """
    global _last_strategy

    old_clipboard = _read_clipboard()

    for strategy in ("line", "all"):
        _select(strategy)
        text = _copy_with_verification(old_clipboard)
        if text.strip():
            _last_strategy = strategy
            return text.strip()

    # 没有取到任何文本：收起可能残留的选区，恢复光标位置
    _last_strategy = None
    pyautogui.press('right')
    time.sleep(0.1)
    return ""


def replace_text(expected, new_text):
    """把 `expected` 对应的文本替换为 `new_text`。

    粘贴前先复制一次当前选区并核对内容，确认选区正好覆盖 `expected`，
    避免选区没建立时把译文“插入”到原文前面（原文与译文同时残留）。
    返回 True 表示已完成替换。
    """
    global _last_strategy

    strategy = _last_strategy or "line"
    old_clipboard = _read_clipboard()

    _select(strategy)
    current = _copy_with_verification(old_clipboard).strip()

    if current != expected.strip() and strategy != "all":
        _select("all")
        current = _copy_with_verification(old_clipboard).strip()

    if current != expected.strip():
        # 无法确认将要覆盖的内容，宁可不动
        pyautogui.press('right')
        time.sleep(0.1)
        return False

    if not _write_clipboard(new_text):
        return False

    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.2)
    _write_clipboard(old_clipboard)
    return True
