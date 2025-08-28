#!/usr/bin/env python3
"""
音频片段提取器
用于从音频中提取有说话内容的片段，用于TTS学习
"""

import os
import numpy as np
import librosa
import soundfile as sf
from typing import Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)


class AudioSegmentExtractor:
    def __init__(self, min_speech_duration: float = 30.0, 
                 speech_threshold: float = 0.01,
                 min_speech_interval: float = 2.0):
        """
        初始化音频片段提取器
        
        Args:
            min_speech_duration: 最小语音片段时长（秒）
            speech_threshold: 语音检测阈值
            min_speech_interval: 最小语音间隔（秒）
        """
        self.min_speech_duration = min_speech_duration
        self.speech_threshold = speech_threshold
        self.min_speech_interval = min_speech_interval
    
    def detect_speech_segments(self, audio_path: str) -> List[Tuple[float, float]]:
        """
        检测音频中的语音片段
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            List[Tuple[float, float]]: 语音片段列表，每个元素为(开始时间, 结束时间)
        """
        try:
            # 加载音频
            y, sr = librosa.load(audio_path, sr=None)
            
            # 计算音频的RMS能量
            frame_length = int(0.025 * sr)  # 25ms帧
            hop_length = int(0.010 * sr)    # 10ms跳跃
            
            rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
            
            # 归一化RMS
            rms_normalized = rms / np.max(rms)
            
            # 检测语音活动
            speech_frames = rms_normalized > self.speech_threshold
            
            # 找到连续的语音片段
            segments = self._find_continuous_segments(speech_frames, hop_length, sr)
            
            # 过滤太短的片段
            segments = [seg for seg in segments if seg[1] - seg[0] >= self.min_speech_interval]
            
            logger.info(f"检测到 {len(segments)} 个语音片段")
            for i, (start, end) in enumerate(segments):
                logger.info(f"  片段 {i+1}: {start:.2f}s - {end:.2f}s (时长: {end-start:.2f}s)")
            
            return segments
            
        except Exception as e:
            logger.error(f"检测语音片段失败: {e}")
            return []
    
    def _find_continuous_segments(self, speech_frames: np.ndarray, hop_length: int, sr: int) -> List[Tuple[float, float]]:
        """
        找到连续的语音片段
        
        Args:
            speech_frames: 语音帧标记
            hop_length: 跳跃长度
            sr: 采样率
            
        Returns:
            List[Tuple[float, float]]: 语音片段列表
        """
        segments = []
        start_frame = None
        
        for i, is_speech in enumerate(speech_frames):
            if is_speech and start_frame is None:
                start_frame = i
            elif not is_speech and start_frame is not None:
                end_frame = i
                start_time = start_frame * hop_length / sr
                end_time = end_frame * hop_length / sr
                segments.append((start_time, end_time))
                start_frame = None
        
        # 处理最后一个片段
        if start_frame is not None:
            end_time = len(speech_frames) * hop_length / sr
            start_time = start_frame * hop_length / sr
            segments.append((start_time, end_time))
        
        return segments
    
    def extract_best_speech_segment(self, audio_path: str, target_duration: float = 30.0) -> Optional[Tuple[float, float]]:
        """
        提取最佳的语音片段
        
        Args:
            audio_path: 音频文件路径
            target_duration: 目标时长（秒）
            
        Returns:
            Optional[Tuple[float, float]]: 最佳片段的(开始时间, 结束时间)，如果没有找到则返回None
        """
        segments = self.detect_speech_segments(audio_path)
        
        if not segments:
            logger.warning("未检测到语音片段")
            return None
        
        # 找到最接近目标时长的片段
        best_segment = None
        best_score = float('inf')
        
        for start, end in segments:
            duration = end - start
            
            # 如果片段太短，跳过
            if duration < self.min_speech_duration:
                continue
            
            # 计算与目标时长的差异
            score = abs(duration - target_duration)
            
            # 优先选择接近目标时长的片段
            if score < best_score:
                best_score = score
                best_segment = (start, end)
        
        if best_segment:
            logger.info(f"选择最佳片段: {best_segment[0]:.2f}s - {best_segment[1]:.2f}s (时长: {best_segment[1] - best_segment[0]:.2f}s)")
        else:
            logger.warning("未找到合适的语音片段")
        
        return best_segment
    
    def extract_audio_segment(self, audio_path: str, start_time: float, end_time: float, 
                            output_path: str) -> bool:
        """
        提取音频片段并保存
        
        Args:
            audio_path: 输入音频文件路径
            start_time: 开始时间（秒）
            end_time: 结束时间（秒）
            output_path: 输出文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            # 加载音频
            y, sr = librosa.load(audio_path, sr=None)
            
            # 计算采样点
            start_sample = int(start_time * sr)
            end_sample = int(end_time * sr)
            
            # 确保不超出边界
            start_sample = max(0, start_sample)
            end_sample = min(len(y), end_sample)
            
            # 提取片段
            segment = y[start_sample:end_sample]
            
            # 保存音频片段
            sf.write(output_path, segment, sr)
            
            logger.info(f"音频片段已保存: {output_path}")
            logger.info(f"  时长: {end_time - start_time:.2f}s")
            logger.info(f"  采样率: {sr}Hz")
            
            return True
            
        except Exception as e:
            logger.error(f"提取音频片段失败: {e}")
            return False
    
    def extract_tts_training_audio(self, audio_path: str, output_path: str, 
                                 target_duration: float = 30.0) -> bool:
        """
        提取用于TTS训练的音频片段
        
        Args:
            audio_path: 输入音频文件路径
            output_path: 输出文件路径
            target_duration: 目标时长（秒）
            
        Returns:
            bool: 是否成功
        """
        logger.info(f"开始提取TTS训练音频片段")
        logger.info(f"  输入文件: {audio_path}")
        logger.info(f"  目标时长: {target_duration}秒")
        
        # 检测最佳语音片段
        best_segment = self.extract_best_speech_segment(audio_path, target_duration)
        
        if not best_segment:
            logger.error("未找到合适的语音片段")
            return False
        
        start_time, end_time = best_segment
        
        # 如果片段太长，截取中间部分
        if end_time - start_time > target_duration:
            center_time = (start_time + end_time) / 2
            start_time = center_time - target_duration / 2
            end_time = center_time + target_duration / 2
            logger.info(f"截取中间部分: {start_time:.2f}s - {end_time:.2f}s")
        
        # 提取音频片段
        success = self.extract_audio_segment(audio_path, start_time, end_time, output_path)
        
        if success:
            logger.info(f"TTS训练音频片段提取成功: {output_path}")
        else:
            logger.error("TTS训练音频片段提取失败")
        
        return success


def extract_tts_training_audio(audio_path: str, output_path: str, 
                             target_duration: float = 30.0) -> bool:
    """
    便捷函数：提取TTS训练音频片段
    
    Args:
        audio_path: 输入音频文件路径
        output_path: 输出文件路径
        target_duration: 目标时长（秒）
        
    Returns:
        bool: 是否成功
    """
    extractor = AudioSegmentExtractor()
    return extractor.extract_tts_training_audio(audio_path, output_path, target_duration)


if __name__ == "__main__":
    # 测试代码
    import sys
    
    if len(sys.argv) != 3:
        print("用法: python audio_segment_extractor.py <输入音频文件> <输出音频文件>")
        sys.exit(1)
    
    input_audio = sys.argv[1]
    output_audio = sys.argv[2]
    
    success = extract_tts_training_audio(input_audio, output_audio, 30.0)
    
    if success:
        print(f"✅ 音频片段提取成功: {output_audio}")
    else:
        print(f"❌ 音频片段提取失败")
        sys.exit(1)
