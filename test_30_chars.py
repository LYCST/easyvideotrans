#!/usr/bin/env python3
"""
测试30字符换行
"""

from src.service.video_synthesis.video_preview import _wrap_text

def test_30_chars():
    """测试30字符换行"""
    
    print("🧪 测试30字符换行")
    print("=" * 50)
    
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
    
    if original_chars != result_chars:
        print(f"不匹配的字符:")
        for i, (orig, res) in enumerate(zip(original_chars, result_chars)):
            if orig != res:
                print(f"  位置{i}: 原文'{orig}' vs 结果'{res}'")

if __name__ == "__main__":
    test_30_chars()
