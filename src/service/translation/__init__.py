from .translator import Translator
from .deepl_translator import DeepLTranslator
from .google_translator import GoogleTranslator
from .gpt_translator import GPTTranslator

__all__ = [
    "Translator",
    "DeepLTranslator",
    "GoogleTranslator",
    "GPTTranslator",
    "get_translator",
]


def get_translator(translate_vendor, api_key=None, proxies=None, base_url=None, model_name=None):
    if translate_vendor == "google":
        return GoogleTranslator(proxy=proxies)
    elif translate_vendor == "deepl":
        if not api_key:
            raise ValueError("Missing translate key for DeepL.")
        return DeepLTranslator(key=api_key)
    elif "gpt" in translate_vendor:
        # 对于本地部署，api_key可以为空
        if translate_vendor == "gpt-local" and not api_key:
            api_key = ""  # 本地部署可能不需要API密钥
        
        # 使用传入的模型名称，如果没有则使用translate_vendor
        actual_model_name = model_name if model_name else translate_vendor
        
        return GPTTranslator(
            api_key=api_key, 
            model_name=actual_model_name, 
            base_url=base_url,
            proxies=proxies
        )
    else:
        raise ValueError("Unknown translation vendor.")
