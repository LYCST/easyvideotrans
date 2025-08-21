#!/usr/bin/env python3
"""
测试 OpenAI TTS 客户端
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_openai_tts_client():
    """测试 OpenAI TTS 客户端初始化"""
    try:
        from src.service.tts.openai_tts import OpenAITTSClient
        
        # 检查环境变量
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("警告: OPENAI_API_KEY 环境变量未设置，使用测试 key")
            api_key = "test-key"
        
        print(f"使用 API Key: {api_key[:10]}...")
        
        # 测试客户端初始化
        print("正在初始化 OpenAI TTS 客户端...")
        client = OpenAITTSClient(voice="alloy", model="tts-1")
        print("✅ OpenAI TTS 客户端初始化成功!")
        
        # 测试参数
        print(f"语音类型: {client.voice}")
        print(f"模型: {client.model}")
        print(f"指令: {client.instructions}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI TTS 客户端初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== OpenAI TTS 客户端测试 ===")
    success = test_openai_tts_client()
    if success:
        print("\n✅ 测试通过!")
    else:
        print("\n❌ 测试失败!")
        sys.exit(1)
