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
        
        # 移除调试打印，只保留进度信息
        
        response = requests.post(api_url, headers=headers, json=payload, proxies=self.proxies, timeout=60)
        
        # 检查响应状态
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
        
        try:
            return response.json()
        except json.JSONDecodeError as e:
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
            if isinstance(results, dict) and 'message' in results:
                text_result = results['message'].get('content', '')
            else:
                text_result = str(results)
        
        # 处理markdown格式
        if '```' in text_result:
            text_result = text_result.split('```')[1]
            text_result = text_result.strip().replace("\n", "").replace("translated text", "").replace("```", "")
        
        # 处理本地部署可能没有usage信息的情况
        usage = results.get('usage', {})
        model = results.get('model', self.model_name)
        
        # 移除统计信息打印，只保留进度信息
        
        result_dict = {"text_result": text_result,
                       "model": model,
                       "usage": usage,
                       "all_usage": usage.get('prompt_tokens', 0) + usage.get('completion_tokens', 0) * 3 if usage else 0,
                       'time': et - st}
        return result_dict

    def translate_en_to_zh(self, texts, max_tokens=1200, max_workers=30, timeout=300):
        """
        翻译英文文本到中文
        
        Args:
            texts: 要翻译的文本列表
            max_tokens: 最大token数
            max_workers: 最大并发工作线程数
            timeout: 超时时间（秒），默认5分钟
        """
        print(f"🚀 开始翻译 {len(texts)} 个文本片段，最大并发数: {max_workers}，超时时间: {timeout}秒")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            futures = {executor.submit(self.process_text, text, max_tokens): i for i, text in enumerate(texts)}
            results = [None] * len(texts)  # 预分配结果列表
            completed_count = 0
            failed_indices = []  # 记录失败的索引
            
            # 处理完成的任务，带超时
            try:
                for future in concurrent.futures.as_completed(futures, timeout=timeout):
                    try:
                        result = future.result()
                        index = futures[future]
                        results[index] = result
                        completed_count += 1
                        
                        # 打印进度
                        remaining = len(texts) - completed_count
                        print(f"✅ 完成 {completed_count}/{len(texts)} 个翻译请求，还剩 {remaining} 个请求")
                        
                        if remaining == 0:
                            print("🎉 所有翻译请求已完成！")
                        
                    except Exception as e:
                        index = futures[future]
                        print(f"❌ 第 {index + 1} 个翻译请求失败: {e}")
                        # 记录失败的索引，稍后重试
                        failed_indices.append(index)
                        completed_count += 1
                        
            except concurrent.futures.TimeoutError:
                print(f"⏰ 翻译超时！已完成 {completed_count}/{len(texts)} 个请求")
                # 取消未完成的任务
                for future in futures:
                    if not future.done():
                        future.cancel()
                        print(f"❌ 取消未完成的翻译请求")
                
                # 记录未完成的任务索引
                for future, index in futures.items():
                    if results[index] is None:
                        failed_indices.append(index)
                        print(f"⚠️ 第 {index + 1} 个请求因超时而失败")
            
            # 处理失败的翻译请求，尝试重试
            if failed_indices:
                print(f"🔄 开始重试 {len(failed_indices)} 个失败的翻译请求...")
                retry_results = self._retry_failed_translations(texts, failed_indices, max_tokens)
                
                # 更新失败的结果
                for i, failed_index in enumerate(failed_indices):
                    if retry_results[i]:
                        results[failed_index] = retry_results[i]
                        print(f"✅ 第 {failed_index + 1} 个请求重试成功")
                    else:
                        # 重试3次都失败了，直接使用原文
                        original_text = texts[failed_index]
                        results[failed_index] = {
                            "text_result": original_text,
                            "model": self.model_name,
                            "usage": {},
                            "all_usage": 0,
                            "time": 0
                        }
                        print(f"❌ 第 {failed_index + 1} 个请求重试3次后仍失败，使用原文")
        
        return [result['text_result'] for result in results]

    def _retry_failed_translations(self, texts, failed_indices, max_tokens, max_retries=3):
        """
        重试失败的翻译请求
        
        Args:
            texts: 原始文本列表
            failed_indices: 失败的索引列表
            max_tokens: 最大token数
            max_retries: 最大重试次数
            
        Returns:
            list: 重试结果列表
        """
        retry_results = [None] * len(failed_indices)
        
        for retry_attempt in range(max_retries):
            print(f"🔄 第 {retry_attempt + 1} 次重试...")
            
            for i, failed_index in enumerate(failed_indices):
                if retry_results[i] is None:  # 只重试尚未成功的
                    try:
                        # 增加延迟避免频率限制
                        import time
                        time.sleep(1)
                        
                        result = self.process_text(texts[failed_index], max_tokens)
                        retry_results[i] = result
                        print(f"✅ 重试成功: 第 {failed_index + 1} 个请求")
                        
                    except Exception as e:
                        print(f"❌ 重试失败: 第 {failed_index + 1} 个请求 - {e}")
                        if retry_attempt == max_retries - 1:  # 最后一次重试
                            retry_results[i] = None
        
        return retry_results
