#!/usr/bin/env python3
"""
测试字幕换行修复
"""

import os
import tempfile
from src.service.video_synthesis.video_preview import _wrap_text, _process_subtitle_wrapping

def test_wrap_text():
    """测试文本换行功能"""
    
    print("🧪 测试文本换行功能")
    print("=" * 50)
    
    # 测试用例
    test_cases = [
        {
            "text": "这是一个很短的句子。",
            "max_chars": 30,
            "description": "正常字符串，正常数字"
        },
        {
            "text": "这是一个很短的句子。",
            "max_chars": "30",
            "description": "正常字符串，字符串数字"
        },
        {
            "text": "这是一个非常长的句子，需要被分成多行来显示，以确保在视频中能够正确显示。",
            "max_chars": 20,
            "description": "长字符串，需要换行"
        },
        {
            "text": 12345,  # 非字符串
            "max_chars": "abc",  # 非数字
            "description": "非字符串，非数字参数"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试: {test_case['description']}")
        print(f"   文本: {test_case['text']}")
        print(f"   参数: {test_case['max_chars']}")
        
        try:
            result = _wrap_text(test_case['text'], test_case['max_chars'])
            print(f"   结果: {result}")
            print(f"   ✅ 成功")
        except Exception as e:
            print(f"   ❌ 失败: {e}")

def test_srt_wrapping():
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
        
        # 测试不同的参数类型
        test_params = [30, "25", "abc", None]
        
        for param in test_params:
            print(f"\n🔧 测试参数: {param} (类型: {type(param)})")
            
            # 处理字幕换行
            processed_path = _process_subtitle_wrapping(temp_srt_path, param)
            
            if processed_path != temp_srt_path:
                print(f"✅ 字幕换行处理完成: {processed_path}")
                
                # 读取处理后的文件
                with open(processed_path, 'r', encoding='utf-8') as f:
                    processed_content = f.read()
                
                print("📝 处理后的字幕内容:")
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
        
        # 测试不同的参数
        test_params = [25, "30", "abc"]
        
        for param in test_params:
            print(f"\n🔧 测试参数: {param}")
            
            try:
                # 处理字幕换行
                processed_path = _process_subtitle_wrapping(real_srt_path, param)
                
                if processed_path != real_srt_path:
                    print(f"✅ 字幕换行处理完成: {processed_path}")
                    
                    # 显示前几行处理后的内容
                    with open(processed_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[:10]  # 只显示前10行
                    
                    print("📝 处理后的字幕内容（前10行）:")
                    print(''.join(lines))
                    
                    # 清理临时文件
                    os.remove(processed_path)
                    print(f"🗑️ 已清理临时文件: {processed_path}")
                else:
                    print("❌ 字幕换行处理失败")
                    
            except Exception as e:
                print(f"❌ 处理失败: {e}")
    else:
        print(f"⚠️ 未找到真实SRT文件: {real_srt_path}")

if __name__ == "__main__":
    test_wrap_text()
    test_srt_wrapping()
    test_real_srt_file()
    
    print("\n" + "=" * 50)
    print("🎯 测试完成！")
    print("\n📝 修复内容:")
    print("- 添加了参数类型检查和转换")
    print("- 添加了异常处理")
    print("- 添加了详细的调试信息")
    print("- 确保字符串和数字类型的兼容性")
