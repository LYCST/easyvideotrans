#!/usr/bin/env python3
"""
测试TTS错误处理
"""

import os
import shutil
from src.service.tts import get_tts_client

def test_tts_error_handling():
    """测试TTS错误处理"""
    print("=== 测试TTS错误处理 ===\n")
    
    # 创建测试SRT文件
    test_srt_content = """1
00:00:01,000 --> 00:00:04,000
这是一个测试字幕。

2
00:00:04,000 --> 00:00:07,000
用于测试TTS错误处理。
"""
    
    test_srt_file = "test_tts_error.srt"
    with open(test_srt_file, "w", encoding="utf-8") as f:
        f.write(test_srt_content)
    
    print(f"✓ 创建测试SRT文件: {test_srt_file}")
    
    # 测试目录
    test_output_dir = "./test_tts_error_output"
    
    # 清理之前的测试目录
    if os.path.exists(test_output_dir):
        shutil.rmtree(test_output_dir)
    
    print(f"\n📁 测试目录: {test_output_dir}")
    
    # 测试Edge TTS（预期会失败）
    print("\n1️⃣ 测试Edge TTS（预期会失败）...")
    try:
        edge_client = get_tts_client('edge', character="zh-CN-XiaoyiNeural")
        result = edge_client.srt_to_voice(test_srt_file, test_output_dir)
        print(f"   ✅ Edge TTS成功: {result}")
    except Exception as e:
        print(f"   ❌ Edge TTS失败（预期）: {e}")
        print("   📝 错误信息已正确返回")
    
    # 检查是否生成了文件
    print(f"\n📂 检查生成的文件:")
    if os.path.exists(test_output_dir):
        files = os.listdir(test_output_dir)
        if files:
            print(f"   ⚠️ 意外生成了 {len(files)} 个文件:")
            for file in files:
                print(f"     📄 {file}")
        else:
            print("   ✅ 没有生成任何文件（正确）")
    else:
        print("   ✅ 输出目录不存在（正确）")
    
    # 测试fallback TTS（预期也会失败）
    print("\n2️⃣ 测试fallback TTS（预期也会失败）...")
    fallback_output_dir = "./test_fallback_error_output"
    if os.path.exists(fallback_output_dir):
        shutil.rmtree(fallback_output_dir)
    
    try:
        fallback_client = get_tts_client('fallback', character="zh-CN-XiaoyiNeural")
        result = fallback_client.srt_to_voice(test_srt_file, fallback_output_dir)
        print(f"   ✅ Fallback TTS成功: {result}")
    except Exception as e:
        print(f"   ❌ Fallback TTS失败（预期）: {e}")
        print("   📝 错误信息已正确返回")
    
    print("\n=== 测试完成 ===")
    print("\n💡 说明:")
    print("1. TTS失败时会直接抛出异常")
    print("2. 不会生成静音占位符")
    print("3. 错误信息会正确返回给用户")
    print("4. 用户需要解决TTS服务问题才能继续")

if __name__ == "__main__":
    test_tts_error_handling()
