# Zh2En - 实时中文转英文翻译工具

Windows 平台上的全局中译英小工具。在任意输入框中输入中文，**0.5 秒内连按 3 次空格**，程序会截取光标前的文本（默认取当前行前缀），调用 LLM 翻译并原位替换；在 **3 秒内**再次连按 3 次空格可在译文和原文之间切换。

> 当前为 MVP 版本：命令行程序，无 GUI/托盘，仅缓存最近一次翻译。

## 功能特性

- **全局触发**：基于 `keyboard` 全局键盘钩子，在浏览器、编辑器、聊天软件等输入框中均可使用。
- **原位替换**：翻译结果直接替换选区，不弹出窗口。
- **原文/译文切换**：在有效时间窗口内再次连按 3 次空格，可在缓存的两个版本之间来回切换。
- **多后端**：支持 OpenAI Chat Completions 兼容接口和 Ollama Chat API。
- **中文检测**：截取文本包含基本汉字（`U+4E00`–`U+9FFF`）时才发起翻译。
- **选区兜底**：优先 `Shift+Home` 选取当前行前缀；失败时回退到 `Ctrl+A` 全选。
- **剪贴板保护**：复制前写入哨兵值，确认剪贴板确实变化；操作结束恢复原剪贴板。
- **替换前核对**：粘贴前重新复制当前选区并与预期文本比对，不一致就放弃替换，避免把译文插入原文前面。
- **思考段清理**：自动移除模型输出中的 `<think>...</think>`，兼容 qwen3 等思考模型。
- **轻量后台**：无 GUI 常驻，控制台输出翻译状态，按 `Ctrl+Q` 退出。

## 运行环境

- Windows 10/11
- Python 3.12（推荐）
- `start.bat` 固定使用 `py -3.12`；手动运行代码可用 Python 3.8+，但 `keyboard` 对 Python 3.14 支持不完善，建议使用 3.12。

## 安装

### 方式一：使用 start.bat（推荐）

在项目目录下双击 `start.bat`，或在命令行运行：

```bat
start.bat
```

脚本会自动完成：

1. 检查 `py -3.12` 是否可用；
2. 首次运行时创建 `venv` 虚拟环境；
3. 首次运行时安装 `requirements.txt` 中的依赖（通过 `venv\.installed` 标记）；
4. 以 UTF-8 输出启动 `main.py`。

> 如果修改了 `requirements.txt`，删除 `venv\.installed` 后重新运行脚本即可重新安装。

### 方式二：手动安装

```bat
cd zh2en

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python main.py
```

### 依赖说明

| 依赖 | 用途 |
| --- | --- |
| `keyboard` | 注册全局空格键和 `Ctrl+Q` 热键 |
| `pyautogui` | 模拟 `Shift+Home`、`Ctrl+A`、`Ctrl+C`、`Ctrl+V` |
| `pyperclip` | 读取和写入剪贴板 |
| `requests` | 调用 OpenAI/Ollama HTTP API |
| `pywin32` | Windows 平台依赖；`requirements.txt` 中保留，当前代码未直接 `import` |

## 配置

程序启动时读取**工作目录**下的 `config.json`。文件不存在时，`config.py` 会用默认值创建；已有配置缺少字段时，自动补默认值。修改配置后需要重启程序。

> 当前仓库中的 `config.json` 指向本地 Ollama（`qwen3:latest`）。使用前请确认 Ollama 已启动；如果要使用 OpenAI 或兼容服务，请按下方示例替换配置。

> 手动启动时请先 `cd` 到项目目录，否则会在其他目录读取/生成 `config.json`。`start.bat` 已自动切换到脚本所在目录。

### OpenAI / OpenAI 兼容接口

```json
{
    "api_type": "openai",
    "endpoint": "https://api.openai.com/v1/chat/completions",
    "api_key": "sk-your-key",
    "model": "gpt-4o-mini",
    "time_window_ms": 500,
    "toggle_window_s": 3,
    "system_prompt": "You are a Chinese-to-English translator. Translate the following Chinese text to English. If the text contains non-Chinese parts, keep them unchanged. Only return the translation, no explanation or quotes.",
    "max_tokens": 2048,
    "temperature": 0.3
}
```

`api_type` 只要不是 `ollama`，都会按 OpenAI Chat Completions 协议发送请求，因此也可以指向兼容该协议的第三方服务或本地服务。

### Ollama

```json
{
    "api_type": "ollama",
    "endpoint": "http://localhost:11434/api/chat",
    "api_key": "",
    "model": "qwen3:latest",
    "time_window_ms": 500,
    "toggle_window_s": 3,
    "system_prompt": "You are a Chinese-to-English translator. Translate the following Chinese text to English. If the text contains non-Chinese parts, keep them unchanged. Only return the translation, no explanation or quotes.",
    "max_tokens": 2048,
    "temperature": 0.3
}
```

注意：

- Ollama 端点必须使用 **`/api/chat`**。代码发送的是 `messages` 并读取 `message.content`，与 `/api/generate` 不兼容。
- 请先启动 Ollama 并拉取模型，例如 `ollama pull qwen3`。
- 使用思考模型时，程序会移除 `<think>...</think>` 内容；建议在使用前确认模型输出稳定。

### 配置项说明

| 配置项 | 说明 | 默认值 |
| --- | --- | --- |
| `api_type` | `ollama` 走 Ollama Chat API；其他值走 OpenAI Chat Completions | `openai` |
| `endpoint` | 完整的 API 地址 | `https://api.openai.com/v1/chat/completions` |
| `api_key` | 非空时作为 `Authorization: Bearer ...` 发送；Ollama 可留空 | 空 |
| `model` | 模型名称 | `gpt-4o-mini` |
| `time_window_ms` | 3 次空格触发的时间窗口（毫秒，滚动计算） | `500` |
| `toggle_window_s` | 翻译成功或切换操作后的可切换时间窗口（秒） | `3` |
| `system_prompt` | 翻译系统提示词 | 中译英提示 |
| `max_tokens` | 最大输出 token；OpenAI 映射 `max_tokens`，Ollama 映射 `num_predict` | `2048` |
| `temperature` | 采样温度 | `0.3` |

- 请求超时固定为：OpenAI 30 秒，Ollama 60 秒，MVP 暂不可配置。
- `api_key` 以明文保存在 `config.json` 中，请勿把真实密钥提交到版本库。

## 使用方法

### 启动

```bat
start.bat
```

或手动启动：

```bat
venv\Scripts\activate
python main.py
```

启动后控制台会显示 API 类型、模型、端点和使用提示。窗口需要保持运行，可以最小化。

### 翻译

1. 将光标放到目标输入框内，输入中文。
2. 在 `time_window_ms`（默认 500 毫秒）内连按 3 次空格。
3. 程序截取从光标到当前行行首的文本（失败时全选整个输入框），去除首尾空白后检查是否包含中文。
4. 包含中文时调用配置的 LLM，替换前核对通过后原位替换；控制台分别输出 `[翻译]` 和 `[结果]`。
5. 触发用的 3 个空格会包含在选区中，随原文一起被替换，不会残留在结果里。

### 切换原文/译文

- 在最后一次翻译成功或切换操作后的 `toggle_window_s`（默认 3 秒）内，再次连按 3 次空格。
- 切换前会确认当前截取到的文本与界面正在显示的文本一致；一致才切换，避免在错误位置替换。
- 每成功切换一次，3 秒窗口会重新计时，因此可以在窗口内反复切换。
- 超过 3 秒后，3 次空格会被当作“新文本”处理：
  - 当前是中文：重新翻译；
  - 当前是英文译文：不含中文，控制台提示 `[提示] 未检测到中文`，缓存被清空，**此时无法再切回原文**。
- 如果替换前核对失败，程序不会修改输入框，并输出提示。

### 退出

按 `Ctrl+Q` 退出。该热键不会拦截按键，目标应用如果也绑定了 `Ctrl+Q`，可能同时响应。

### 示例

```text
输入：你好世界
操作：500 毫秒内按 3 次空格
结果：Hello World

操作：3 秒内再按 3 次空格
结果：你好世界
```

> 建议在单行、内容较简单的输入框中把光标放在句末使用；多行或混合内容会受选区范围限制，见“已知限制”。

## 工作原理

### 处理流程

```text
连按 3 次空格（≤ time_window_ms）
        │
        ▼
KeyboardMonitor 记录时间戳并触发回调（独立线程）
        │
        ▼
extract_text_before_cursor()
  ├─ Shift+Home → Ctrl+C → 剪贴板是否变化？
  │                           └─ 否 → Ctrl+A → Ctrl+C
  ├─ 恢复原剪贴板
  └─ strip() 去掉触发空格和首尾空白
        │
        ├─ 有缓存 + 在 toggle_window_s 内 + 文本等于当前显示 → 替换为另一版本
        │
        ├─ 不含中文 → 提示并清空缓存
        │
        ▼
TranslationEngine.translate()
  ├─ OpenAI Chat Completions
  └─ Ollama /api/chat
        │
        ▼
replace_text()
  ├─ 用相同策略重选 → Ctrl+C → 与预期文本比对
  ├─ 不一致 → 回退 Ctrl+A 再比对 → 仍不一致则放弃
  └─ 一致 → 写入剪贴板 → Ctrl+V → 恢复原剪贴板
        │
        ▼
StateManager 更新原文/译文缓存和切换窗口
```

### 模块说明

| 文件 | 职责 |
| --- | --- |
| `main.py` | 程序入口，串联监听、截取、翻译、替换；中文检测和切换决策 |
| `config.py` | 默认配置、读取 `config.json`、补齐缺失字段、生成默认配置 |
| `keyboard_monitor.py` | 全局空格监听；时间窗口内计数；触发回调线程；处理期间屏蔽新触发 |
| `text_extractor.py` | 选区/复制/校验/粘贴；剪贴板哨兵和恢复 |
| `translation_engine.py` | OpenAI/Ollama 请求；清理 `<think>` 输出 |
| `state_manager.py` | 原文/译文缓存、当前显示状态、切换窗口、处理中标志 |
| `start.bat` | Windows 启动脚本：检查 Python、创建虚拟环境、安装依赖、启动程序 |

### 关键防护

- **剪贴板哨兵**：复制前先写入唯一哨兵值，只有剪贴板发生变化才认为复制成功，避免把旧剪贴板内容当成刚截取的文本。
- **替换前核对**：粘贴前重新复制选区，确认选区正好覆盖预期原文；无法确认时宁可不动。
- **处理中屏蔽**：翻译期间 `_is_sending` 为真，空格事件不会再次触发，避免处理期间重复触发。
- **失败回滚**：切换后替换失败会把显示状态回滚；截取失败或未检测到中文会清空缓存。

## 已知限制与注意事项

### 选区与替换范围

- 首选 `Shift+Home`，只选中**光标到当前行行首**的内容，不是任意“光标前全部文本”。
- 如果 `Shift+Home` 无法建立选区，会退回到 `Ctrl+A`，此时范围是整个输入控件。
- 多行文本中光标位于最后一行时，通常只截取最后一行前缀；多行译文在切换时也可能因只能选中最后一行而无法与缓存全文匹配。
- 建议在单行输入框、句末光标、内容干净的位置使用。

### 触发与缓存

- 3 秒切换窗口从**最后一次翻译成功或切换操作**开始计算；超时后不能切回原文。
- 只有一组原文/译文缓存；翻译新内容会覆盖旧缓存。
- 翻译处理期间的空格不会计入 3 次触发。
- 任何场景下快速输入 3 个空格都会触发；如果误触发频繁，可减小 `time_window_ms`（例如 300）。
- 中文检测只覆盖基本汉字区 `U+4E00`–`U+9FFF`，扩展区汉字可能无法触发。
- 未检测到中文、截取失败或替换核对失败时，可能会清空缓存。

### 输入环境

- 密码框、部分自绘控件、终端/游戏/远程桌面等环境可能无法复制或粘贴。
- 对以管理员权限运行的目标程序，非管理员运行的 Zh2En 可能收不到键盘事件或无法注入按键；必要时以相同权限运行。
- 中文输入法请先完成上屏，再按 3 次空格。
- `Ctrl+Q` 是普通全局热键，不会吞掉按键。

### 剪贴板

- 截取和替换期间会临时写入哨兵值、译文，操作结束后恢复原剪贴板；剪贴板管理器可能记录这些中间值。
- 如果剪贴板被其他程序锁定，复制/粘贴可能失败，程序会提示并尽量避免修改原文。

### 隐私

- 文本不会写入本地历史文件；但会发送到配置的 `endpoint`。
- 使用远程 OpenAI 兼容服务时，文本会离开本机；使用本地 Ollama 时不出本机。
- `config.json` 中的 API Key 为明文，请妥善保管。

### 模型输出

- 当前只清理 `<think>...</think>` 和未闭合的 `<think>` 段，没有对空译文做额外拦截。
- 如果模型返回空字符串，替换逻辑仍可能执行并清空选区（取决于目标控件对空剪贴板的处理）；请关注控制台 `[结果]`，并使用输出稳定的模型。
- OpenAI 兼容接口需要接受 `messages`、`max_tokens`、`temperature` 等请求字段。

## 常见问题

**Q: 连按 3 次空格没有反应？**

- 确认 3 次按键在 `time_window_ms`（默认 500 毫秒）内完成。
- 确认目标输入框有焦点，且光标前有可截取的文字。
- 确认截取到的文本包含基本汉字（`U+4E00`–`U+9FFF`）。
- 查看控制台是否有“无法截取文本”“未检测到中文”或 API 错误提示。

**Q: 为什么切不回原文？**

- 切换只在最后一次翻译成功或切换操作后的 `toggle_window_s`（默认 3 秒）内有效。
- 如果当前输入框里的文本与缓存显示文本不一致（例如手动编辑过），不会切换。
- 多行译文可能因 `Shift+Home` 只能选中最后一行而核对失败。
- 超时后再按 3 次空格会按新文本处理；英文译文会被判定为“未检测到中文”，缓存随即清空。

**Q: 只翻译了半句话 / 翻译范围不对？**

- 首选策略是 `Shift+Home`，只会选到当前行行首。把光标放到句末，或使用单行输入框。
- 兜底策略是 `Ctrl+A`，会选中整个控件；如果控件里有其他内容，替换前的核对可能失败。

**Q: 提示 API 请求失败？**

- 检查 `endpoint`、`model`、`api_key` 是否正确。
- Ollama 需先启动服务并拉取模型，端点应为 `/api/chat`。
- 远程服务需保证网络可达；超时为 OpenAI 30 秒、Ollama 60 秒。
- 某些新版 OpenAI 模型不接受 `max_tokens` 字段，可换用兼容模型或调整代码。

**Q: 能翻译成其他语言吗？**

- 可以。修改 `system_prompt`，例如改为“Translate Chinese to Japanese”，并同步调整触发/切换的使用习惯。

**Q: 程序会保存我的输入吗？**

- 不会写入本地历史文件。翻译时会临时使用剪贴板；文本会发送到你配置的 API。使用本地 Ollama 时不出本机。

**Q: 支持哪些输入框？**

- 大多数标准文本输入控件可用。密码框、部分自绘控件、提权窗口、终端/游戏等可能不可用。

## 开发计划

### 已实现（MVP）

- [x] 全局键盘监听与 3 次空格触发
- [x] 文本截取：`Shift+Home` 优先，`Ctrl+A` 兜底
- [x] 剪贴板哨兵验证与原剪贴板恢复
- [x] 替换前选区内容核对
- [x] OpenAI / OpenAI 兼容接口
- [x] Ollama `/api/chat`
- [x] 中文检测
- [x] 原文/译文缓存与 3 秒切换窗口
- [x] `<think>` 思考段清理
- [x] JSON 配置文件与默认值补齐
- [x] `Ctrl+Q` 退出

### 计划功能

- [ ] 图形化配置界面
- [ ] 系统托盘图标
- [ ] 翻译历史记录
- [ ] 多语言支持
- [ ] 自定义快捷键 / 触发键
- [ ] 批量翻译模式
- [ ] 翻译缓存优化
- [ ] 空译文与异常响应保护
- [ ] 单元测试与自动化测试
- [ ] 打包为独立 exe

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request。
