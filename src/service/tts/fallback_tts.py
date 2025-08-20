import os
import copy
import srt
import requests
import time
from pydub import AudioSegment
from src.service.tts.tts_client import TTSClient


class FallbackTTSClient(TTSClient):
    """
    备用TTS客户端，使用多种备选方案
    """
    
    def __init__(self, character="zh-CN-XiaoyiNeural"):
        self.character = character
        self.available_services = [
            self._try_edge_tts_alternative,
            self._try_simple_silence,
        ]
    
    def _try_edge_tts_alternative(self, text, output_path):
        """
        尝试使用edge-tts的替代方法
        """
        try:
            import edge_tts
            import asyncio
            
            async def generate_speech():
                # 使用不同的参数重试
                communicate = edge_tts.Communicate(
                    text, 
                    voice=self.character,
                    rate="+0%",
                    volume="+0%"
                )
                await communicate.save(output_path)
            
            # 使用新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(generate_speech())
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    return True
            finally:
                loop.close()
        except Exception as e:
            print(f"Edge TTS alternative failed: {e}")
        
        return False
    
    def _try_simple_silence(self, text, output_path):
        """
        生成对应时长的静音文件作为占位符
        """
        try:
            # 估算文本对应的音频时长（大约每秒2-3个中文字符）
            duration_seconds = max(1, len(text) / 2.5)
            
            # 生成静音音频
            silence = AudioSegment.silent(duration=int(duration_seconds * 1000))  # 毫秒
            silence.export(output_path, format="mp3")
            
            print(f"Generated silence placeholder for: {text[:50]}... (duration: {duration_seconds:.1f}s)")
            return True
        except Exception as e:
            print(f"Failed to generate silence: {e}")
            return False
    
    def _generate_single_audio(self, text, output_path):
        """
        为单个文本生成音频，尝试多种方法
        """
        for service in self.available_services:
            try:
                if service(text, output_path):
                    return True
                time.sleep(0.5)  # 在不同服务间稍作延迟
            except Exception as e:
                print(f"Service failed: {e}")
                continue
        
        print(f"All TTS services failed for text: {text[:50]}...")
        return False
    
    def srt_to_voice(self, srt_file_path, output_dir):
        """
        将SRT文件转换为语音文件
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(srt_file_path, "r", encoding="utf-8") as file:
            srt_content = file.read()

        sub_generator = srt.parse(srt_content)
        sub_title_list = list(sub_generator)
        file_names = []
        successful_count = 0

        print(f"Processing {len(sub_title_list)} subtitle segments...")

        for index, sub_title in enumerate(sub_title_list, start=1):
            file_name = f"{index}.wav"
            mp3_file_name = f"{index}.mp3"
            mp3_path = os.path.join(output_dir, mp3_file_name)
            wav_path = os.path.join(output_dir, file_name)
            file_names.append(file_name)

            print(f"Processing segment {index}/{len(sub_title_list)}: {sub_title.content[:50]}...")
            
            # 生成MP3文件
            if self._generate_single_audio(sub_title.content, mp3_path):
                try:
                    # 转换MP3到WAV
                    if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 0:
                        sound = AudioSegment.from_mp3(mp3_path)
                        sound.export(wav_path, format="wav")
                        os.remove(mp3_path)
                        successful_count += 1
                        print(f"Successfully processed segment {index}")
                    else:
                        print(f"MP3 file is empty or missing for segment {index}")
                except Exception as e:
                    print(f"Failed to convert MP3 to WAV for segment {index}: {e}")
            else:
                print(f"Failed to generate audio for segment {index}")

        print(f"TTS processing complete: {successful_count}/{len(sub_title_list)} segments successful")

        # 生成voice map和其他必要文件
        voice_map_srt = copy.deepcopy(sub_title_list)
        for i, sub_title in enumerate(voice_map_srt):
            sub_title.content = file_names[i]

        voice_map_srt_content = srt.compose(voice_map_srt)
        voice_map_srt_path = os.path.join(output_dir, "voiceMap.srt")
        with open(voice_map_srt_path, "w", encoding="utf-8") as file:
            file.write(voice_map_srt_content)

        srt_additional_path = os.path.join(output_dir, "sub.srt")
        with open(srt_additional_path, "w", encoding="utf-8") as file:
            file.write(srt_content)

        if successful_count > 0:
            print("TTS conversion completed with some success")
            return True
        else:
            print("TTS conversion failed completely")
            return False
