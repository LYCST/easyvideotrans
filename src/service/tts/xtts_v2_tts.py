import os
import copy
import srt
import time
import torch
import numpy as np
from pathlib import Path
from pydub import AudioSegment
from src.service.tts.tts_client import TTSClient

try:
    from TTS.api import TTS
    XTTS_AVAILABLE = True
except ImportError:
    XTTS_AVAILABLE = False
    print("Warning: XTTS v2 not available. Install with: pip install TTS")


class XTTSv2Client(TTSClient):
    """
    XTTS v2 (Coqui TTS) 客户端
    支持多语言语音合成，需要提供参考音频
    """
    
    def __init__(self, model_name="tts_models/multilingual/multi-dataset/xtts_v2", 
                 reference_audio_path=None, language="zh"):
        """
        初始化 XTTS v2 客户端
        
        Args:
            model_name: XTTS v2 模型名称
            reference_audio_path: 参考音频文件路径（用于克隆声音）
            language: 目标语言代码 (zh, en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, sv, hu, ko, ja)
        """
        self.model_name = model_name
        self.reference_audio_path = reference_audio_path
        self.language = language
        self.tts_model = None
        
        if not XTTS_AVAILABLE:
            raise ImportError("XTTS v2 not available. Install with: pip install TTS")
        
        # 初始化模型
        self._load_model()
    
    def _load_model(self):
        """加载 XTTS v2 模型"""
        try:
            print(f"Loading XTTS v2 model: {self.model_name}")
            self.tts_model = TTS(self.model_name).to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
            print("XTTS v2 model loaded successfully")
        except Exception as e:
            print(f"Failed to load XTTS v2 model: {e}")
            raise
    
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
            
            # 使用 XTTS v2 生成语音
            self.tts_model.tts_to_file(
                text=text,
                speaker_wav=self.reference_audio_path,
                language=self.language,
                file_path=output_path
            )
            
            # 验证生成的音频文件
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"Generated audio for: {text[:50]}... -> {output_path}")
                return True
            else:
                print(f"Failed to generate audio for: {text[:50]}...")
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
        
        print(f"Processing {len(sub_title_list)} subtitle entries with XTTS v2...")
        
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
            time.sleep(0.1)
        
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
        
        print(f"XTTS v2 processing completed. Success: {success_count}/{len(sub_title_list)}")
        return True
