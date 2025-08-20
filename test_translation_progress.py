#!/usr/bin/env python3
"""
测试翻译进度跟踪功能
"""

from src.service.translation import get_translator
import time

def test_translation_progress():
    """测试翻译进度跟踪功能"""
    print("=== 测试翻译进度跟踪功能 ===\n")
    
    # 创建GPT翻译器
    translator = get_translator(
        'gpt', 
        api_key="sk_Ydc40RdtWUZ2IJN2fXHvWM8QIuHCrK",
        base_url="http://111.6.70.74:10115/v1/",
        model_name="gpt-oss:120b",
        cache_dir="./translation_cache"
    )
    
    # 创建多个测试文本，模拟真实翻译场景
    test_texts = [
        "Hello, this is a test message.",
        "The weather is nice today.",
        "I love programming and coding.",
        "Machine learning is fascinating.",
        "Artificial intelligence is the future.",
        "Python is a great programming language.",
        "Deep learning has revolutionized AI.",
        "Natural language processing is complex.",
        "Computer vision is amazing.",
        "Data science is an exciting field."
    ]
    
    print(f"📝 准备翻译 {len(test_texts)} 个文本片段")
    print("⏰ 开始翻译，请观察进度输出...")
    
    start_time = time.time()
    
    # 设置较短的超时时间进行测试
    results = translator.translate_en_to_zh(test_texts, max_workers=5, timeout=120)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n⏱️ 总耗时: {total_time:.2f}秒")
    print(f"📊 平均每个请求: {total_time/len(test_texts):.2f}秒")
    
    print(f"\n📋 翻译结果:")
    for i, (original, translated) in enumerate(zip(test_texts, results)):
        print(f"  {i+1}. {original} -> {translated}")

if __name__ == "__main__":
    test_translation_progress()
