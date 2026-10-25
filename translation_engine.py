import re
import requests


class TranslationEngine:
    def __init__(self, config):
        self.api_type = config['api_type']
        self.endpoint = config['endpoint']
        self.api_key = config.get('api_key', '')
        self.model = config['model']
        self.system_prompt = config.get('system_prompt', '')
        self.max_tokens = config.get('max_tokens', 2048)
        self.temperature = config.get('temperature', 0.3)

    def translate(self, text):
        if self.api_type == 'ollama':
            return self._translate_ollama(text)
        else:
            return self._translate_openai(text)

    def _clean_response(self, text):
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        text = re.sub(r'<think>.*', '', text, flags=re.DOTALL)
        return text.strip()

    def _translate_openai(self, text):
        headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        data = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': text}
            ],
            'max_tokens': self.max_tokens,
            'temperature': self.temperature
        }

        response = requests.post(self.endpoint, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return self._clean_response(result['choices'][0]['message']['content'])

    def _translate_ollama(self, text):
        data = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': text}
            ],
            'stream': False,
            'options': {
                'temperature': self.temperature,
                'num_predict': self.max_tokens
            }
        }

        response = requests.post(self.endpoint, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        return self._clean_response(result['message']['content'])
