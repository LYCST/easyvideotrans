#!/usr/bin/env python3
"""
测试英文单词保护功能
"""

from src.service.video_synthesis.video_preview import _wrap_text

def test_english_protection():
    """测试英文单词保护"""
    
    print("🧪 测试英文单词保护功能")
    print("=" * 50)
    
    # 测试用例
    test_cases = [
        {
            "text": "Josh Sorensen，Church Media Squad 的系统副总裁，也是我最喜爱的无代码运营者之一，表达得最为精准。",
            "max_chars": 30,
            "description": "中英文混合，30字符换行"
        },
        {
            "text": "Josh Sorensen，Church Media Squad 的系统副总裁，也是我最喜爱的无代码运营者之一，表达得最为精准。",
            "max_chars": 40,
            "description": "中英文混合，40字符换行"
        },
        {
            "text": "This is a very long English sentence that should be wrapped at word boundaries.",
            "max_chars": 25,
            "description": "纯英文句子，25字符换行"
        },
        {
            "text": "无论您有特定的数据隐私需求、想要对性能拥有更多控制，还是仅仅希望成本更可预测，n8n 对想自行托管的公司来说都是不二之选。",
            "max_chars": 20,
            "description": "中文句子，包含英文单词n8n"
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
        
        # 检查英文单词是否被截断
        print("🔍 检查英文单词完整性:")
        for j, line in enumerate(lines, 1):
            words = line.split()
            for word in words:
                if word.isalpha() and len(word) < 3:  # 可能被截断的短单词
                    print(f"   第{j}行可能被截断的单词: {word}")

def test_specific_case():
    """测试特定案例"""
    
    print("\n" + "=" * 50)
    print("🔧 测试特定案例")
    
    text = "Josh Sorensen，Church Media Squad 的系统副总裁，也是我最喜爱的无代码运营者之一，表达得最为精准。"
    max_chars = 30
    
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

if __name__ == "__main__":
    test_english_protection()
    test_specific_case()
    
    print("\n" + "=" * 50)
    print("🎯 测试完成！")
    print("\n📝 新功能特点:")
    print("- 保持简单可靠的换行逻辑")
    print("- 英文单词不在中间截断")
    print("- 在单词边界处换行")
    print("- 保持字符完整性")
