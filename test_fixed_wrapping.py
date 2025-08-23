#!/usr/bin/env python3
"""
测试修复后的换行逻辑
"""

from src.service.video_synthesis.video_preview import _wrap_text

def test_fixed_wrapping():
    """测试修复后的换行逻辑"""
    
    print("🧪 测试修复后的换行逻辑")
    print("=" * 50)
    
    # 测试用例
    test_cases = [
        {
            "text": "无论您有特定的数据隐私需求、想要对性能拥有更多控制，还是仅仅希望成本更可预测，n8n 对想自行托管的公司来说都是不二之选。",
            "max_chars": 20,
            "description": "长句子，20字符换行"
        },
        {
            "text": "这是一个测试句子，它包含多个逗号，用来测试标点符号换行功能。",
            "max_chars": 15,
            "description": "标点符号测试"
        },
        {
            "text": "没有标点符号的长句子需要被强制换行处理以确保在视频中能够正确显示",
            "max_chars": 15,
            "description": "无标点符号，强制换行"
        },
        {
            "text": "短句子。",
            "max_chars": 30,
            "description": "短句子，无需换行"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试: {test_case['description']}")
        print(f"原文: {test_case['text']}")
        print(f"字符数: {len(test_case['text'])}")
        print(f"限制: {test_case['max_chars']}字符/行")
        
        result = _wrap_text(test_case['text'], test_case['max_chars'])
        
        print(f"结果:")
        lines = result.split('\n')
        for j, line in enumerate(lines, 1):
            print(f"  第{j}行 ({len(line)}字符): {repr(line)}")
        
        # 检查是否有重复行
        line_set = set(lines)
        if len(line_set) != len(lines):
            print(f"⚠️  警告: 发现重复行!")
            for line in lines:
                if lines.count(line) > 1:
                    print(f"   重复行: {repr(line)} 出现 {lines.count(line)} 次")
        else:
            print("✅ 无重复行")
        
        # 检查每行字符数
        for j, line in enumerate(lines, 1):
            if len(line) > test_case['max_chars']:
                print(f"⚠️  警告: 第{j}行超过字符限制 ({len(line)} > {test_case['max_chars']})")
        
        # 检查是否有字符丢失或重复
        original_chars = test_case['text']
        result_chars = ''.join(lines)
        if original_chars != result_chars:
            print(f"⚠️  警告: 字符不匹配!")
            print(f"   原文: {repr(original_chars)}")
            print(f"   结果: {repr(result_chars)}")
        else:
            print("✅ 字符完整匹配")

def test_specific_case():
    """测试特定案例"""
    
    print("\n" + "=" * 50)
    print("🔧 测试特定案例")
    
    text = "无论您有特定的数据隐私需求、想要对性能拥有更多控制，还是仅仅希望成本更可预测，n8n 对想自行托管的公司来说都是不二之选。"
    max_chars = 20
    
    print(f"原文: {text}")
    print(f"字符数: {len(text)}")
    print(f"限制: {max_chars}字符/行")
    
    result = _wrap_text(text, max_chars)
    lines = result.split('\n')
    
    print(f"\n换行结果:")
    for j, line in enumerate(lines, 1):
        print(f"第{j}行 ({len(line)}字符): {line}")
    
    # 验证字符完整性
    original_chars = text
    result_chars = ''.join(lines)
    
    print(f"\n字符验证:")
    print(f"原文字符数: {len(original_chars)}")
    print(f"结果字符数: {len(result_chars)}")
    print(f"字符匹配: {'✅' if original_chars == result_chars else '❌'}")
    
    if original_chars != result_chars:
        print(f"不匹配的字符:")
        for i, (orig, res) in enumerate(zip(original_chars, result_chars)):
            if orig != res:
                print(f"  位置{i}: 原文'{orig}' vs 结果'{res}'")

if __name__ == "__main__":
    test_fixed_wrapping()
    test_specific_case()
    
    print("\n" + "=" * 50)
    print("🎯 测试完成！")
    print("\n📝 修复内容:")
    print("- 使用 while 循环替代 for 循环，避免字符重复处理")
    print("- 正确处理标点符号换行后的字符跳过")
    print("- 确保每个字符只被处理一次")
    print("- 保持字符完整性")
