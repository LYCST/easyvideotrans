from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import os
import subprocess
import srt
import re


class SubtitleStyle:
    """字幕样式配置类"""
    
    def __init__(self, 
                 font_name="Arial",
                 font_size=24,
                 primary_color="&Hffffff",  # 白色
                 outline_color="&H000000",  # 黑色
                 back_color="&H000000",     # 黑色背景
                 outline_width=2,
                 shadow_depth=1,
                 alignment=2,  # 2=底部居中
                 margin_v=30,
                 margin_l=10,
                 margin_r=10,
                 auto_scale=True,
                 min_font_size=16,
                 max_font_size=32,
                 bilingual_config=None):
        
        self.font_name = font_name
        self.font_size = font_size
        self.primary_color = primary_color
        self.outline_color = outline_color
        self.back_color = back_color
        self.outline_width = outline_width
        self.shadow_depth = shadow_depth
        self.alignment = alignment
        self.margin_v = margin_v
        self.margin_l = margin_l
        self.margin_r = margin_r
        self.auto_scale = auto_scale
        self.min_font_size = min_font_size
        self.max_font_size = max_font_size
        
        # 双语字幕配置
        self.bilingual_config = bilingual_config or {}
    
    def to_ffmpeg_style(self):
        """转换为FFmpeg样式字符串"""
        return (f"FontName={self.font_name},"
                f"FontSize={self.font_size},"
                f"PrimaryColour={self.primary_color},"
                f"OutlineColour={self.outline_color},"
                f"BackColour={self.back_color},"
                f"Outline={self.outline_width},"
                f"Shadow={self.shadow_depth},"
                f"Alignment={self.alignment},"
                f"MarginV={self.margin_v},"
                f"MarginL={self.margin_l},"
                f"MarginR={self.margin_r}")
    
    def get_secondary_style(self):
        """获取副字体样式（用于双语字幕）"""
        if not self.bilingual_config:
            return None
            
        secondary_font_name = self.bilingual_config.get('secondary_font_name', self.font_name)
        secondary_font_size = self.bilingual_config.get('secondary_font_size', self.font_size)
        secondary_color = self.bilingual_config.get('secondary_color', self.primary_color)
        
        return {
            'font_name': secondary_font_name,
            'font_size': secondary_font_size,
            'primary_color': secondary_color,
            'outline_color': self.outline_color,
            'back_color': self.back_color,
            'outline_width': self.outline_width,
            'shadow_depth': self.shadow_depth,
            'alignment': self.alignment,
            'margin_v': self.margin_v,
            'margin_l': self.margin_l,
            'margin_r': self.margin_r,
            'vertical_spacing': self.bilingual_config.get('vertical_spacing', 5)
        }


def create_bilingual_ass_subtitle(srt_path, subtitle_style):
    """
    创建双语ASS字幕文件，支持中英文不同样式
    
    Args:
        srt_path: 原始SRT字幕文件路径
        subtitle_style: 字幕样式配置对象
    
    Returns:
        str: ASS字幕文件路径，失败返回None
    """
    try:
        import srt
        
        # 读取原始字幕文件
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析字幕
        subs = list(srt.parse(content))
        print(f"处理 {len(subs)} 个双语字幕条目")
        
        # 获取副字体样式
        secondary_style = subtitle_style.get_secondary_style()
        if not secondary_style:
            print("❌ 未找到双语字幕配置")
            return None
        
        # 检查原始字幕文件是否存在且可读
        if not os.path.exists(srt_path):
            print(f"❌ 原始字幕文件不存在: {srt_path}")
            return None
        
        if os.path.getsize(srt_path) == 0:
            print(f"❌ 原始字幕文件为空: {srt_path}")
            return None
        
        # 创建ASS文件路径
        ass_path = srt_path.replace('.srt', '.ass')
        
        # 生成ASS文件头部
        ass_header = f"""[Script Info]
Title: Bilingual Subtitles
ScriptType: v4.00+
WrapStyle: 1
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Chinese,{subtitle_style.font_name},{subtitle_style.font_size},{subtitle_style.primary_color},&H000000,{subtitle_style.outline_color},{subtitle_style.back_color},0,0,0,0,100,100,0,0,1,{subtitle_style.outline_width},{subtitle_style.shadow_depth},{subtitle_style.alignment},{subtitle_style.margin_l},{subtitle_style.margin_r},{subtitle_style.margin_v + secondary_style['vertical_spacing']},1
Style: English,{secondary_style['font_name']},{secondary_style['font_size']},{secondary_style['primary_color']},&H000000,{secondary_style['outline_color']},{secondary_style['back_color']},0,0,0,0,100,100,0,0,1,{secondary_style['outline_width']},{secondary_style['shadow_depth']},{secondary_style['alignment']},{secondary_style['margin_l']},{secondary_style['margin_r']},{subtitle_style.margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        # 生成ASS事件
        ass_events = []
        for i, sub in enumerate(subs):
            # 分离中英文内容
            lines = sub.content.split('\n')
            if len(lines) >= 2:
                chinese_text = lines[0].strip()
                english_text = lines[1].strip()
                
                # 转换时间格式 (timedelta对象)
                start_total_seconds = int(sub.start.total_seconds())
                end_total_seconds = int(sub.end.total_seconds())
                
                start_hours = start_total_seconds // 3600
                start_minutes = (start_total_seconds % 3600) // 60
                start_seconds = start_total_seconds % 60
                start_centiseconds = int((sub.start.microseconds % 1000000) // 10000)
                
                end_hours = end_total_seconds // 3600
                end_minutes = (end_total_seconds % 3600) // 60
                end_seconds = end_total_seconds % 60
                end_centiseconds = int((sub.end.microseconds % 1000000) // 10000)
                
                start_time = f"{start_hours:01d}:{start_minutes:02d}:{start_seconds:02d}.{start_centiseconds:02d}"
                end_time = f"{end_hours:01d}:{end_minutes:02d}:{end_seconds:02d}.{end_centiseconds:02d}"
                
                # 创建两个事件：中文在上，英文在下
                if chinese_text:
                    ass_events.append(f"Dialogue: 1,{start_time},{end_time},Chinese,,0,0,0,,{chinese_text}")
                if english_text:
                    ass_events.append(f"Dialogue: 0,{start_time},{end_time},English,,0,0,0,,{english_text}")
        
        # 写入ASS文件
        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(ass_header)
            f.write('\n'.join(ass_events))
        
        # 验证ASS文件是否创建成功
        if not os.path.exists(ass_path):
            print(f"❌ ASS文件创建失败: {ass_path}")
            return None
        
        if os.path.getsize(ass_path) == 0:
            print(f"❌ ASS文件为空: {ass_path}")
            return None
        
        print(f"✅ 双语ASS字幕文件已创建: {ass_path} (大小: {os.path.getsize(ass_path)} 字节)")
        return ass_path
        
    except Exception as e:
        print(f"❌ 创建双语ASS字幕文件失败: {e}")
        return None


def create_adaptive_subtitle_srt(original_srt_path, style_config, max_chars_per_line=50):
    """
    创建自适应字体大小的字幕文件
    
    Args:
        original_srt_path: 原始字幕文件路径
        style_config: 字幕样式配置
        max_chars_per_line: 每行最大字符数（用于判断是否需要缩小字体）
    
    Returns:
        str: 处理后的字幕文件路径
    """
    try:
        # 读取原始字幕文件
        with open(original_srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析字幕
        subs = list(srt.parse(content))
        print(f"处理 {len(subs)} 个字幕条目")
        
        # 处理每个字幕
        for i, sub in enumerate(subs):
            # 计算字幕长度（去除换行符）
            text_length = len(sub.content.replace('\n', ''))
            
            # 如果启用自动缩放且字幕较长
            if style_config.auto_scale and text_length > max_chars_per_line:
                # 计算缩放比例
                scale_ratio = min(1.0, max_chars_per_line / text_length)
                new_font_size = max(style_config.min_font_size, 
                                  int(style_config.font_size * scale_ratio))
                
                # 创建临时样式配置
                temp_style = SubtitleStyle(
                    font_name=style_config.font_name,
                    font_size=new_font_size,
                    primary_color=style_config.primary_color,
                    outline_color=style_config.outline_color,
                    back_color=style_config.back_color,
                    outline_width=style_config.outline_width,
                    shadow_depth=style_config.shadow_depth,
                    alignment=style_config.alignment,
                    margin_v=style_config.margin_v,
                    margin_l=style_config.margin_l,
                    margin_r=style_config.margin_r,
                    auto_scale=False  # 避免递归缩放
                )
                
                # 为这个字幕添加样式标记
                sub.content = f"{{\\r\\an{temp_style.alignment}\\fs{new_font_size}\\c{temp_style.primary_color}\\3c{temp_style.outline_color}\\4c{temp_style.back_color}\\3a{temp_style.outline_width*255//10}\\4a&H80&}}{sub.content}"
                
                print(f"字幕 {i+1} 已缩放: {text_length}字符 -> 字体大小{new_font_size}")
        
        # 生成处理后的字幕文件路径
        base_name = os.path.splitext(original_srt_path)[0]
        processed_path = f"{base_name}_styled.srt"
        
        # 写入处理后的字幕文件
        with open(processed_path, 'w', encoding='utf-8') as f:
            f.write(srt.compose(subs))
        
        print(f"自适应字幕文件已生成: {processed_path}")
        return processed_path
        
    except Exception as e:
        print(f"创建自适应字幕文件失败: {e}")
        return original_srt_path


def get_subtitle_file_path(output_path, video_id, subtitle_type):
    """
    根据字幕类型获取字幕文件路径
    
    Args:
        output_path: 输出目录
        video_id: 视频ID
        subtitle_type: 字幕类型 ('original', 'translated', 'bilingual')
    
    Returns:
        str: 字幕文件路径
    """
    if subtitle_type == 'original':
        return os.path.join(output_path, f"{video_id}_en_merged.srt")
    elif subtitle_type == 'translated':
        return os.path.join(output_path, f"{video_id}_zh_merged.srt")
    elif subtitle_type == 'bilingual':
        return os.path.join(output_path, f"{video_id}_bilingual.srt")
    else:
        # 默认使用翻译字幕
        return os.path.join(output_path, f"{video_id}_zh_merged.srt")


def zhVideoPreview(logger, videoFileNameAndPath, voiceFileNameAndPath, insturmentFileNameAndPath, srtFileNameAndPath,
                   outputFileNameAndPath, hardcode_subtitles=False, subtitle_style=None, subtitle_type='translated'):
    """
    生成视频预览
    
    Args:
        logger: 日志记录器
        videoFileNameAndPath: 视频文件路径
        voiceFileNameAndPath: 语音文件路径
        insturmentFileNameAndPath: 背景音乐文件路径
        srtFileNameAndPath: 字幕文件路径
        outputFileNameAndPath: 输出文件路径
        hardcode_subtitles: 是否硬编码字幕
        subtitle_style: 字幕样式配置对象
        subtitle_type: 字幕类型 ('original', 'translated', 'bilingual')
    """
    print(f"🎬 开始视频预览合成")
    print(f"   视频文件: {videoFileNameAndPath}")
    print(f"   语音文件: {voiceFileNameAndPath}")
    print(f"   背景音乐: {insturmentFileNameAndPath}")
    print(f"   字幕类型: {subtitle_type}")
    
    # 如果启用硬编码字幕且字幕文件存在，使用FFmpeg处理（需要重新编码视频）
    if hardcode_subtitles and srtFileNameAndPath and os.path.exists(srtFileNameAndPath):
        return _create_video_with_hardcoded_subtitles(
            videoFileNameAndPath, voiceFileNameAndPath, insturmentFileNameAndPath, 
            srtFileNameAndPath, outputFileNameAndPath, subtitle_style
        )
    else:
        # 不硬编码字幕时使用优化的FFmpeg方法（视频流复制，只重新编码音频）
        return _create_video_with_ffmpeg_fast(
            videoFileNameAndPath, voiceFileNameAndPath, insturmentFileNameAndPath, 
            outputFileNameAndPath
        )


def _create_video_with_ffmpeg_fast(videoFileNameAndPath, voiceFileNameAndPath, insturmentFileNameAndPath, outputFileNameAndPath):
    """使用FFmpeg快速创建视频（视频流复制，只重新编码音频）"""
    
    print(f"🎬 开始快速视频合成（视频流复制）")
    print(f"   视频文件: {videoFileNameAndPath}")
    print(f"   人声音频: {voiceFileNameAndPath}")
    print(f"   背景音乐: {insturmentFileNameAndPath}")
    
    # 构建FFmpeg命令
    command = ['ffmpeg', '-y']  # -y 表示覆盖输出文件
    
    # 输入文件
    command.extend(['-i', videoFileNameAndPath])
    
    # 音频文件
    audio_inputs = []
    if voiceFileNameAndPath and os.path.exists(voiceFileNameAndPath):
        command.extend(['-i', voiceFileNameAndPath])
        audio_inputs.append(f'[1:a]')
    
    if insturmentFileNameAndPath and os.path.exists(insturmentFileNameAndPath):
        command.extend(['-i', insturmentFileNameAndPath])
        audio_inputs.append(f'[{len(audio_inputs) + 1}:a]')
    
    # 构建过滤器
    filter_complex = []
    
    # 音频混合
    if len(audio_inputs) > 1:
        filter_complex.append(f"{' '.join(audio_inputs)}amix=inputs={len(audio_inputs)}[a]")
    elif len(audio_inputs) == 1:
        # 对于单个音频，使用 aresample 确保兼容性
        filter_complex.append(f"{audio_inputs[0]}aresample=async=1[a]")
    
    # 组合过滤器
    if filter_complex:
        command.extend(['-filter_complex', ';'.join(filter_complex)])
    
    # 输出映射
    command.extend(['-map', '0:v'])  # 复制视频流
    if len(audio_inputs) > 0:
        command.extend(['-map', '[a]'])  # 使用混合后的音频
    
    # 编码设置 - 视频流复制，只重新编码音频
    command.extend([
        '-c:v', 'copy',  # 视频流直接复制，不重新编码
        '-c:a', 'aac',   # 音频重新编码为AAC
        '-b:a', '192k'   # 音频比特率
    ])
    
    # 输出文件
    command.append(outputFileNameAndPath)
    
    try:
        print(f"执行FFmpeg命令: {' '.join(command)}")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("快速视频合成成功完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"视频合成过程中发生错误: {e}")
        return False


def _create_video_with_moviepy(videoFileNameAndPath, voiceFileNameAndPath, insturmentFileNameAndPath, outputFileNameAndPath):
    """使用MoviePy创建视频（不包含硬编码字幕）- 保留作为备用方案"""
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
                                          srtFileNameAndPath, outputFileNameAndPath, subtitle_style=None):
    """使用FFmpeg创建包含硬编码字幕的视频"""
    
    print(f"🎬 开始硬编码字幕视频合成")
    print(f"   原始字幕文件: {srtFileNameAndPath}")
    
    # 检查字幕文件是否存在
    if not os.path.exists(srtFileNameAndPath):
        print(f"❌ 字幕文件不存在: {srtFileNameAndPath}")
        return False
    
    # 检查字幕文件大小，确保不是空文件
    if os.path.getsize(srtFileNameAndPath) == 0:
        print(f"❌ 字幕文件为空: {srtFileNameAndPath}")
        return False
    
    # 检查字幕文件是否可读
    try:
        with open(srtFileNameAndPath, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if not first_line:
                print(f"❌ 字幕文件内容无效: {srtFileNameAndPath}")
                return False
    except Exception as e:
        print(f"❌ 字幕文件读取失败: {srtFileNameAndPath}, 错误: {e}")
        return False
    
    # 检查字幕文件类型
    is_ass_subtitle = srtFileNameAndPath.endswith('.ass')
    print(f"🔍 字幕文件类型: {'ASS' if is_ass_subtitle else 'SRT'}")
    
    # 初始化processed_srt_path变量
    processed_srt_path = None
    
    # 如果提供了样式配置且启用了自动缩放，创建自适应字幕文件
    if subtitle_style and subtitle_style.auto_scale and not is_ass_subtitle:
        print(f"🔄 启用自适应字体大小功能")
        processed_srt_path = create_adaptive_subtitle_srt(srtFileNameAndPath, subtitle_style)
        if processed_srt_path != srtFileNameAndPath:
            print(f"✅ 使用自适应字幕文件: {processed_srt_path}")
            srtFileNameAndPath = processed_srt_path
    else:
        print(f"✅ 使用字幕文件: {srtFileNameAndPath}")
    
    print(f"   文件大小: {os.path.getsize(srtFileNameAndPath)} 字节")
    
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
    command.extend(['-i', srtFileNameAndPath])
    
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
        # 对于单个音频，使用 aresample 确保兼容性
        filter_complex.append(f"{audio_inputs[0]}aresample=async=1[a]")
    
    # 视频字幕叠加
    subtitle_input = audio_count + 1
    
    # 处理字幕文件路径，确保FFmpeg能正确识别
    subtitle_path_for_ffmpeg = srtFileNameAndPath.replace('\\', '/').replace(':', '\\:')
    print(f"   字幕路径(FFmpeg): {subtitle_path_for_ffmpeg}")
    
    # 如果是ASS格式的字幕文件，使用ass滤镜
    if srtFileNameAndPath.endswith('.ass'):
        print(f"   使用ASS字幕滤镜")
        filter_complex.append(f"[0:v]ass={subtitle_path_for_ffmpeg}[v]")
    else:
        # 使用传入的subtitle_style，如果没有则使用默认样式
        if subtitle_style:
            style_str = subtitle_style.to_ffmpeg_style()
            print(f"   字幕样式: {style_str}")
        else:
            style_str = "FontSize=24,PrimaryColour=&Hffffff,OutlineColour=&H000000,BackColour=&H000000,Outline=2,Shadow=1,Alignment=2,MarginV=30"
            print(f"   使用默认字幕样式")
        
        filter_complex.append(f"[0:v]subtitles={subtitle_path_for_ffmpeg}:force_style='{style_str}'[v]")
    
    # 组合过滤器
    if filter_complex:
        command.extend(['-filter_complex', ';'.join(filter_complex)])
    
    # 输出映射
    command.extend(['-map', '[v]'])
    if len(audio_inputs) > 0:
        command.extend(['-map', '[a]'])
    
    # 编码设置 - 硬编码字幕时需要重新编码视频，但使用快速预设
    command.extend([
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-preset', 'ultrafast',  # 使用最快的编码预设
        '-crf', '28'            # 稍微降低质量以提高速度
    ])
    
    # 输出文件
    command.append(outputFileNameAndPath)
    
    try:
        print(f"执行FFmpeg命令: {' '.join(command)}")
        
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"✅ 硬编码字幕视频合成成功")
        
        # 清理临时文件
        if processed_srt_path and processed_srt_path != srtFileNameAndPath and os.path.exists(processed_srt_path):
            try:
                os.remove(processed_srt_path)
                print(f"🧹 已清理临时字幕文件: {processed_srt_path}")
            except Exception as e:
                print(f"⚠️ 清理临时文件失败: {e}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ 视频合成过程中发生错误: {e}")
        return False



