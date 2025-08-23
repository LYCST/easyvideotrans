#!/usr/bin/env python3
"""
调试换行逻辑，查找重复字段的问题
"""

from src.service.video_synthesis.video_preview import _wrap_text

def debug_wrap_text():
    """调试换行逻辑"""
    
    print("🔍 调试换行逻辑")
    print("=" * 50)
    
    # 测试用例
    test_cases = [
        {
            "text": "无论您有特定的数据隐私需求、想要对性能拥有更多控制，还是仅仅希望成本更可预测，n8n 对想自行托管的公司来说都是不二之选。",
            "max_chars": 20,
            "description": "长句子测试"
        },
        {
            "text": "这是一个测试句子，它包含多个逗号，用来测试标点符号换行功能。",
            "max_chars": 15,
            "description": "标点符号测试"
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

def step_by_step_debug():
    """逐步调试换行逻辑"""
    
    print("\n" + "=" * 50)
    print("🔧 逐步调试换行逻辑")
    
    text = "无论您有特定的数据隐私需求、想要对性能拥有更多控制，还是仅仅希望成本更可预测，n8n 对想自行托管的公司来说都是不二之选。"
    max_chars = 20
    
    print(f"原文: {text}")
    print(f"字符数: {len(text)}")
    print(f"限制: {max_chars}字符/行")
    
    # 手动模拟换行逻辑
    punctuation_marks = ['。', '！', '？', '；', '，', '.', '!', '?', ';', ',']
    lines = []
    current_line = ""
    char_count = 0
    
    print(f"\n逐步处理:")
    
    for i, char in enumerate(text):
        current_line += char
        char_count += 1
        
        print(f"字符 {i+1}: '{char}' (位置{i}), 当前行: '{current_line}' (长度{char_count})")
        
        # 检查是否需要换行
        if char_count >= max_chars:
            print(f"  ⚠️  超过字符限制 ({char_count} >= {max_chars})")
            
            # 情况1：超过字数，且前后5个字内有标点，在标点处换行
            found_punctuation = False
            
            # 向前查找5个字符内的标点
            for j in range(max(0, i-4), i+1):
                if j < len(text) and text[j] in punctuation_marks:
                    print(f"    找到标点 '{text[j]}' 在位置 {j}")
                    
                    if j < i:  # 标点在当前位置之前
                        print(f"    标点在当前位置之前，重新构建行")
                        # 重新构建当前行，在标点后换行
                        current_line = text[:j+1]
                        remaining_text = text[j+1:]
                        lines.append(current_line)
                        print(f"    添加行: '{current_line}'")
                        current_line = ""
                        char_count = 0
                        
                        print(f"    处理剩余文本: '{remaining_text}'")
                        # 处理剩余文本
                        for k, remaining_char in enumerate(remaining_text):
                            current_line += remaining_char
                            char_count += 1
                            print(f"      剩余字符 {k+1}: '{remaining_char}', 当前行: '{current_line}' (长度{char_count})")
                            if char_count >= max_chars:
                                # 如果剩余文本也超过限制，直接换行
                                lines.append(current_line)
                                print(f"      添加行: '{current_line}'")
                                current_line = ""
                                char_count = 0
                        break
                    else:  # 标点就是当前位置
                        lines.append(current_line)
                        print(f"    标点就是当前位置，添加行: '{current_line}'")
                        current_line = ""
                        char_count = 0
                        found_punctuation = True
                        break
            
            # 情况2：超过字数，前后5个字没有标点，直接在超过字数的地方换行
            if not found_punctuation:
                lines.append(current_line)
                print(f"    未找到标点，直接换行: '{current_line}'")
                current_line = ""
                char_count = 0
    
    # 添加最后一行
    if current_line:
        lines.append(current_line)
        print(f"添加最后一行: '{current_line}'")
    
    result = '\n'.join(lines)
    print(f"\n最终结果:")
    for j, line in enumerate(lines, 1):
        print(f"  第{j}行 ({len(line)}字符): {repr(line)}")
    
    # 检查重复
    line_set = set(lines)
    if len(line_set) != len(lines):
        print(f"⚠️  发现重复行!")
        for line in lines:
            if lines.count(line) > 1:
                print(f"   重复行: {repr(line)} 出现 {lines.count(line)} 次")

if __name__ == "__main__":
    debug_wrap_text()
    step_by_step_debug()
