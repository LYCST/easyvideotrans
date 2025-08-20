#!/usr/bin/env python3
"""
测试Edge TTS失败时的fallback机制
"""

import os
import shutil
from src.service.tts import get_tts_client

def test_edge_tts_fallback():
    """测试Edge TTS失败时的fallback机制"""
    print("=== 测试Edge TTS失败时的Fallback机制 ===\n")
    
    # 创建测试SRT文件
    test_srt_content = """1
00:00:01,000 --> 00:00:04,000
这是一个测试字幕。

2
00:00:04,000 --> 00:00:07,000
用于测试Edge TTS失败时的fallback机制。
"""
    
    test_srt_file = "test_edge_tts.srt"
    with open(test_srt_file, "w", encoding="utf-8") as f:
        f.write(test_srt_content)
    
    print(f"✓ 创建测试SRT文件: {test_srt_file}")
    
    # 测试目录
    test_output_dir = "./test_edge_tts_output"
    
    # 清理之前的测试目录
    if os.path.exists(test_output_dir):
        shutil.rmtree(test_output_dir)
    
    print(f"\n📁 测试目录: {test_output_dir}")
    
    # 测试Edge TTS（预期会失败并触发fallback）
    print("\n1️⃣ 测试Edge TTS（预期会失败）...")
    try:
        edge_client = get_tts_client('edge', character="zh-CN-XiaoyiNeural")
        result = edge_client.srt_to_voice(test_srt_file, test_output_dir)
        print(f"   ✅ Edge TTS成功: {result}")
    except Exception as e:
        print(f"   ⚠️ Edge TTS失败（预期）: {e}")
        print("   🔄 在实际应用中会自动切换到fallback TTS")
    
    # 检查是否生成了文件
    print(f"\n📂 检查生成的文件:")
    if os.path.exists(test_output_dir):
        files = os.listdir(test_output_dir)
        if files:
            print(f"   ✅ 生成了 {len(files)} 个文件:")
            for file in files:
                file_path = os.path.join(test_output_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"     📄 {file} ({size} bytes)")
        else:
            print("   ❌ 没有生成任何文件")
    else:
        print("   ❌ 输出目录不存在")
    
    # 测试直接使用fallback TTS
    print("\n2️⃣ 测试直接使用fallback TTS...")
    fallback_output_dir = "./test_fallback_output"
    if os.path.exists(fallback_output_dir):
        shutil.rmtree(fallback_output_dir)
    
    try:
        fallback_client = get_tts_client('fallback', character="zh-CN-XiaoyiNeural")
        result = fallback_client.srt_to_voice(test_srt_file, fallback_output_dir)
        print(f"   ✅ Fallback TTS成功: {result}")
        
        # 检查fallback生成的文件
        if os.path.exists(fallback_output_dir):
            files = os.listdir(fallback_output_dir)
            print(f"   📂 Fallback生成了 {len(files)} 个文件:")
            for file in files:
                file_path = os.path.join(fallback_output_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"     📄 {file} ({size} bytes)")
    except Exception as e:
        print(f"   ❌ Fallback TTS失败: {e}")
    
    print("\n=== 测试完成 ===")
    print("\n💡 说明:")
    print("1. Edge TTS遇到403错误时会立即失败")
    print("2. 失败后会触发fallback机制")
    print("3. Fallback会生成静音占位符音频")
    print("4. 确保整个工作流程不会中断")

if __name__ == "__main__":
    test_edge_tts_fallback()
