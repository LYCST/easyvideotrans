from abc import ABC, abstractmethod
import srt
import os
import json
import hashlib
import shutil


class Translator(ABC):
    def __init__(self, cache_dir="./translation_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    @abstractmethod
    def translate_en_to_zh(self, texts: list) -> list:
        pass
    
    def _extract_video_id(self, file_path):
        """从文件路径中提取video_id"""
        filename = os.path.basename(file_path)
        # 支持多种文件名格式
        if '_en_merged.srt' in filename:
            return filename.replace('_en_merged.srt', '')
        elif '_en.srt' in filename:
            return filename.replace('_en.srt', '')
        elif '_merged.srt' in filename:
            return filename.replace('_merged.srt', '')
        else:
            # 如果没有匹配的模式，使用文件名（不含扩展名）
            return os.path.splitext(filename)[0]
    
    def _get_cache_key(self, source_file_path, translator_name):
        """生成缓存键，基于video_id和翻译器名称"""
        video_id = self._extract_video_id(source_file_path)
        return f"{video_id}_{translator_name}"
    
    def _get_cache_path(self, cache_key):
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _load_cached_translation(self, cache_key):
        """从缓存加载翻译结果"""
        cache_path = self._get_cache_path(cache_key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load cache from {cache_path}: {e}")
        return None
    
    def _save_cached_translation(self, cache_key, translated_content_list):
        """保存翻译结果到缓存"""
        cache_path = self._get_cache_path(cache_key)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(translated_content_list, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save cache to {cache_path}: {e}")
    
    def get_translator_name(self):
        """获取翻译器名称，子类可以重写此方法"""
        return self.__class__.__name__.lower()

    def translate_srt(self, source_file_name_and_path, output_file_name_and_path):
        translator_name = self.get_translator_name()
        
        # 生成缓存键
        cache_key = self._get_cache_key(source_file_name_and_path, translator_name)
        
        # 尝试从缓存加载翻译结果
        cached_translation = self._load_cached_translation(cache_key)
        
        if cached_translation is not None:
            print(f"Using cached translation for {translator_name} (video_id: {self._extract_video_id(source_file_name_and_path)})")
            content_list = cached_translation
        else:
            print(f"Translating with {translator_name} (no cache found)")
            # 执行翻译
            content_list = self._perform_translation(source_file_name_and_path)
            # 保存翻译结果到缓存
            self._save_cached_translation(cache_key, content_list)
        
        # 生成最终的字幕文件
        self._generate_output_file(source_file_name_and_path, output_file_name_and_path, content_list)
        return True
    
    def _perform_translation(self, source_file_name_and_path):
        """执行翻译操作"""
        srt_content = open(source_file_name_and_path, "r", encoding="utf-8").read()
        sub_generator = srt.parse(srt_content)
        sub_title_list = list(sub_generator)
        content_list = [subTitle.content for subTitle in sub_title_list]
        
        # 执行翻译
        content_list = self.translate_en_to_zh(content_list)
        return content_list
    
    def _generate_output_file(self, source_file_name_and_path, output_file_name_and_path, content_list):
        """生成输出文件"""
        # 重新读取源文件以获取原始字幕结构
        srt_content = open(source_file_name_and_path, "r", encoding="utf-8").read()
        sub_generator = srt.parse(srt_content)
        sub_title_list = list(sub_generator)
        
        # 应用翻译结果
        for i in range(len(sub_title_list)):
            sub_title_list[i].content = content_list[i]

        # 生成最终的字幕文件
        srt_content = srt.compose(sub_title_list)
        with open(output_file_name_and_path, "w", encoding="utf-8") as file:
            file.write(srt_content)
