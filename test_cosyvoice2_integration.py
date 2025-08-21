#!/usr/bin/env python3
"""
测试 CosyVoice2 集成
支持零样本语音克隆和跨语种语音生成
"""

import os
import sys
from src.service.tts import get_tts_client

def test_cosyvoice2_integration():
    """测试 CosyVoice2 集成"""
    print("=== 测试 CosyVoice2 集成 ===\n")
    
    # 检查 CosyVoice2 是否可用
    try:
        from src.service.tts import CosyVoice2Client
        print("✅ CosyVoice2Client 可用")
    except ImportError as e:
        print(f"❌ CosyVoice2Client 不可用: {e}")
        return
    
    # 检查参考音频
    print("\n1️⃣ 检查参考音频...")
    reference_audio_dir = "/home/shuzuan/prj/easy-video/CosyVoice/asset"
    reference_audio_file = os.path.join(reference_audio_dir, "zero_shot_prompt.wav")
    
    if not os.path.exists(reference_audio_file):
        print(f"   ⚠️ 参考音频文件不存在: {reference_audio_file}")
        print("   💡 请确保 CosyVoice 目录下有 asset/zero_shot_prompt.wav 文件")
        return
    
    print(f"   ✅ 找到参考音频: {reference_audio_file}")
    
    # 创建测试SRT文件
    print("\n2️⃣ 创建测试SRT文件...")
    test_srt_content = """1
00:00:01,000 --> 00:00:04,000
收到好友从远方寄来的生日礼物，那份意外的惊喜与深深的祝福让我心中充满了甜蜜的快乐，笑容如花儿般绽放。

2
00:00:04,000 --> 00:00:07,000
希望你以后能够做的比我还好呦。
"""
    
    test_srt_file = "test_cosyvoice2.srt"
    with open(test_srt_file, "w", encoding="utf-8") as f:
        f.write(test_srt_content)
    
    print(f"   ✅ 创建测试SRT文件: {test_srt_file}")
    
    # 测试零样本模式
    print("\n3️⃣ 测试零样本模式...")
    try:
        cosyvoice_client = get_tts_client(
            'cosyvoice2',
            model_path='pretrained_models/CosyVoice2-0.5B',
            reference_audio_path=reference_audio_file,
            speaker_name='希望你以后能够做的比我还好呦。',
            fp16=False
        )
        print("   ✅ CosyVoice2 客户端创建成功")
        
        # 测试零样本语音生成
        test_output_dir = "./test_cosyvoice2_zero_shot"
        if os.path.exists(test_output_dir):
            import shutil
            shutil.rmtree(test_output_dir)
        
        result = cosyvoice_client.srt_to_voice(test_srt_file, test_output_dir, mode="zero_shot")
        if result:
            print("   ✅ 零样本模式测试成功")
            
            # 检查生成的文件
            if os.path.exists(test_output_dir):
                files = os.listdir(test_output_dir)
                print(f"   📂 生成了 {len(files)} 个文件:")
                for file in files:
                    file_path = os.path.join(test_output_dir, file)
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        print(f"     📄 {file} ({size} bytes)")
        else:
            print("   ❌ 零样本模式测试失败")
            
    except Exception as e:
        print(f"   ❌ 零样本模式测试异常: {e}")
    
    # 测试跨语种模式
    print("\n4️⃣ 测试跨语种模式...")
    try:
        cross_lingual_srt_content = """1
00:00:01,000 --> 00:00:04,000
<|en|>And then later on, fully acquiring that company. So keeping management in line, interest in line with the asset that's coming into the family is a reason why sometimes we don't buy the whole thing.
"""
        
        cross_lingual_srt_file = "test_cosyvoice2_cross_lingual.srt"
        with open(cross_lingual_srt_file, "w", encoding="utf-8") as f:
            f.write(cross_lingual_srt_content)
        
        cross_lingual_output_dir = "./test_cosyvoice2_cross_lingual"
        if os.path.exists(cross_lingual_output_dir):
            import shutil
            shutil.rmtree(cross_lingual_output_dir)
        
        result = cosyvoice_client.srt_to_voice(cross_lingual_srt_file, cross_lingual_output_dir, mode="cross_lingual")
        if result:
            print("   ✅ 跨语种模式测试成功")
        else:
            print("   ❌ 跨语种模式测试失败")
            
    except Exception as e:
        print(f"   ❌ 跨语种模式测试异常: {e}")
    
    # 测试指令模式
    print("\n5️⃣ 测试指令模式...")
    try:
        instruct_output_dir = "./test_cosyvoice2_instruct"
        if os.path.exists(instruct_output_dir):
            import shutil
            shutil.rmtree(instruct_output_dir)
        
        result = cosyvoice_client.srt_to_voice(test_srt_file, instruct_output_dir, mode="instruct", instruction="用四川话说这句话")
        if result:
            print("   ✅ 指令模式测试成功")
        else:
            print("   ❌ 指令模式测试失败")
            
    except Exception as e:
        print(f"   ❌ 指令模式测试异常: {e}")
    
    # 测试说话人管理
    print("\n6️⃣ 测试说话人管理...")
    try:
        # 添加零样本说话人
        success = cosyvoice_client.add_zero_shot_speaker(
            '希望你以后能够做的比我还好呦。', 
            cosyvoice_client.prompt_speech, 
            'my_zero_shot_spk'
        )
        if success:
            print("   ✅ 添加零样本说话人成功")
            
            # 保存说话人信息
            cosyvoice_client.save_speaker_info()
            print("   ✅ 保存说话人信息成功")
        else:
            print("   ❌ 添加零样本说话人失败")
            
    except Exception as e:
        print(f"   ❌ 说话人管理测试异常: {e}")
    
    print("\n=== 测试完成 ===")
    print("\n💡 说明:")
    print("1. CosyVoice2 支持零样本语音克隆")
    print("2. 支持跨语种语音生成")
    print("3. 支持指令控制语音风格")
    print("4. 可以保存和管理说话人信息")
    print("5. 需要提供参考音频文件")

if __name__ == "__main__":
    test_cosyvoice2_integration()
