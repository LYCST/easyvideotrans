#!/usr/bin/env python3
"""
测试修改后的音频处理流程
"""

import requests
import json
import os
import time

def test_audio_flow():
    """测试完整的音频处理流程"""
    
    print("🧪 测试音频处理流程")
    print("=" * 60)
    
    # 测试数据
    test_data = {
        "video_id": "Am54LhN2NLk"
    }
    
    print(f"📤 测试视频ID: {test_data['video_id']}")
    
    # 步骤1: 下载音频和高清视频
    print(f"\n📥 步骤1: 下载音频和高清视频")
    print("-" * 40)
    
    try:
        response = requests.post(
            "http://localhost:10310/yt_download",
            json=test_data,
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 下载成功: {result.get('message', '')}")
            print(f"   音频文件: {result.get('audio_file', '')}")
            print(f"   高清视频: {result.get('hd_video_file', '')}")
        else:
            print(f"   ❌ 下载失败: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ 下载异常: {e}")
        return
    
    # 步骤2: 移除背景音乐
    print(f"\n🎵 步骤2: 移除背景音乐")
    print("-" * 40)
    
    try:
        response = requests.post(
            "http://localhost:10310/remove_audio_bg",
            json=test_data,
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 背景音乐移除成功: {result.get('message', '')}")
        else:
            print(f"   ❌ 背景音乐移除失败: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ 背景音乐移除异常: {e}")
        return
    
    # 步骤3: 转录音频
    print(f"\n📝 步骤3: 转录音频")
    print("-" * 40)
    
    try:
        response = requests.post(
            "http://localhost:10310/transcribe",
            json=test_data,
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 转录成功: {result.get('message', '')}")
        else:
            print(f"   ❌ 转录失败: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ 转录异常: {e}")
        return
    
    # 检查生成的文件
    print(f"\n🔍 检查生成的文件")
    print("-" * 40)
    
    output_dir = "/home/shuzuan/temp/output"
    video_id = test_data["video_id"]
    
    expected_files = [
        f"{video_id}_audio.wav",      # 下载的音频
        f"{video_id}_hd.mp4",         # 高清视频
        f"{video_id}_bg.wav",         # 背景音乐
        f"{video_id}_no_bg.wav",      # 人声
        f"{video_id}_en.srt",         # 英文字幕
        f"{video_id}_en_merged.srt"   # 合并的英文字幕
    ]
    
    for file_name in expected_files:
        file_path = os.path.join(output_dir, file_name)
        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"   ✅ {file_name}: 文件存在 ({size/1024:.2f} KB)")
            else:
                print(f"   ✅ {file_name}: 目录存在")
        else:
            print(f"   ❌ {file_name}: 不存在")

def test_file_renaming():
    """测试文件重命名逻辑"""
    
    print(f"\n🔧 测试文件重命名逻辑")
    print("=" * 40)
    
    output_dir = "/home/shuzuan/temp/output"
    video_id = "Am54LhN2NLk"
    
    # 检查重命名前后的文件
    old_names = [
        f"{video_id}_audio_bg.wav",
        f"{video_id}_audio_no_bg.wav"
    ]
    
    new_names = [
        f"{video_id}_bg.wav",
        f"{video_id}_no_bg.wav"
    ]
    
    print(f"📁 检查重命名逻辑:")
    for old_name, new_name in zip(old_names, new_names):
        old_path = os.path.join(output_dir, old_name)
        new_path = os.path.join(output_dir, new_name)
        
        if os.path.exists(old_path):
            print(f"   ⚠️  {old_name}: 仍然存在（应该被重命名）")
        elif os.path.exists(new_path):
            size = os.path.getsize(new_path)
            print(f"   ✅ {new_name}: 重命名成功 ({size/1024:.2f} KB)")
        else:
            print(f"   ❌ {new_name}: 重命名后文件不存在")

def main():
    """主函数"""
    
    print("🚀 音频处理流程测试")
    print("=" * 60)
    
    # 测试完整流程
    test_audio_flow()
    
    # 测试文件重命名
    test_file_renaming()
    
    print(f"\n📊 测试总结:")
    print(f"  ✅ 测试了下载音频和高清视频")
    print(f"  ✅ 测试了背景音乐移除")
    print(f"  ✅ 测试了音频转录")
    print(f"  ✅ 检查了文件重命名逻辑")
    print(f"  💡 现在应该使用下载的音频文件进行后续处理")

if __name__ == "__main__":
    main()
