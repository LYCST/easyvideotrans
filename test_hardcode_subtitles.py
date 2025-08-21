#!/usr/bin/env python3
"""
测试硬编码字幕功能
"""

import os
import sys
import json
import requests

def test_hardcode_subtitles():
    """测试硬编码字幕功能"""
    
    # 测试配置
    base_url = "http://localhost:10310"
    video_id = "Am54LhN2NLk"  # 使用一个测试视频ID
    
    print("🧪 测试硬编码字幕功能")
    print("=" * 50)
    
    # 测试1: 不启用硬编码字幕（默认行为）
    print("\n1️⃣ 测试不启用硬编码字幕（默认）")
    data = {
        "video_id": video_id,
        "hardcode_subtitles": False
    }
    
    try:
        response = requests.post(f"{base_url}/video_preview", 
                               json=data, 
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 202:
            print("✅ 异步任务提交成功")
            task_id = response.json().get('video_preview_task_id')
            print(f"   任务ID: {task_id}")
        elif response.status_code == 200:
            print("✅ 同步任务执行成功")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"   响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 测试2: 启用硬编码字幕
    print("\n2️⃣ 测试启用硬编码字幕")
    data = {
        "video_id": video_id,
        "hardcode_subtitles": True
    }
    
    try:
        response = requests.post(f"{base_url}/video_preview", 
                               json=data, 
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 202:
            print("✅ 异步任务提交成功")
            task_id = response.json().get('video_preview_task_id')
            print(f"   任务ID: {task_id}")
        elif response.status_code == 200:
            print("✅ 同步任务执行成功")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"   响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 测试3: 不传参数（应该默认为False）
    print("\n3️⃣ 测试不传参数（默认False）")
    data = {
        "video_id": video_id
    }
    
    try:
        response = requests.post(f"{base_url}/video_preview", 
                               json=data, 
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 202:
            print("✅ 异步任务提交成功")
            task_id = response.json().get('video_preview_task_id')
            print(f"   任务ID: {task_id}")
        elif response.status_code == 200:
            print("✅ 同步任务执行成功")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"   响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 测试完成！")
    print("\n📝 说明:")
    print("- hardcode_subtitles=False: 使用MoviePy合成视频，不包含硬编码字幕")
    print("- hardcode_subtitles=True: 使用FFmpeg合成视频，包含硬编码字幕")
    print("- 不传参数: 默认为False")

if __name__ == "__main__":
    test_hardcode_subtitles()
