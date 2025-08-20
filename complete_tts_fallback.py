#!/usr/bin/env python3
"""
为缺失的TTS文件生成fallback音频
"""

import os
import srt
from src.service.tts import get_tts_client

def complete_tts_fallback():
    """为缺失的TTS文件生成fallback音频"""
    print("=== 为缺失的TTS文件生成Fallback音频 ===\n")
    
    srt_file = "output/Am54LhN2NLk_zh_merged.srt"
    tts_dir = "output/Am54LhN2NLk_zh_source"
    
    print(f"📁 SRT文件: {srt_file}")
    print(f"📁 TTS目录: {tts_dir}")
    print()
    
    # 确保TTS目录存在
    os.makedirs(tts_dir, exist_ok=True)
    print(f"✅ 确保TTS目录存在: {tts_dir}")
    
    # 读取SRT文件
    try:
        with open(srt_file, 'r', encoding='utf-8') as f:
            srt_content = f.read()
        
        sub_generator = srt.parse(srt_content)
        sub_title_list = list(sub_generator)
        total_subtitles = len(sub_title_list)
        
        print(f"📊 SRT文件包含 {total_subtitles} 个字幕")
        
        # 检查现有的音频文件
        existing_files = set()
        if os.path.exists(tts_dir):
            for file in os.listdir(tts_dir):
                if file.endswith('.wav') and file[:-4].isdigit():
                    existing_files.add(int(file[:-4]))
        
        print(f"📊 现有音频文件: {len(existing_files)} 个")
        
        # 找出缺失的文件
        missing_files = []
        for i in range(1, total_subtitles + 1):
            if i not in existing_files:
                missing_files.append(i)
        
        if not missing_files:
            print("✅ 所有音频文件都已存在，无需生成fallback")
            return
        
        print(f"❌ 缺失 {len(missing_files)} 个音频文件: {missing_files}")
        
        # 为缺失的文件生成fallback音频
        print(f"\n🔄 为缺失文件生成fallback音频...")
        
        fallback_client = get_tts_client('fallback', character="zh-CN-XiaoyiNeural")
        
        for missing_index in missing_files:
            if missing_index <= len(sub_title_list):
                subtitle = sub_title_list[missing_index - 1]
                text = subtitle.content
                
                # 生成单个音频文件
                output_path = os.path.join(tts_dir, f"{missing_index}.wav")
                
                try:
                    # 使用fallback TTS生成单个音频
                    success = fallback_client._generate_single_audio(text, output_path)
                    if success:
                        print(f"   ✅ 生成 {missing_index}.wav: {text[:50]}...")
                    else:
                        print(f"   ❌ 生成 {missing_index}.wav 失败")
                except Exception as e:
                    print(f"   ❌ 生成 {missing_index}.wav 异常: {e}")
        
        print(f"\n✅ Fallback音频生成完成")
        
        # 最终检查
        final_existing = set()
        if os.path.exists(tts_dir):
            for file in os.listdir(tts_dir):
                if file.endswith('.wav') and file[:-4].isdigit():
                    final_existing.add(int(file[:-4]))
        
        final_missing = [i for i in range(1, total_subtitles + 1) if i not in final_existing]
        
        if not final_missing:
            print("🎉 所有音频文件现在都已完整！")
        else:
            print(f"⚠️ 仍有 {len(final_missing)} 个文件缺失: {final_missing}")
            
    except Exception as e:
        print(f"❌ 处理失败: {e}")
    
    print("\n=== 处理完成 ===")

if __name__ == "__main__":
    complete_tts_fallback()
