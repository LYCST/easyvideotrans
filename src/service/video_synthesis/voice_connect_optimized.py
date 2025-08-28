import os
import srt
import datetime
import subprocess
from src.utils.log_util import WarningFile


def connect_voice_optimized(logger, sourceDir, outputAndPath, warningFilePath):
    """
    优化的语音连接函数，使用FFmpeg避免重新编码
    """
    if not os.path.exists(sourceDir):
        return False

    srtMapFileName = "voiceMap.srt"
    srtMapFileAndPath = os.path.join(sourceDir, srtMapFileName)
    if not os.path.exists(srtMapFileAndPath):
        return False

    # 读取voiceMap.srt
    with open(srtMapFileAndPath, "r", encoding="utf-8") as f:
        voiceMapSrtContent = f.read()

    voiceMapSrt = list(srt.parse(voiceMapSrtContent))
    if not voiceMapSrt:
        return False

    # 尝试使用FFmpeg concat（无重新编码）
    if _try_ffmpeg_concat(logger, sourceDir, voiceMapSrt, outputAndPath):
        return True

    # 回退到pydub（会重新编码）
    logger.warning("FFmpeg concat failed, falling back to pydub (will re-encode)")
    return _fallback_to_pydub(logger, sourceDir, voiceMapSrt, outputAndPath, warningFilePath)


def _try_ffmpeg_concat(logger, sourceDir, voiceMapSrt, outputAndPath):
    """尝试使用FFmpeg concat方法（无重新编码）"""
    try:
        # 创建concat文件列表
        concat_file = os.path.join(sourceDir, "concat_list.txt")
        with open(concat_file, "w", encoding="utf-8") as f:
            for subtitle in voiceMapSrt:
                audio_file = os.path.join(sourceDir, subtitle.content)
                if not os.path.exists(audio_file):
                    return False
                duration = (subtitle.end - subtitle.start).total_seconds()
                f.write(f"file '{audio_file}'\n")
                f.write(f"duration {duration}\n")
            # 添加最后一个文件
            last_audio_file = os.path.join(sourceDir, voiceMapSrt[-1].content)
            f.write(f"file '{last_audio_file}'\n")

        # 执行FFmpeg concat命令
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',  # 关键：不重新编码
            outputAndPath
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        # 清理临时文件
        try:
            os.remove(concat_file)
        except:
            pass

        if result.returncode == 0:
            logger.info("FFmpeg concat successful (no re-encoding)")
            return True
        else:
            logger.warning(f"FFmpeg concat failed: {result.stderr}")
            return False

    except Exception as e:
        logger.warning(f"FFmpeg concat method failed: {e}")
        return False


def _fallback_to_pydub(logger, sourceDir, voiceMapSrt, outputAndPath, warningFilePath):
    """回退到pydub方法（会重新编码）"""
    try:
        from pydub import AudioSegment
        
        # 原有的pydub逻辑
        MAX_SPEED_UP = 1.2
        MIN_SPEED_UP = 1.05
        MIN_GAP_DURATION = 0.1

        duration = voiceMapSrt[-1].end.total_seconds() * 1000
        finalAudioFileAndPath = os.path.join(sourceDir, voiceMapSrt[-1].content)
        finalAudioEnd = voiceMapSrt[-1].start.total_seconds() * 1000
        finalAudioEnd += AudioSegment.from_wav(finalAudioFileAndPath).duration_seconds * 1000
        duration = max(duration, finalAudioEnd)

        diagnosisLog = WarningFile(warningFilePath)
        combined = AudioSegment.silent(duration=duration)
        
        for i in range(len(voiceMapSrt)):
            audioFileAndPath = os.path.join(sourceDir, voiceMapSrt[i].content)
            audio = AudioSegment.from_wav(audioFileAndPath)
            audio = audio.strip_silence(silence_thresh=-40, silence_len=100)
            audio_position = voiceMapSrt[i].start.total_seconds() * 1000

            if i != len(voiceMapSrt) - 1:
                audio_end_position = audio_position + audio.duration_seconds * 1000 + MIN_GAP_DURATION * 1000
                audio_next_position = voiceMapSrt[i + 1].start.total_seconds() * 1000
                if audio_next_position < audio_end_position:
                    position_delta = (audio_next_position - audio_position)
                    speedUp = (audio.duration_seconds * 1000 + MIN_GAP_DURATION * 1000) / position_delta
                    seconds = audio_position / 1000.0
                    timeStr = str(datetime.timedelta(seconds=seconds))
                    if speedUp > MAX_SPEED_UP:
                        logStr = f"Warning: The audio {i + 1} , at {timeStr} , is too short, speed up is {speedUp}."
                        diagnosisLog.write(logStr)

                    if speedUp < MIN_SPEED_UP:
                        logStr = (f"Warning: The audio {i + 1} , at {timeStr} , speed up {speedUp} is too near to 1.0."
                                  f" Set to {MIN_SPEED_UP} forcibly.")
                        diagnosisLog.write(logStr)
                        speedUp = MIN_SPEED_UP
                    audio = audio.speedup(playback_speed=speedUp)

            combined = combined.overlay(audio, position=audio_position)

        combined.export(outputAndPath, format="wav")
        logger.info("Pydub fallback successful (with re-encoding)")
        return True

    except Exception as e:
        logger.error(f"Pydub fallback failed: {e}")
        return False
