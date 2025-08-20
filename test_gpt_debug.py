#!/usr/bin/env python3
"""
测试GPT翻译器的调试输出
"""

from src.service.translation import get_translator

def test_gpt_debug():
    """测试GPT翻译器的调试输出"""
    print("=== 测试GPT翻译器调试输出 ===\n")
    
    # 创建GPT翻译器
    translator = get_translator(
        'gpt', 
        api_key="sk_Ydc40RdtWUZ2IJN2fXHvWM8QIuHCrK",
        base_url="http://111.6.70.74:10115/v1/",
        model_name="gpt-oss:120b",
        cache_dir="./translation_cache"
    )
    
    # 测试翻译
    test_texts = [
        "Hello, this is a test message.",
        "The weather is nice today."
    ]
    
    print("🚀 开始翻译测试...")
    results = translator.translate_en_to_zh(test_texts)
    
    print(f"\n📋 翻译结果:")
    for i, (original, translated) in enumerate(zip(test_texts, results)):
        print(f"  {i+1}. {original} -> {translated}")

if __name__ == "__main__":
    test_gpt_debug()
