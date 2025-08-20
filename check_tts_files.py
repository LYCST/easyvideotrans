#!/usr/bin/env python3
"""
检查TTS文件是否完整
"""

import os
import srt

def check_tts_files():
    """检查TTS文件是否完整"""
    print("=== 检查TTS文件完整性 ===\n")
    
    # 检查SRT文件
    srt_file = "output/Am54LhN2NLk_zh_merged.srt"
    tts_dir = "output/Am54LhN2NLk_zh_source"
    
    print(f"📁 SRT文件: {srt_file}")
    print(f"📁 TTS目录: {tts_dir}")
    print()
    
    # 读取SRT文件，获取字幕数量
    try:
        with open(srt_file, 'r', encoding='utf-8') as f:
            srt_content = f.read()
        
        sub_generator = srt.parse(srt_content)
        sub_title_list = list(sub_generator)
        total_subtitles = len(sub_title_list)
        
        print(f"📊 SRT文件包含 {total_subtitles} 个字幕")
        
        # 检查TTS目录中的音频文件
        if os.path.exists(tts_dir):
            audio_files = []
            for file in os.listdir(tts_dir):
                if file.endswith('.wav') and file[:-4].isdigit():
                    audio_files.append(int(file[:-4]))
            
            audio_files.sort()
            print(f"📊 TTS目录包含 {len(audio_files)} 个音频文件")
            
            # 检查缺失的文件
            missing_files = []
            for i in range(1, total_subtitles + 1):
                if i not in audio_files:
                    missing_files.append(i)
            
            if missing_files:
                print(f"❌ 缺失的音频文件: {missing_files}")
                print(f"📝 缺失文件对应的字幕:")
                for i in missing_files:
                    if i <= len(sub_title_list):
                        subtitle = sub_title_list[i-1]
                        print(f"   {i}: {subtitle.content}")
            else:
                print("✅ 所有音频文件都已生成")
            
            # 显示音频文件列表
            print(f"\n📂 音频文件列表:")
            for i in range(1, total_subtitles + 1):
                status = "✅" if i in audio_files else "❌"
                print(f"   {status} {i}.wav")
                
        else:
            print("❌ TTS目录不存在")
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    
    print("\n=== 检查完成 ===")

if __name__ == "__main__":
    check_tts_files()
