#!/usr/bin/env python3
"""
测试下载验证功能
"""

import os
import sys
import json
import requests

def test_download_validation():
    """测试下载验证功能"""
    
    base_url = "http://localhost:10310"
    video_id = "Am54LhN2NLk"  # 使用一个测试视频ID
    
    print("🧪 测试下载验证功能")
    print("=" * 50)
    
    # 测试下载视频
    print(f"\n📥 测试下载视频: {video_id}")
    data = {
        "video_id": video_id
    }
    
    try:
        response = requests.post(f"{base_url}/yt_download", 
                               json=data, 
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            print("✅ 下载成功或文件已存在且有效")
            print(f"   响应: {response.json()['message']}")
        elif response.status_code == 500:
            print("❌ 下载失败")
            print(f"   错误: {response.json()['message']}")
        else:
            print(f"⚠️ 其他状态码: {response.status_code}")
            print(f"   响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 测试完成！")
    print("\n📝 说明:")
    print("- 如果文件不存在，会下载新文件")
    print("- 如果文件存在但损坏，会删除并重新下载")
    print("- 如果文件存在且有效，会跳过下载")

if __name__ == "__main__":
    test_download_validation()
