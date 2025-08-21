#!/usr/bin/env python3
"""
测试 CosyVoice2 TTS 客户端
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cosyvoice2_client():
    """测试 CosyVoice2 TTS 客户端初始化"""
    try:
        from src.service.tts.cosyvoice2_tts import CosyVoice2Client
        
        print("正在初始化 CosyVoice2 TTS 客户端...")
        
        # 测试客户端初始化（不加载模型，只测试导入）
        client = CosyVoice2Client(
            model_path="pretrained_models/CosyVoice2-0.5B",
            reference_audio_path=None,
            speaker_name="测试说话人",
            mode="zero_shot",
            instruction="用四川话说这句话"
        )
        
        print("✅ CosyVoice2 TTS 客户端初始化成功!")
        
        # 测试参数
        print(f"模型路径: {client.model_path}")
        print(f"参考音频路径: {client.reference_audio_path}")
        print(f"说话人名称: {client.speaker_name}")
        print(f"生成模式: {client.mode}")
        print(f"指令: {client.instruction}")
        
        return True
        
    except Exception as e:
        print(f"❌ CosyVoice2 TTS 客户端初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== CosyVoice2 TTS 客户端测试 ===")
    success = test_cosyvoice2_client()
    if success:
        print("\n✅ 测试通过!")
    else:
        print("\n❌ 测试失败!")
        sys.exit(1)
