import deepl
from .translator import Translator


class DeepLTranslator(Translator):
    def __init__(self, key, cache_dir="./translation_cache"):
        super().__init__(cache_dir)
        self.key = key
    
    def get_translator_name(self):
        return "deepl"

    def translate_en_to_zh(self, texts):
        dl_translator = deepl.Translator(self.key)
        textEn = "\n".join(texts)
        textZh = dl_translator.translate_text(textEn, target_lang="zh")
        textsZh = str(textZh).split("\n")
        return textsZh
