#!/usr/bin/env python3
"""
测试音频时长问题
"""

import os
import srt
import subprocess
from pydub import AudioSegment

def get_audio_duration(audio_path):
    """获取音频时长（秒）"""
    try:
        audio = AudioSegment.from_wav(audio_path)
        return len(audio) / 1000.0
    except Exception as e:
        print(f"获取音频时长失败: {e}")
        return None

def get_video_duration(video_path):
    """获取视频时长（秒）"""
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', video_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"获取视频时长失败: {e}")
        return None

def analyze_srt_timing(srt_path):
    """分析SRT文件的时间信息"""
    try:
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        subs = list(srt.parse(content))
        
        print(f"📝 SRT文件分析: {srt_path}")
        print(f"   字幕数量: {len(subs)}")
        print(f"   开始时间: {subs[0].start}")
        print(f"   结束时间: {subs[-1].end}")
        print(f"   总时长: {(subs[-1].end - subs[0].start).total_seconds():.2f}秒")
        
        return subs
    except Exception as e:
        print(f"分析SRT文件失败: {e}")
        return None

def analyze_voice_source_dir(video_id):
    """分析语音源目录"""
    voice_dir = f"output/{video_id}_zh_source"
    
    if not os.path.exists(voice_dir):
        print(f"❌ 语音源目录不存在: {voice_dir}")
        return
    
    print(f"\n🔊 语音源目录分析: {voice_dir}")
    
    # 检查voiceMap.srt
    voice_map_path = os.path.join(voice_dir, "voiceMap.srt")
    if os.path.exists(voice_map_path):
        subs = analyze_srt_timing(voice_map_path)
        
        # 分析每个音频文件
        total_audio_duration = 0
        for i, sub in enumerate(subs):
            audio_file = os.path.join(voice_dir, sub.content)
            if os.path.exists(audio_file):
                duration = get_audio_duration(audio_file)
                if duration:
                    total_audio_duration += duration
                    print(f"   音频 {i+1}: {sub.content} - 时长: {duration:.2f}s, 字幕时间: {(sub.end - sub.start).total_seconds():.2f}s")
        
        print(f"   音频总时长: {total_audio_duration:.2f}秒")
        print(f"   字幕总时长: {(subs[-1].end - subs[0].start).total_seconds():.2f}秒")
        print(f"   差异: {total_audio_duration - (subs[-1].end - subs[0].start).total_seconds():.2f}秒")

def main():
    """主函数"""
    video_id = "Am54LhN2NLk"
    
    print("🧪 音频时长问题分析")
    print("=" * 50)
    
    # 检查原始音频
    original_audio = f"output/{video_id}.wav"
    if os.path.exists(original_audio):
        duration = get_audio_duration(original_audio)
        print(f"📹 原始音频: {original_audio} - 时长: {duration:.2f}秒")
    
    # 检查中文音频
    chinese_audio = f"output/{video_id}_zh.wav"
    if os.path.exists(chinese_audio):
        duration = get_audio_duration(chinese_audio)
        print(f"🔊 中文音频: {chinese_audio} - 时长: {duration:.2f}秒")
    
    # 检查视频
    video_file = f"output/{video_id}.mp4"
    if os.path.exists(video_file):
        duration = get_video_duration(video_file)
        print(f"🎬 视频文件: {video_file} - 时长: {duration:.2f}秒")
    
    # 分析字幕文件
    srt_file = f"output/{video_id}_zh_merged.srt"
    if os.path.exists(srt_file):
        analyze_srt_timing(srt_file)
    
    # 分析语音源目录
    analyze_voice_source_dir(video_id)
    
    print("\n📝 问题分析:")
    print("- 如果中文音频时长比原始音频长，说明TTS生成的音频片段比原文字幕时间长")
    print("- 这会导致voice_connect时音频被拉伸，最终视频时长变长")
    print("- 解决方案：调整TTS参数或修改voice_connect逻辑")

if __name__ == "__main__":
    main()
