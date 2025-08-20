from .translator import Translator
from pygtrans import Translate


class GoogleTranslator(Translator):
    def __init__(self, proxy="", cache_dir="./translation_cache"):
        super().__init__(cache_dir)
        self.proxy = proxy
        if proxy == "":
            self.client = Translate()
        else:
            self.client = Translate(proxies={'https': self.proxy})
    
    def get_translator_name(self):
        return "google"

    def translate_en_to_zh(self, texts):
        texts_response = self.client.translate(texts, target='zh')
        texts_translated = [txtResponse.translatedText for txtResponse in texts_response]
        return texts_translated
