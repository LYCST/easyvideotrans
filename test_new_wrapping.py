#!/usr/bin/env python3
"""
测试新的字幕换行逻辑
"""

from src.service.video_synthesis.video_preview import _wrap_text

def test_wrapping_logic():
    """测试换行逻辑"""
    
    print("🧪 测试新的字幕换行逻辑")
    print("=" * 50)
    
    # 测试用例
    test_cases = [
        {
            "text": "无论您有特定的数据隐私需求、想要对性能拥有更多控制，还是仅仅希望成本更可预测，n8n 对想自行托管的公司来说都是不二之选。",
            "max_chars": 20,
            "description": "长句子，20字符换行，优先在标点处换行"
        },
        {
            "text": "这是一个很短的句子。",
            "max_chars": 30,
            "description": "短句子，无需换行"
        },
        {
            "text": "N8n has been a darling of the automation community for the past couple of years.",
            "max_chars": 25,
            "description": "英文句子，25字符换行"
        },
        {
            "text": "没有标点符号的长句子需要被强制换行处理以确保在视频中能够正确显示",
            "max_chars": 15,
            "description": "无标点符号，强制换行"
        },
        {
            "text": "这是一个测试句子，它包含多个逗号，用来测试标点符号换行功能。",
            "max_chars": 18,
            "description": "测试标点符号优先换行"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试: {test_case['description']}")
        print(f"   原文: {test_case['text']}")
        print(f"   字符数: {len(test_case['text'])}")
        print(f"   限制: {test_case['max_chars']}字符/行")
        
        result = _wrap_text(test_case['text'], test_case['max_chars'])
        
        print(f"   结果:")
        lines = result.split('\n')
        for j, line in enumerate(lines, 1):
            print(f"     第{j}行 ({len(line)}字符): {line}")
        
        print(f"   总行数: {len(lines)}")

def test_real_subtitle():
    """测试真实字幕"""
    
    print("\n" + "=" * 50)
    print("🧪 测试真实字幕")
    
    real_text = "无论您有特定的数据隐私需求、想要对性能拥有更多控制，还是仅仅希望成本更可预测，n8n 对想自行托管的公司来说都是不二之选。"
    
    print(f"原文: {real_text}")
    print(f"字符数: {len(real_text)}")
    
    # 测试不同的字符限制
    for max_chars in [15, 20, 25, 30]:
        print(f"\n🔧 测试 {max_chars} 字符/行:")
        result = _wrap_text(real_text, max_chars)
        lines = result.split('\n')
        
        for j, line in enumerate(lines, 1):
            print(f"  第{j}行 ({len(line)}字符): {line}")

if __name__ == "__main__":
    test_wrapping_logic()
    test_real_subtitle()
    
    print("\n" + "=" * 50)
    print("🎯 测试完成！")
    print("\n📝 新逻辑特点:")
    print("- 超过字数时，优先在前后5个字内的标点处换行")
    print("- 超过字数且前后5个字内无标点时，直接在超过字数处换行")
    print("- 每次换行后字数计数都会重置")
    print("- 使用实际换行符而不是 \\N")
