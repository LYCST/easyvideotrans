#!/usr/bin/env python3
"""
演示基于video_id的简单缓存机制
"""

import os
import json
from src.service.translation import get_translator

def demo_simple_cache():
    """演示基于video_id的缓存机制"""
    print("=== 基于video_id的缓存机制演示 ===\n")
    
    # 设置缓存目录
    cache_dir = "./demo_simple_cache"
    
    print(f"📁 缓存目录: {cache_dir}")
    
    # 模拟不同的翻译场景
    scenarios = [
        {
            "name": "Google翻译",
            "translator": "google",
            "source_file": "output/Am54LhN2NLk_en_merged.srt",
            "output_file": "output/Am54LhN2NLk_zh_merged.srt"
        },
        {
            "name": "GPT翻译",
            "translator": "gpt-oss:120b",
            "source_file": "output/Am54LhN2NLk_en_merged.srt",
            "output_file": "output/Am54LhN2NLk_zh_merged.srt"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}️⃣ {scenario['name']}...")
        
        try:
            if scenario['translator'] == 'google':
                translator = get_translator("google", cache_dir=cache_dir)
            else:
                translator = get_translator("gpt-oss:120b", 
                                          api_key="sk_Ydc40RdtWUZ2IJN2fXHvWM8QIuHCrK",
                                          base_url="http://111.6.70.74:10115/v1/",
                                          model_name="gpt-oss:120b",
                                          cache_dir=cache_dir)
            
            # 执行翻译
            result = translator.translate_srt(scenario['source_file'], scenario['output_file'])
            print(f"   ✅ 翻译完成: {result}")
            
        except Exception as e:
            print(f"   ❌ 翻译失败: {e}")
    
    # 显示缓存文件
    print(f"\n📂 缓存文件:")
    if os.path.exists(cache_dir):
        for file in os.listdir(cache_dir):
            if file.endswith('.json'):
                print(f"  📄 {file}")
                cache_path = os.path.join(cache_dir, file)
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    print(f"     📊 缓存条目数: {len(cache_data)}")
                    if cache_data:
                        print(f"     💬 示例翻译: {cache_data[0][:30]}...")
                except Exception as e:
                    print(f"     ❌ 读取缓存失败: {e}")
    else:
        print("  ❌ 缓存目录不存在")
    
    print("\n=== 演示完成 ===")
    print("\n💡 新缓存机制的优势:")
    print("1. 🎯 基于video_id，不依赖文件内容")
    print("2. 🔄 即使文件被修改，缓存仍然有效")
    print("3. 📝 缓存文件名直观易懂")
    print("4. ⚡ 支持快速切换不同翻译器")
    print("5. 💾 每种翻译器独立缓存")

if __name__ == "__main__":
    demo_simple_cache()
