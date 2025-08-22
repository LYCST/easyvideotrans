#!/usr/bin/env python3
"""
检查字幕文件的存在性和内容
"""

import os
import srt

def check_subtitle_files(video_id="Am54LhN2NLk"):
    """检查字幕文件"""
    
    print("🔍 检查字幕文件")
    print("=" * 50)
    
    # 检查各种可能的字幕文件
    subtitle_files = [
        f"output/{video_id}_zh_merged.srt",
        f"output/{video_id}_zh_merged_wrapped.srt",
        f"output/{video_id}_en_merged.srt",
        f"output/{video_id}_en.srt"
    ]
    
    for file_path in subtitle_files:
        print(f"\n📁 检查文件: {file_path}")
        
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"   ✅ 文件存在")
            print(f"   文件大小: {file_size} 字节")
            
            # 尝试解析SRT文件
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                subs = list(srt.parse(content))
                print(f"   字幕条目数: {len(subs)}")
                
                if len(subs) > 0:
                    print(f"   第一个字幕: {subs[0].content[:50]}...")
                    print(f"   最后一个字幕: {subs[-1].content[:50]}...")
                    print(f"   总时长: {subs[-1].end.total_seconds():.2f}秒")
                
            except Exception as e:
                print(f"   ❌ 解析失败: {e}")
        else:
            print(f"   ❌ 文件不存在")

def test_subtitle_wrapping(video_id="Am54LhN2NLk"):
    """测试字幕换行处理"""
    
    print("\n" + "=" * 50)
    print("🧪 测试字幕换行处理")
    
    from src.service.video_synthesis.video_preview import _process_subtitle_wrapping
    
    original_srt = f"output/{video_id}_zh_merged.srt"
    
    if not os.path.exists(original_srt):
        print(f"❌ 原始字幕文件不存在: {original_srt}")
        return
    
    print(f"📁 原始字幕文件: {original_srt}")
    
    # 测试字幕换行处理
    try:
        processed_srt = _process_subtitle_wrapping(original_srt, 25)
        print(f"✅ 处理完成: {processed_srt}")
        
        if os.path.exists(processed_srt):
            print(f"   文件大小: {os.path.getsize(processed_srt)} 字节")
            
            # 显示前几行内容
            with open(processed_srt, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]
            
            print("   前10行内容:")
            for line in lines:
                print(f"   {line.rstrip()}")
        else:
            print(f"❌ 处理后的文件不存在")
            
    except Exception as e:
        print(f"❌ 处理失败: {e}")

def check_ffmpeg_subtitle_path():
    """检查FFmpeg字幕路径处理"""
    
    print("\n" + "=" * 50)
    print("🔧 检查FFmpeg字幕路径处理")
    
    test_paths = [
        "./output/Am54LhN2NLk_zh_merged_wrapped.srt",
        "C:\\Users\\test\\output\\Am54LhN2NLk_zh_merged_wrapped.srt",
        "/home/user/output/Am54LhN2NLk_zh_merged_wrapped.srt"
    ]
    
    for path in test_paths:
        print(f"\n原始路径: {path}")
        
        # 应用FFmpeg路径处理
        ffmpeg_path = path.replace('\\', '/').replace(':', '\\:')
        print(f"FFmpeg路径: {ffmpeg_path}")
        
        # 检查是否需要转义
        if ':' in path and not path.startswith('/'):
            escaped_path = path.replace(':', '\\:')
            print(f"转义路径: {escaped_path}")

if __name__ == "__main__":
    check_subtitle_files()
    test_subtitle_wrapping()
    check_ffmpeg_subtitle_path()
    
    print("\n" + "=" * 50)
    print("🎯 检查完成！")
