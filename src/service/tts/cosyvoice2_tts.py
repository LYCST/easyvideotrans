import os
import copy
import srt
import sys
import torch
import torchaudio
from pathlib import Path
from pydub import AudioSegment
from src.service.tts.tts_client import TTSClient

# 添加 CosyVoice 路径到 Python 路径
cosyvoice_path = "/home/shuzuan/prj/easy-video/CosyVoice"
if cosyvoice_path not in sys.path:
    sys.path.append(cosyvoice_path)

# 添加 Matcha-TTS 路径到 Python 路径
matcha_tts_path = os.path.join(cosyvoice_path, "third_party/Matcha-TTS")
if matcha_tts_path not in sys.path:
    sys.path.append(matcha_tts_path)

class CosyVoice2Client(TTSClient):
    """
    CosyVoice2 客户端
    支持零样本语音克隆和跨语种语音生成
    """
    
    def __init__(self, model_path="pretrained_models/CosyVoice2-0.5B", 
                 reference_audio_path=None, speaker_name="", 
                 mode="zero_shot", instruction="",
                 load_jit=False, load_trt=False, load_vllm=False, fp16=False):
        """
        初始化 CosyVoice2 客户端
        
        Args:
            model_path: 模型路径
            reference_audio_path: 参考音频路径（用于零样本语音克隆）
            speaker_name: 说话人名称（用于零样本模式）
            mode: 生成模式 ('zero_shot', 'cross_lingual', 'instruct')
            instruction: 指令（用于指令模式）
            load_jit: 是否加载JIT模型
            load_trt: 是否加载TensorRT模型
            load_vllm: 是否加载vLLM模型
            fp16: 是否使用FP16精度
        """
        self.model_path = model_path
        self.reference_audio_path = reference_audio_path
        self.speaker_name = speaker_name
        self.mode = mode
        self.instruction = instruction
        self.cosyvoice = None
        self.prompt_speech = None
        self._load_model(load_jit, load_trt, load_vllm, fp16)
        self._load_reference_audio()
    
    def _load_model(self, load_jit, load_trt, load_vllm, fp16):
        """加载 CosyVoice2 模型"""
        try:
            from cosyvoice.cli.cosyvoice import CosyVoice2
            # 使用绝对路径
            full_model_path = os.path.join(cosyvoice_path, self.model_path)
            self.cosyvoice = CosyVoice2(full_model_path, load_jit=load_jit, 
                                      load_trt=load_trt, load_vllm=load_vllm, fp16=fp16)
            print(f"CosyVoice2 model loaded: {full_model_path}")
        except Exception as e:
            print(f"Failed to load CosyVoice2 model: {e}")
            raise
    
    def _load_reference_audio(self):
        """加载参考音频并裁剪到30秒"""
        if self.reference_audio_path and os.path.exists(self.reference_audio_path):
            try:
                from cosyvoice.utils.file_utils import load_wav
                import torch
                
                # 加载音频
                self.prompt_speech = load_wav(self.reference_audio_path, 16000)
                
                # 检查音频长度并裁剪到30秒
                sample_rate = 16000
                max_samples = 30 * sample_rate  # 30秒 * 16000Hz = 480000个样本
                
                if self.prompt_speech.shape[-1] > max_samples:
                    print(f"Reference audio too long ({self.prompt_speech.shape[-1]/sample_rate:.1f}s), cropping to 30s")
                    # 从中间部分裁剪30秒
                    start_sample = (self.prompt_speech.shape[-1] - max_samples) // 2
                    self.prompt_speech = self.prompt_speech[..., start_sample:start_sample + max_samples]
                
                print(f"Reference audio loaded and processed: {self.reference_audio_path} ({self.prompt_speech.shape[-1]/sample_rate:.1f}s)")
            except Exception as e:
                print(f"Failed to load reference audio: {e}")
                self.prompt_speech = None
    
    def _generate_single_audio_zero_shot(self, text, output_path):
        """
        使用零样本模式生成音频
        
        Args:
            text: 要合成的文本
            output_path: 输出音频文件路径
        """
        try:
            if self.prompt_speech is None:
                raise ValueError("Reference audio is required for zero-shot mode")
            
            # 使用零样本模式生成语音
            for i, result in enumerate(self.cosyvoice.inference_zero_shot(
                text, self.speaker_name, self.prompt_speech, stream=False)):
                torchaudio.save(output_path, result['tts_speech'], 
                              self.cosyvoice.sample_rate)
                return True
        except Exception as e:
            print(f"Error generating audio with CosyVoice2 zero-shot: {e}")
            return False
    
    def _generate_single_audio_cross_lingual(self, text, output_path):
        """
        使用跨语种模式生成音频
        
        Args:
            text: 要合成的文本
            output_path: 输出音频文件路径
        """
        try:
            if self.prompt_speech is None:
                raise ValueError("Reference audio is required for cross-lingual mode")
            
            # 使用跨语种模式生成语音
            for i, result in enumerate(self.cosyvoice.inference_cross_lingual(
                text, self.prompt_speech, stream=False)):
                torchaudio.save(output_path, result['tts_speech'], 
                              self.cosyvoice.sample_rate)
                return True
        except Exception as e:
            print(f"Error generating audio with CosyVoice2 cross-lingual: {e}")
            return False
    
    def _generate_single_audio_instruct(self, text, instruction, output_path):
        """
        使用指令模式生成音频
        
        Args:
            text: 要合成的文本
            instruction: 指令（如"用四川话说这句话"）
            output_path: 输出音频文件路径
        """
        try:
            if self.prompt_speech is None:
                raise ValueError("Reference audio is required for instruct mode")
            
            # 使用指令模式生成语音
            for i, result in enumerate(self.cosyvoice.inference_instruct2(
                text, instruction, self.prompt_speech, stream=False)):
                torchaudio.save(output_path, result['tts_speech'], 
                              self.cosyvoice.sample_rate)
                return True
        except Exception as e:
            print(f"Error generating audio with CosyVoice2 instruct: {e}")
            return False
    
    def srt_to_voice(self, srt_file_path, output_dir, mode="zero_shot", instruction=""):
        """
        将 SRT 字幕文件转换为语音文件
        
        Args:
            srt_file_path: SRT 字幕文件路径
            output_dir: 输出目录
            mode: 生成模式 ("zero_shot", "cross_lingual", "instruct")
            instruction: 指令（用于instruct模式）
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
        
        print(f"Processing {len(sub_title_list)} subtitle entries with CosyVoice2 ({self.mode} mode)...")
        
        for index, sub_title in enumerate(sub_title_list, start=1):
            file_name = f"{index}.wav"
            output_path = os.path.join(output_dir, file_name)
            file_names.append(file_name)
            
            # 根据模式生成音频
            success = False
            if self.mode == "zero_shot":
                success = self._generate_single_audio_zero_shot(sub_title.content, output_path)
            elif self.mode == "cross_lingual":
                success = self._generate_single_audio_cross_lingual(sub_title.content, output_path)
            elif self.mode == "instruct":
                success = self._generate_single_audio_instruct(sub_title.content, self.instruction, output_path)
            else:
                print(f"Unknown mode: {self.mode}, using zero_shot")
                success = self._generate_single_audio_zero_shot(sub_title.content, output_path)
            
            if success:
                success_count += 1
            else:
                # 如果生成失败，创建静音文件
                duration_seconds = max(1, len(sub_title.content) / 2.5)
                silence = AudioSegment.silent(duration=int(duration_seconds * 1000))
                silence.export(output_path, format="wav")
                print(f"Created silence placeholder for failed generation: {file_name}")
        
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
        
        print(f"CosyVoice2 processing completed. Success: {success_count}/{len(sub_title_list)}")
        return True
    
    def add_zero_shot_speaker(self, speaker_name, prompt_speech, speaker_id):
        """
        添加零样本说话人
        
        Args:
            speaker_name: 说话人名称
            prompt_speech: 提示音频
            speaker_id: 说话人ID
        """
        try:
            success = self.cosyvoice.add_zero_shot_spk(speaker_name, prompt_speech, speaker_id)
            if success:
                print(f"Added zero-shot speaker: {speaker_id}")
                return True
            else:
                print(f"Failed to add zero-shot speaker: {speaker_id}")
                return False
        except Exception as e:
            print(f"Error adding zero-shot speaker: {e}")
            return False
    
    def save_speaker_info(self):
        """保存说话人信息"""
        try:
            self.cosyvoice.save_spkinfo()
            print("Speaker info saved")
        except Exception as e:
            print(f"Error saving speaker info: {e}")
    
    def list_available_speakers(self):
        """列出可用的说话人"""
        try:
            return self.cosyvoice.list_available_spks()
        except Exception as e:
            print(f"Error listing speakers: {e}")
            return []
