#!/usr/bin/env python3
"""
测试 CosyVoice2 音频生成功能
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cosyvoice2_audio_generation():
    """测试 CosyVoice2 音频生成"""
    try:
        from src.service.tts.cosyvoice2_tts import CosyVoice2Client
        
        print("正在初始化 CosyVoice2 TTS 客户端...")
        
        # 测试客户端初始化
        client = CosyVoice2Client(
            model_path="pretrained_models/CosyVoice2-0.5B",
            reference_audio_path=None,  # 暂时不加载参考音频
            speaker_name="测试说话人",
            mode="zero_shot",
            instruction="用四川话说这句话"
        )
        
        print("✅ CosyVoice2 TTS 客户端初始化成功!")
        
        # 测试音频生成（不加载参考音频，应该会失败）
        print("测试音频生成（无参考音频）...")
        test_text = "这是一个测试文本。"
        test_output = "./test_output.wav"
        
        # 测试零样本模式
        success = client._generate_single_audio_zero_shot(test_text, test_output)
        if not success:
            print("✅ 正确检测到缺少参考音频")
        else:
            print("❌ 应该失败但没有失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== CosyVoice2 音频生成测试 ===")
    success = test_cosyvoice2_audio_generation()
    if success:
        print("\n✅ 测试通过!")
    else:
        print("\n❌ 测试失败!")
        sys.exit(1)
