import requests
import json
import concurrent.futures
import time
import tenacity
from .translator import Translator

DEFAULT_URL = "https://api.openai.com/v1/"
GHATGPT_TERMS_FILE = "../../../configs/gpt_terms.json"


class GPTTranslator(Translator):
    def __init__(self, api_key, model_name="gpt-3.5-turbo-0125", base_url=None, proxies=None, terms_file=GHATGPT_TERMS_FILE, cache_dir="./translation_cache"):
        super().__init__(cache_dir)
        self.api_key = api_key
        self.base_url = base_url if base_url else DEFAULT_URL
        self.model_name = model_name
        self.proxies = proxies
        self.terms = {}
        self.load_terms(terms_file)
    
    def get_translator_name(self):
        return f"gpt_{self.model_name.replace(':', '_').replace('-', '_')}"

    def load_terms(self, terms_file):
        try:
            with open(terms_file, 'r', encoding='utf-8') as f:
                self.terms = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Terms file {terms_file} not found, using empty terms dictionary")
            self.terms = {}

    @tenacity.retry(wait=tenacity.wait_exponential(multiplier=1, min=3, max=6),
                    stop=tenacity.stop_after_attempt(3),
                    reraise=True)
    def request_llm(self, system_text="",
                    assistant_text='',
                    user_text="",
                    max_tokens=1200):
        headers = {
            "Content-Type": "application/json",
        }
        
        # 只有在使用OpenAI官方API时才添加Authorization头
        if self.base_url == DEFAULT_URL or "openai.com" in self.base_url:
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.api_key and self.api_key != "":  # 本地部署可能需要API密钥
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": system_text,
                },
                {
                    "role": "assistant",
                    "content": assistant_text,
                },
                {
                    "role": "user",
                    "content": user_text,
                }
            ],
            "max_tokens": max_tokens
        }
        
        # 确保URL以/结尾
        api_url = self.base_url.rstrip('/') + "/chat/completions"
        
        print(f"Making API request to: {api_url}")
        print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        response = requests.post(api_url, headers=headers, json=payload, proxies=self.proxies)
        
        # 检查响应状态
        if response.status_code != 200:
            print(f"API request failed with status {response.status_code}: {response.text}")
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
        
        try:
            return response.json()
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {response.text}")
            raise Exception(f"Invalid JSON response: {e}")

    def process_text(self, text, max_tokens):
        st = time.time()
        system_text = ("You are a professional subtitle translator that translates English subtitles to idiomatic "
                       "Chinese subtitles.")
        assistant_text = f"Here are some key terms and their translations:\n{json.dumps(self.terms, ensure_ascii=False)}"
        user_text = f"""You are a professional video subtitle translator.
        You need to translate a segment of subtitles and correct obvious word errors based on the context.
        Additionally, you need to consider some translation rules for terminology provided above.
        Below is the subtitle segment that needs to be translated:\n\n
        ```
        {text}
        ```
        your output format should be:
        ```
        translated text
        ```
        """

        results = self.request_llm(system_text=system_text,
                                   assistant_text=assistant_text,
                                   user_text=user_text,
                                   max_tokens=max_tokens)
        et = time.time()
        
        # 处理Ollama API响应格式
        if 'choices' in results and len(results['choices']) > 0:
            text_result = results['choices'][0]['message']['content']
        elif 'response' in results:
            # Ollama API格式
            text_result = results['response']
        else:
            # 如果都不匹配，尝试其他可能的格式
            print(f"Warning: Unexpected API response format: {results}")
            if isinstance(results, dict) and 'message' in results:
                text_result = results['message'].get('content', '')
            else:
                text_result = str(results)
        if '```' in text_result:
            text_result = text_result.split('```')[1]
            text_result = text_result.strip().replace("\n", "").replace("translated text", "").replace("```", "")
        
        # 处理本地部署可能没有usage信息的情况
        usage = results.get('usage', {})
        model = results.get('model', self.model_name)
        
        result_dict = {"text_result": text_result,
                       "model": model,
                       "usage": usage,
                       "all_usage": usage.get('prompt_tokens', 0) + usage.get('completion_tokens', 0) * 3 if usage else 0,
                       'time': et - st}
        return result_dict

    def translate_en_to_zh(self, texts, max_tokens=1200, max_workers=30):
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.process_text, text, max_tokens) for text in texts]
            results = [future.result() for future in futures]
        return [result['text_result'] for result in results]
