from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import os
import subprocess


def zhVideoPreview(logger, videoFileNameAndPath, voiceFileNameAndPath, insturmentFileNameAndPath, srtFileNameAndPath,
                   outputFileNameAndPath, hardcode_subtitles=False, max_chars_per_line=30):
    """
    视频预览合成函数
    
    Args:
        logger: 日志记录器
        videoFileNameAndPath: 视频文件路径
        voiceFileNameAndPath: 人声音频文件路径
        insturmentFileNameAndPath: 背景音乐文件路径
        srtFileNameAndPath: 字幕文件路径
        outputFileNameAndPath: 输出文件路径
        hardcode_subtitles: 是否硬编码字幕到视频中，默认False
        max_chars_per_line: 每行最大字符数，默认30
    """
    
    # 如果启用硬编码字幕且字幕文件存在，使用FFmpeg处理
    if hardcode_subtitles and srtFileNameAndPath and os.path.exists(srtFileNameAndPath):
        return _create_video_with_hardcoded_subtitles(
            videoFileNameAndPath, voiceFileNameAndPath, insturmentFileNameAndPath, 
            srtFileNameAndPath, outputFileNameAndPath, max_chars_per_line
        )
    else:
        # 使用原来的MoviePy方法
        return _create_video_with_moviepy(
            videoFileNameAndPath, voiceFileNameAndPath, insturmentFileNameAndPath, 
            outputFileNameAndPath
        )


def _create_video_with_moviepy(videoFileNameAndPath, voiceFileNameAndPath, insturmentFileNameAndPath, outputFileNameAndPath):
    """使用MoviePy创建视频（不包含硬编码字幕）"""
    # 从moviepy.editor导入VideoFileClip的创建音-视频剪辑
    video_clip = VideoFileClip(videoFileNameAndPath)

    # 加载音频
    voice_clip = None
    if (voiceFileNameAndPath is not None) and os.path.exists(voiceFileNameAndPath):
        voice_clip = AudioFileClip(voiceFileNameAndPath)
    insturment_clip = None
    if (insturmentFileNameAndPath is not None) and os.path.exists(insturmentFileNameAndPath):
        insturment_clip = AudioFileClip(insturmentFileNameAndPath)

    # 组合音频剪辑
    final_audio = None
    if voiceFileNameAndPath is not None and os.path.exists(voiceFileNameAndPath) and insturmentFileNameAndPath is not None and os.path.exists(insturmentFileNameAndPath):
        final_audio = CompositeAudioClip([voice_clip, insturment_clip])
    elif voiceFileNameAndPath is not None and os.path.exists(voiceFileNameAndPath):
        final_audio = voice_clip
    elif insturmentFileNameAndPath is not None and os.path.exists(insturmentFileNameAndPath):
        final_audio = insturment_clip

    # 只有当有音频时才设置音频
    if final_audio is not None:
        video_clip = video_clip.set_audio(final_audio)
    video_clip.write_videofile(outputFileNameAndPath, codec='libx264', audio_codec='aac',
                               remove_temp=True, logger=None)
    video_clip.close()
    return True


def _create_video_with_hardcoded_subtitles(videoFileNameAndPath, voiceFileNameAndPath, insturmentFileNameAndPath, 
                                          srtFileNameAndPath, outputFileNameAndPath, max_chars_per_line=30):
    """使用FFmpeg创建包含硬编码字幕的视频"""
    
    print(f"🎬 开始硬编码字幕视频合成")
    print(f"   原始字幕文件: {srtFileNameAndPath}")
    print(f"   每行字符数: {max_chars_per_line}")
    
    # 处理字幕换行
    processed_srt_path = _process_subtitle_wrapping(srtFileNameAndPath, max_chars_per_line)
    
    # 检查处理后的字幕文件是否存在
    if not os.path.exists(processed_srt_path):
        print(f"❌ 处理后的字幕文件不存在: {processed_srt_path}")
        return False
    
    print(f"✅ 处理后的字幕文件: {processed_srt_path}")
    print(f"   文件大小: {os.path.getsize(processed_srt_path)} 字节")
    
    # 构建FFmpeg命令
    command = ['ffmpeg', '-y']  # -y 表示覆盖输出文件
    
    # 输入文件
    command.extend(['-i', videoFileNameAndPath])
    
    # 音频文件
    if voiceFileNameAndPath and os.path.exists(voiceFileNameAndPath):
        command.extend(['-i', voiceFileNameAndPath])
    
    if insturmentFileNameAndPath and os.path.exists(insturmentFileNameAndPath):
        command.extend(['-i', insturmentFileNameAndPath])
    
    # 字幕文件（使用处理后的字幕文件）
    command.extend(['-i', processed_srt_path])
    
    # 构建复杂的过滤器
    filter_complex = []
    audio_inputs = []
    audio_count = 0
    
    # 添加音频输入
    if voiceFileNameAndPath and os.path.exists(voiceFileNameAndPath):
        audio_inputs.append(f'[{audio_count + 1}:a]')
        audio_count += 1
    
    if insturmentFileNameAndPath and os.path.exists(insturmentFileNameAndPath):
        audio_inputs.append(f'[{audio_count + 1}:a]')
        audio_count += 1
    
    # 音频混合
    if len(audio_inputs) > 1:
        filter_complex.append(f"{' '.join(audio_inputs)}amix=inputs={len(audio_inputs)}[a]")
    elif len(audio_inputs) == 1:
        filter_complex.append(f"{audio_inputs[0]}copy[a]")
    
    # 视频字幕叠加（支持自动换行）
    subtitle_input = audio_count + 1
    
    # 处理字幕文件路径，确保FFmpeg能正确识别
    subtitle_path_for_ffmpeg = processed_srt_path.replace('\\', '/').replace(':', '\\:')
    print(f"   字幕路径(FFmpeg): {subtitle_path_for_ffmpeg}")
    
    filter_complex.append(f"[0:v]subtitles={subtitle_path_for_ffmpeg}:force_style='FontSize=24,PrimaryColour=&Hffffff,OutlineColour=&H000000,BackColour=&H000000,Outline=2,Shadow=1,Alignment=2,MarginV=30'[v]")
    
    # 组合过滤器
    if filter_complex:
        command.extend(['-filter_complex', ';'.join(filter_complex)])
    
    # 输出映射
    command.extend(['-map', '[v]'])
    if len(audio_inputs) > 0:
        command.extend(['-map', '[a]'])
    
    # 编码设置
    command.extend([
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-preset', 'medium',
        '-crf', '23'
    ])
    
    # 输出文件
    command.append(outputFileNameAndPath)
    
    try:
        print(f"执行FFmpeg命令: {' '.join(command)}")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("视频合成成功完成")
        
        # 清理临时文件
        if processed_srt_path != srtFileNameAndPath:
            try:
                os.remove(processed_srt_path)
            except:
                pass
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"视频合成过程中发生错误: {e}")
        return False


def _process_subtitle_wrapping(srt_file_path, max_chars_per_line=30):
    """
    处理字幕换行
    
    Args:
        srt_file_path: 原始字幕文件路径
        max_chars_per_line: 每行最大字符数
        
    Returns:
        str: 处理后的字幕文件路径
    """
    try:
        import srt
        
        # 确保 max_chars_per_line 是整数
        try:
            max_chars_per_line = int(max_chars_per_line)
        except (ValueError, TypeError):
            max_chars_per_line = 30  # 默认值
        
        print(f"字幕换行处理: 文件={srt_file_path}, 每行字符数={max_chars_per_line}")
        
        # 读取原始字幕文件
        with open(srt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析字幕
        subs = list(srt.parse(content))
        print(f"解析到 {len(subs)} 个字幕条目")
        
        # 处理每个字幕的换行
        for i, sub in enumerate(subs):
            try:
                original_content = sub.content
                sub.content = _wrap_text(sub.content, max_chars_per_line)
                if original_content != sub.content:
                    print(f"字幕 {i+1} 已换行处理")
            except Exception as e:
                print(f"处理字幕 {i+1} 时出错: {e}")
                # 继续处理其他字幕
        
        # 生成处理后的字幕文件路径
        base_name = os.path.splitext(srt_file_path)[0]
        processed_path = f"{base_name}_wrapped.srt"
        
        # 写入处理后的字幕文件
        with open(processed_path, 'w', encoding='utf-8') as f:
            f.write(srt.compose(subs))
        
        print(f"字幕换行处理完成: {processed_path}")
        return processed_path
        
    except Exception as e:
        print(f"字幕换行处理失败: {e}")
        return srt_file_path  # 如果处理失败，返回原文件


def _wrap_text(text, max_chars_per_line=30):
    """
    文本换行处理
    
    Args:
        text: 原始文本
        max_chars_per_line: 每行最大字符数
        
    Returns:
        str: 换行后的文本
    """
    # 确保 max_chars_per_line 是整数
    try:
        max_chars_per_line = int(max_chars_per_line)
    except (ValueError, TypeError):
        max_chars_per_line = 30  # 默认值
    
    # 确保 text 是字符串
    if not isinstance(text, str):
        text = str(text)
    
    if len(text) <= max_chars_per_line:
        return text
    
    # 标点符号列表
    punctuation_marks = ['。', '！', '？', '；', '，', '.', '!', '?', ';', ',']
    
    lines = []
    current_line = ""
    char_count = 0
    
    for i, char in enumerate(text):
        current_line += char
        char_count += 1
        
        # 检查是否需要换行
        if char_count >= max_chars_per_line:
            # 情况1：超过字数，且前后5个字内有标点，在标点处换行
            found_punctuation = False
            
            # 向前查找5个字符内的标点
            for j in range(max(0, i-4), i+1):
                if j < len(text) and text[j] in punctuation_marks:
                    # 找到标点，在标点后换行
                    if j < i:  # 标点在当前位置之前
                        # 重新构建当前行，在标点后换行
                        current_line = text[:j+1]
                        remaining_text = text[j+1:]
                        lines.append(current_line)
                        current_line = ""
                        char_count = 0
                        
                        # 处理剩余文本
                        for k, remaining_char in enumerate(remaining_text):
                            current_line += remaining_char
                            char_count += 1
                            if char_count >= max_chars_per_line:
                                # 如果剩余文本也超过限制，直接换行
                                lines.append(current_line)
                                current_line = ""
                                char_count = 0
                        break
                    else:  # 标点就是当前位置
                        lines.append(current_line)
                        current_line = ""
                        char_count = 0
                        found_punctuation = True
                        break
            
            # 情况2：超过字数，前后5个字没有标点，直接在超过字数的地方换行
            if not found_punctuation:
                lines.append(current_line)
                current_line = ""
                char_count = 0
    
    # 添加最后一行
    if current_line:
        lines.append(current_line)
    
    return '\n'.join(lines)



