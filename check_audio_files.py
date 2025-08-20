#!/usr/bin/env python3
"""
检查音频文件是否有声音
"""

import os
import wave
import numpy as np

def check_audio_files():
    """检查音频文件是否有声音"""
    print("=== 检查音频文件是否有声音 ===\n")
    
    tts_dir = "output/Am54LhN2NLk_zh_source"
    
    if not os.path.exists(tts_dir):
        print("❌ TTS目录不存在")
        return
    
    # 获取所有wav文件
    wav_files = []
    for file in os.listdir(tts_dir):
        if file.endswith('.wav') and file[:-4].isdigit():
            wav_files.append(int(file[:-4]))
    
    wav_files.sort()
    
    print(f"📊 找到 {len(wav_files)} 个音频文件")
    print()
    
    silent_files = []
    audio_files = []
    
    for file_num in wav_files:
        file_path = os.path.join(tts_dir, f"{file_num}.wav")
        
        try:
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            
            if file_size == 0:
                print(f"❌ {file_num:2d}.wav: 空文件 (0 bytes)")
                silent_files.append(file_num)
                continue
            
            # 读取音频文件
            with wave.open(file_path, 'rb') as wav_file:
                # 获取音频参数
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration = frames / sample_rate
                
                # 读取音频数据
                audio_data = wav_file.readframes(frames)
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                
                # 计算音量（RMS）
                if len(audio_array) > 0:
                    rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
                    max_amplitude = np.max(np.abs(audio_array))
                else:
                    rms = 0
                    max_amplitude = 0
                
                # 判断是否有声音（阈值可以根据需要调整）
                if rms < 100 and max_amplitude < 1000:  # 静音阈值
                    print(f"🔇 {file_num:2d}.wav: 静音 (RMS: {rms:.1f}, Max: {max_amplitude}, 时长: {duration:.1f}s)")
                    silent_files.append(file_num)
                else:
                    print(f"🔊 {file_num:2d}.wav: 有声音 (RMS: {rms:.1f}, Max: {max_amplitude}, 时长: {duration:.1f}s)")
                    audio_files.append(file_num)
                    
        except Exception as e:
            print(f"❌ {file_num:2d}.wav: 读取失败 - {e}")
            silent_files.append(file_num)
    
    print(f"\n📊 统计结果:")
    print(f"   🔊 有声音的文件: {len(audio_files)} 个")
    print(f"   🔇 静音文件: {len(silent_files)} 个")
    
    if silent_files:
        print(f"   📝 静音文件列表: {silent_files}")
    
    if audio_files:
        print(f"   📝 有声音文件列表: {audio_files}")
    
    print(f"\n=== 检查完成 ===")

if __name__ == "__main__":
    check_audio_files()
