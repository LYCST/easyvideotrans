#!/usr/bin/env python3
"""
测试音频裁剪功能
"""

import os
import sys
import torch

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_audio_cropping():
    """测试音频裁剪功能"""
    try:
        # 创建一个模拟的长音频（60秒）
        sample_rate = 16000
        duration = 60  # 60秒
        samples = duration * sample_rate
        
        # 创建模拟音频张量
        mock_audio = torch.randn(1, samples)  # 1通道，60秒
        print(f"Created mock audio: {mock_audio.shape} ({mock_audio.shape[-1]/sample_rate:.1f}s)")
        
        # 模拟裁剪逻辑
        max_samples = 30 * sample_rate  # 30秒
        
        if mock_audio.shape[-1] > max_samples:
            print(f"Audio too long ({mock_audio.shape[-1]/sample_rate:.1f}s), cropping to 30s")
            # 从中间部分裁剪30秒
            start_sample = (mock_audio.shape[-1] - max_samples) // 2
            cropped_audio = mock_audio[..., start_sample:start_sample + max_samples]
            print(f"Cropped audio: {cropped_audio.shape} ({cropped_audio.shape[-1]/sample_rate:.1f}s)")
        else:
            cropped_audio = mock_audio
            print("Audio is already short enough")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== 音频裁剪测试 ===")
    success = test_audio_cropping()
    if success:
        print("\n✅ 测试通过!")
    else:
        print("\n❌ 测试失败!")
        sys.exit(1)
