#!/usr/bin/env python3
"""
测试字幕换行功能
"""

import os
import tempfile
from src.service.video_synthesis.video_preview import _wrap_text, _process_subtitle_wrapping

def test_text_wrapping():
    """测试文本换行功能"""
    
    print("🧪 测试字幕换行功能")
    print("=" * 50)
    
    # 测试用例
    test_cases = [
        {
            "text": "这是一个很短的句子。",
            "expected": "这是一个很短的句子。"
        },
        {
            "text": "这是一个非常长的句子，需要被分成多行来显示，以确保在视频中能够正确显示。",
            "expected": "这是一个非常长的句子，\\N需要被分成多行来显示，\\N以确保在视频中能够正确显示。"
        },
        {
            "text": "N8n has been a darling of the automation community for the past couple of years.",
            "expected": "N8n has been a darling of the automation community,\\Nfor the past couple of years."
        },
        {
            "text": "没有标点符号的长句子需要被强制换行处理",
            "expected": "没有标点符号的长句子需要被强制换行处理"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试文本: {test_case['text']}")
        
        result = _wrap_text(test_case['text'], max_chars_per_line=20)
        print(f"   换行结果: {result}")
        
        # 检查是否包含换行符
        if '\\N' in result:
            print("   ✅ 成功换行")
        else:
            print("   ℹ️ 无需换行")

def test_srt_file_wrapping():
    """测试SRT文件换行功能"""
    
    print("\n" + "=" * 50)
    print("🧪 测试SRT文件换行功能")
    
    # 创建测试SRT文件
    test_srt_content = """1
00:00:00,000 --> 00:00:05,000
这是一个很短的句子。

2
00:00:05,000 --> 00:00:10,000
这是一个非常长的句子，需要被分成多行来显示，以确保在视频中能够正确显示。

3
00:00:10,000 --> 00:00:15,000
N8n has been a darling of the automation community for the past couple of years.

4
00:00:15,000 --> 00:00:20,000
没有标点符号的长句子需要被强制换行处理以确保在视频中能够正确显示
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8') as f:
        f.write(test_srt_content)
        temp_srt_path = f.name
    
    try:
        print(f"📁 创建测试SRT文件: {temp_srt_path}")
        
        # 处理字幕换行
        processed_path = _process_subtitle_wrapping(temp_srt_path, max_chars_per_line=20)
        
        if processed_path != temp_srt_path:
            print(f"✅ 字幕换行处理完成: {processed_path}")
            
            # 读取处理后的文件
            with open(processed_path, 'r', encoding='utf-8') as f:
                processed_content = f.read()
            
            print("\n📝 处理后的字幕内容:")
            print(processed_content)
            
            # 清理临时文件
            os.remove(processed_path)
        else:
            print("❌ 字幕换行处理失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        # 清理原始测试文件
        if os.path.exists(temp_srt_path):
            os.remove(temp_srt_path)

def test_real_srt_file():
    """测试真实SRT文件"""
    
    print("\n" + "=" * 50)
    print("🧪 测试真实SRT文件")
    
    # 检查是否存在真实的SRT文件
    real_srt_path = "output/Am54LhN2NLk_zh_merged.srt"
    
    if os.path.exists(real_srt_path):
        print(f"📁 发现真实SRT文件: {real_srt_path}")
        
        # 处理字幕换行
        processed_path = _process_subtitle_wrapping(real_srt_path, max_chars_per_line=25)
        
        if processed_path != real_srt_path:
            print(f"✅ 字幕换行处理完成: {processed_path}")
            
            # 显示前几行处理后的内容
            with open(processed_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:20]  # 只显示前20行
            
            print("\n📝 处理后的字幕内容（前20行）:")
            print(''.join(lines))
            
            # 清理临时文件
            os.remove(processed_path)
            print(f"🗑️ 已清理临时文件: {processed_path}")
        else:
            print("❌ 字幕换行处理失败")
    else:
        print(f"⚠️ 未找到真实SRT文件: {real_srt_path}")

if __name__ == "__main__":
    test_text_wrapping()
    test_srt_file_wrapping()
    test_real_srt_file()
    
    print("\n" + "=" * 50)
    print("🎯 测试完成！")
    print("\n📝 说明:")
    print("- 字幕换行功能会在标点符号处自动换行")
    print("- 如果超过最大字符数且没有标点符号，会强制换行")
    print("- 换行符使用 \\N 格式，符合ASS字幕标准")
    print("- 硬编码字幕时会自动应用换行效果")
