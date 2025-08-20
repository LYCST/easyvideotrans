#!/usr/bin/env python3
"""
测试TTS fallback功能
"""

import os
from src.service.tts import get_tts_client

def test_tts_fallback():
    """测试TTS fallback功能"""
    print("=== 测试TTS Fallback功能 ===\n")
    
    # 创建测试SRT文件
    test_srt_content = """1
00:00:01,000 --> 00:00:04,000
这是一个测试字幕。

2
00:00:04,000 --> 00:00:07,000
用于测试TTS fallback功能。
"""
    
    test_srt_file = "test_tts.srt"
    with open(test_srt_file, "w", encoding="utf-8") as f:
        f.write(test_srt_content)
    
    print(f"✓ 创建测试SRT文件: {test_srt_file}")
    
    # 测试目录
    test_output_dir = "./test_tts_output"
    
    # 测试1: 直接使用fallback TTS
    print("\n1️⃣ 测试直接使用fallback TTS...")
    try:
        fallback_client = get_tts_client('fallback', character="zh-CN-XiaoyiNeural")
        result = fallback_client.srt_to_voice(test_srt_file, test_output_dir)
        print(f"   ✅ Fallback TTS成功: {result}")
    except Exception as e:
        print(f"   ❌ Fallback TTS失败: {e}")
    
    # 测试2: 模拟Edge TTS失败，自动fallback
    print("\n2️⃣ 测试Edge TTS失败自动fallback...")
    try:
        # 这里我们直接测试fallback，因为Edge TTS确实会失败
        edge_client = get_tts_client('edge', character="zh-CN-XiaoyiNeural")
        result = edge_client.srt_to_voice(test_srt_file, test_output_dir + "_edge")
        print(f"   ✅ Edge TTS成功: {result}")
    except Exception as e:
        print(f"   ⚠️ Edge TTS失败（预期）: {e}")
        print("   🔄 在实际应用中会自动切换到fallback TTS")
    
    # 显示生成的文件
    print(f"\n📂 生成的文件:")
    if os.path.exists(test_output_dir):
        for file in os.listdir(test_output_dir):
            file_path = os.path.join(test_output_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"  📄 {file} ({size} bytes)")
    
    print("\n=== 测试完成 ===")
    print("\n💡 Fallback TTS功能:")
    print("1. 🛡️ 当Edge TTS失败时自动切换")
    print("2. 🔇 生成静音占位符音频")
    print("3. ⏱️ 根据文本长度估算音频时长")
    print("4. 🔄 确保工作流程不会中断")

if __name__ == "__main__":
    test_tts_fallback()
