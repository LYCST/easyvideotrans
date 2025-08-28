#!/usr/bin/env python3
"""
检查换行后的字幕文件，查找可能的字段重复问题
"""

import os
import srt

def check_wrapped_subtitles(srt_file_path):
    """
    检查换行后的字幕文件
    
    Args:
        srt_file_path: 字幕文件路径
    """
    if not os.path.exists(srt_file_path):
        print(f"❌ 文件不存在: {srt_file_path}")
        return
    
    print(f"🔍 检查字幕文件: {srt_file_path}")
    print("=" * 60)
    
    try:
        # 读取字幕文件
        with open(srt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析字幕
        subs = list(srt.parse(content))
        print(f"📝 总字幕条目数: {len(subs)}")
        
        # 检查每个字幕条目
        for i, sub in enumerate(subs, 1):
            print(f"\n🎬 字幕 {i}:")
            print(f"   开始时间: {sub.start}")
            print(f"   结束时间: {sub.end}")
            print(f"   内容: {repr(sub.content)}")
            print(f"   内容长度: {len(sub.content)} 字符")
            
            # 检查是否有换行符
            if '\n' in sub.content:
                lines = sub.content.split('\n')
                print(f"   换行数: {len(lines)}")
                for j, line in enumerate(lines, 1):
                    print(f"     第{j}行: {repr(line)} ({len(line)} 字符)")
            
            # 检查是否有重复内容
            if i > 1:
                prev_sub = subs[i-2]  # 前一个字幕
                if sub.content == prev_sub.content:
                    print(f"   ⚠️  警告: 与前一个字幕内容重复!")
                if sub.start == prev_sub.start and sub.end == prev_sub.end:
                    print(f"   ⚠️  警告: 与前一个字幕时间重复!")
        
        # 检查文件大小
        file_size = os.path.getsize(srt_file_path)
        print(f"\n📊 文件大小: {file_size} 字节")
        
        # 检查是否有明显的重复模式
        print(f"\n🔍 检查重复模式...")
        content_lines = content.split('\n')
        line_count = {}
        for line in content_lines:
            line = line.strip()
            if line:
                line_count[line] = line_count.get(line, 0) + 1
        
        repeated_lines = {line: count for line, count in line_count.items() if count > 1}
        if repeated_lines:
            print(f"⚠️  发现重复行:")
            for line, count in repeated_lines.items():
                print(f"   '{line}' 出现 {count} 次")
        else:
            print("✅ 未发现重复行")
            
    except Exception as e:
        print(f"❌ 检查过程中出错: {e}")

def main():
    """主函数"""
    print("🔍 字幕文件检查工具")
    print("=" * 60)
    
    # 加载配置文件获取输出路径
    try:
        import json
        with open("./configs/easyvideotrans.json", "r") as f:
            config = json.load(f)
        output_dir = config.get("OUTPUT_PATH", "/home/shuzuan/temp/output")
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        output_dir = "/home/shuzuan/temp/output"
        print(f"Warning: Could not load config file, using default output_dir: {output_dir}")
    
    print(f"📁 使用输出目录: {output_dir}")
    
    # 检查常见的换行字幕文件
    common_files = [
        os.path.join(output_dir, "Am54LhN2NLk_zh_merged_wrapped.srt"),
        os.path.join(output_dir, "Am54LhN2NLk_zh_merged.srt"),
        os.path.join(output_dir, "Am54LhN2NLk_en_merged.srt")
    ]
    
    for file_path in common_files:
        if os.path.exists(file_path):
            check_wrapped_subtitles(file_path)
            print("\n" + "=" * 60)
    
    # 查找所有换行字幕文件
    print("\n🔍 查找所有换行字幕文件...")
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            if file.endswith("_wrapped.srt"):
                file_path = os.path.join(output_dir, file)
                if file_path not in common_files:
                    check_wrapped_subtitles(file_path)
                    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
