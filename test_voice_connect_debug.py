#!/usr/bin/env python3
"""
测试音频连接函数的调试版本
"""

import os
import sys
from src.service.video_synthesis.voice_connect import connect_voice

def test_voice_connect():
    """测试音频连接函数"""
    
    video_id = "Am54LhN2NLk"
    
    print("🧪 测试音频连接函数")
    print("=" * 50)
    
    # 设置路径
    source_dir = f"output/{video_id}_zh_source"
    output_path = f"output/{video_id}_zh_debug.wav"
    warning_path = f"output/{video_id}_connect_debug.log"
    
    print(f"📁 源目录: {source_dir}")
    print(f"📁 输出文件: {output_path}")
    print(f"📁 警告日志: {warning_path}")
    
    # 检查源目录是否存在
    if not os.path.exists(source_dir):
        print(f"❌ 源目录不存在: {source_dir}")
        return False
    
    # 检查voiceMap.srt是否存在
    voice_map_path = os.path.join(source_dir, "voiceMap.srt")
    if not os.path.exists(voice_map_path):
        print(f"❌ voiceMap.srt不存在: {voice_map_path}")
        return False
    
    print(f"✅ 源目录和voiceMap.srt都存在")
    
    # 调用音频连接函数
    print(f"\n🚀 开始调用connect_voice函数...")
    result = connect_voice(None, source_dir, output_path, warning_path)
    
    if result:
        print(f"\n✅ 音频连接成功!")
        
        # 检查输出文件
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   输出文件大小: {file_size/1024/1024:.2f}MB")
        else:
            print(f"❌ 输出文件不存在: {output_path}")
    else:
        print(f"\n❌ 音频连接失败!")
    
    return result

if __name__ == "__main__":
    test_voice_connect()
