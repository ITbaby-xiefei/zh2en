import json
import os

DEFAULT_CONFIG = {
    "api_type": "openai",
    "endpoint": "https://api.openai.com/v1/chat/completions",
    "api_key": "",
    "model": "gpt-4o-mini",
    "time_window_ms": 500,
    "toggle_window_s": 3,
    "system_prompt": "You are a Chinese-to-English translator. Translate the following Chinese text to English. If the text contains non-Chinese parts, keep them unchanged. Only return the translation, no explanation or quotes.",
    "max_tokens": 2048,
    "temperature": 0.3
}

CONFIG_FILE = "config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()


def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
