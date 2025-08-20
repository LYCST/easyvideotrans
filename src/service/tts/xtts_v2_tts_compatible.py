import os
import copy
import srt
import time
import subprocess
import json
from pathlib import Path
from pydub import AudioSegment
from src.service.tts.tts_client import TTSClient


class XTTSv2CompatibleClient(TTSClient):
    """
    XTTS v2 兼容客户端 - 使用命令行接口避免 Python 版本兼容性问题
    支持多语言语音合成，需要提供参考音频
    """
    
    def __init__(self, model_name="tts_models/multilingual/multi-dataset/xtts_v2", 
                 reference_audio_path=None, language="zh"):
        """
        初始化 XTTS v2 兼容客户端
        
        Args:
            model_name: XTTS v2 模型名称
            reference_audio_path: 参考音频文件路径（用于克隆声音）
            language: 目标语言代码 (zh, en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, sv, hu, ko, ja)
        """
        self.model_name = model_name
        self.reference_audio_path = reference_audio_path
        self.language = language
        
        # 检查 TTS 命令行工具是否可用
        self._check_tts_availability()
    
    def _check_tts_availability(self):
        """检查 TTS 命令行工具是否可用"""
        try:
            result = subprocess.run(['tts', '--help'], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise RuntimeError("TTS command not found or not working properly")
            print("TTS command line tool is available")
        except (subprocess.TimeoutExpired, FileNotFoundError, RuntimeError) as e:
            raise ImportError(f"TTS command line tool not available: {e}. Please install TTS: pip install TTS==0.22.0")
    
    def _generate_single_audio(self, text, output_path):
        """
        为单个文本生成音频
        
        Args:
            text: 要合成的文本
            output_path: 输出音频文件路径
        """
        try:
            if not self.reference_audio_path or not os.path.exists(self.reference_audio_path):
                raise ValueError("Reference audio path is required and must exist")
            
            # 使用 TTS 命令行工具生成语音
            cmd = [
                'tts',
                '--text', text,
                '--model_name', self.model_name,
                '--speaker_wav', self.reference_audio_path,
                '--language_idx', self.language,
                '--out_path', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"Generated audio for: {text[:50]}... -> {output_path}")
                return True
            else:
                print(f"Failed to generate audio for: {text[:50]}...")
                print(f"Command output: {result.stdout}")
                print(f"Command error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"Timeout generating audio for: {text[:50]}...")
            return False
        except Exception as e:
            print(f"Error generating audio with XTTS v2: {e}")
            return False
    
    def srt_to_voice(self, srt_file_path, output_dir):
        """
        将 SRT 字幕文件转换为语音文件
        
        Args:
            srt_file_path: SRT 字幕文件路径
            output_dir: 输出目录
        """
        if not os.path.exists(srt_file_path):
            raise FileNotFoundError(f"SRT file not found: {srt_file_path}")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 读取 SRT 文件
        with open(srt_file_path, "r", encoding="utf-8") as file:
            srt_content = file.read()
        
        sub_generator = srt.parse(srt_content)
        sub_title_list = list(sub_generator)
        
        file_names = []
        success_count = 0
        
        print(f"Processing {len(sub_title_list)} subtitle entries with XTTS v2 (compatible mode)...")
        
        for index, sub_title in enumerate(sub_title_list, start=1):
            file_name = f"{index}.wav"
            output_path = os.path.join(output_dir, file_name)
            file_names.append(file_name)
            
            # 生成音频
            if self._generate_single_audio(sub_title.content, output_path):
                success_count += 1
            else:
                # 如果生成失败，创建静音文件作为占位符
                duration_seconds = max(1, len(sub_title.content) / 2.5)
                silence = AudioSegment.silent(duration=int(duration_seconds * 1000))
                silence.export(output_path, format="wav")
                print(f"Created silence placeholder for failed generation: {file_name}")
            
            # 添加延迟避免过载
            time.sleep(0.5)
        
        # 创建语音映射文件
        voice_map_srt = copy.deepcopy(sub_title_list)
        for i, sub_title in enumerate(voice_map_srt):
            sub_title.content = file_names[i]
        
        voice_map_srt_content = srt.compose(voice_map_srt)
        voice_map_srt_path = os.path.join(output_dir, "voiceMap.srt")
        with open(voice_map_srt_path, "w", encoding="utf-8") as file:
            file.write(voice_map_srt_content)
        
        # 保存原始字幕文件
        srt_additional_path = os.path.join(output_dir, "sub.srt")
        with open(srt_additional_path, "w", encoding="utf-8") as file:
            file.write(srt_content)
        
        print(f"XTTS v2 (compatible) processing completed. Success: {success_count}/{len(sub_title_list)}")
        return True
