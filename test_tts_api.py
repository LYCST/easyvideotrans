#!/usr/bin/env python3
"""
TTS API 测试脚本
用于测试 Edge TTS 和 XTTS v2 的 API 接口
"""

import requests
import json
import os

# API 基础 URL
BASE_URL = "http://localhost:5000"

def test_edge_tts():
    """测试 Edge TTS API"""
    print("🧪 测试 Edge TTS API...")
    
    # Edge TTS 请求参数
    edge_tts_data = {
        "video_id": "Am54LhN2NLk",
        "tts_vendor": "edge",
        "tts_character": "zh-CN-XiaoyiNeural"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/tts",
            json=edge_tts_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Edge TTS API 测试成功")
        else:
            print("❌ Edge TTS API 测试失败")
            
    except Exception as e:
        print(f"❌ Edge TTS API 测试异常: {e}")

def test_xtts_v2():
    """测试 XTTS v2 API"""
    print("\n🧪 测试 XTTS v2 API...")
    
    # 首先上传参考音频
    print("📤 上传参考音频...")
    reference_audio_path = "test_reference_audio.wav"
    
    # 创建一个测试音频文件（如果不存在）
    if not os.path.exists(reference_audio_path):
        print(f"⚠️  测试音频文件不存在: {reference_audio_path}")
        print("请先上传一个参考音频文件")
        return
    
    try:
        with open(reference_audio_path, 'rb') as f:
            files = {'file': f}
            upload_response = requests.post(f"{BASE_URL}/upload_reference_audio", files=files)
        
        if upload_response.status_code == 200:
            upload_result = upload_response.json()
            reference_audio_path = upload_result['file_path']
            print(f"✅ 参考音频上传成功: {upload_result['filename']}")
        else:
            print(f"❌ 参考音频上传失败: {upload_response.json()}")
            return
            
    except Exception as e:
        print(f"❌ 参考音频上传异常: {e}")
        return
    
    # XTTS v2 请求参数
    xtts_v2_data = {
        "video_id": "Am54LhN2NLk",
        "tts_vendor": "xtts_v2",
        "reference_audio_path": reference_audio_path,
        "language": "zh",
        "model_name": "tts_models/multilingual/multi-dataset/xtts_v2"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/tts",
            json=xtts_v2_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 200:
            print("✅ XTTS v2 API 测试成功")
        else:
            print("❌ XTTS v2 API 测试失败")
            
    except Exception as e:
        print(f"❌ XTTS v2 API 测试异常: {e}")

def test_api_parameters():
    """测试 API 参数验证"""
    print("\n🧪 测试 API 参数验证...")
    
    # 测试缺少 tts_vendor 参数（应该自动推断为 edge）
    print("📝 测试缺少 tts_vendor 参数（自动推断为 edge）...")
    edge_data = {
        "video_id": "Am54LhN2NLk",
        "tts_character": "zh-CN-XiaoyiNeural"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/tts",
            json=edge_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 自动推断为 Edge TTS")
        else:
            print("❌ 参数验证失败")
            
    except Exception as e:
        print(f"❌ 参数验证异常: {e}")
    
    # 测试提供 reference_audio_path 但不指定 tts_vendor（应该自动推断为 xtts_v2）
    print("\n📝 测试提供 reference_audio_path 但不指定 tts_vendor（自动推断为 xtts_v2）...")
    xtts_data = {
        "video_id": "Am54LhN2NLk",
        "reference_audio_path": "/path/to/reference_audio.wav",
        "language": "zh"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/tts",
            json=xtts_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 400:
            print("✅ 自动推断为 XTTS v2（但缺少参考音频文件）")
        else:
            print("❌ 自动推断失败")
            
    except Exception as e:
        print(f"❌ 参数验证异常: {e}")

def main():
    """主函数"""
    print("🚀 开始 TTS API 测试...")
    print(f"API 地址: {BASE_URL}")
    print("=" * 50)
    
    # 测试参数验证
    test_api_parameters()
    
    # 测试 Edge TTS
    test_edge_tts()
    
    # 测试 XTTS v2
    test_xtts_v2()
    
    print("\n" + "=" * 50)
    print("🏁 TTS API 测试完成")

if __name__ == "__main__":
    main()
