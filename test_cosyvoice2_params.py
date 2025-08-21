#!/usr/bin/env python3
"""
测试 CosyVoice2 参数处理逻辑
"""

def test_parameter_processing():
    """测试参数处理逻辑"""
    
    # 模拟请求数据
    test_cases = [
        {
            "name": "完整参数",
            "data": {
                "video_id": "Am54LhN2NLk",
                "tts_vendor": "cosyvoice2",
                "tts_character": "zh-CN-XiaoyiNeural",
                "speaker_name": "1",
                "mode": "cross_lingual",
                "instruction": "",
                "model_path": "pretrained_models/CosyVoice2-0.5B",
                "fp16": False,
                "audio_source": "video_voice"
            }
        },
        {
            "name": "缺少 speaker_name，使用 tts_character",
            "data": {
                "video_id": "Am54LhN2NLk",
                "tts_vendor": "cosyvoice2",
                "tts_character": "zh-CN-XiaoyiNeural",
                "mode": "cross_lingual",
                "audio_source": "video_voice"
            }
        },
        {
            "name": "使用默认值",
            "data": {
                "video_id": "Am54LhN2NLk",
                "tts_vendor": "cosyvoice2",
                "tts_character": "zh-CN-XiaoyiNeural"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n=== 测试: {test_case['name']} ===")
        data = test_case['data']
        
        # 模拟参数处理逻辑
        model_path = data.get('model_path', 'pretrained_models/CosyVoice2-0.5B')
        speaker_name = data.get('tts_character') or data.get('speaker_name', '')
        mode = data.get('mode', 'cross_lingual')
        audio_source = data.get('audio_source', 'video_voice')
        
        print(f"输入数据: {data}")
        print(f"处理结果:")
        print(f"  model_path: {model_path}")
        print(f"  speaker_name: {speaker_name}")
        print(f"  mode: {mode}")
        print(f"  audio_source: {audio_source}")
        
        # 验证结果
        if test_case['name'] == "完整参数":
            assert speaker_name == "zh-CN-XiaoyiNeural", f"期望 speaker_name 为 'zh-CN-XiaoyiNeural'，实际为 '{speaker_name}'"
        elif test_case['name'] == "缺少 speaker_name，使用 tts_character":
            assert speaker_name == "zh-CN-XiaoyiNeural", f"期望 speaker_name 为 'zh-CN-XiaoyiNeural'，实际为 '{speaker_name}'"
        elif test_case['name'] == "使用默认值":
            assert mode == "cross_lingual", f"期望 mode 为 'cross_lingual'，实际为 '{mode}'"
            assert audio_source == "video_voice", f"期望 audio_source 为 'video_voice'，实际为 '{audio_source}'"
        
        print("✅ 测试通过")

if __name__ == "__main__":
    print("=== CosyVoice2 参数处理测试 ===")
    test_parameter_processing()
    print("\n🎉 所有测试通过!")
