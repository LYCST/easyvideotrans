import time

from src.service.video_synthesis.video_preview import zhVideoPreview
from src.task_manager.celery_tasks import celery_app

from prometheus_client import Counter, Histogram
from celery.exceptions import SoftTimeLimitExceeded

# Define Prometheus metrics
VIDEO_PREVIEW_TASK_INVOKED = Counter(
    'video_preview_task_invoked_total', 'Total number of times video preview task is invoked')
VIDEO_PREVIEW_TASK_FAILED = Counter(
    'video_preview_task_failed_total', 'Total number of times video preview task failed')
VIDEO_PREVIEW_TASK_SOFT_TIMEOUT = Counter(
    'video_preview_task_soft_timeout_total', 'Total number of times video preview task failed due to soft timeout')
VIDEO_PREVIEW_TASK_DURATION = Histogram(
    'video_preview_task_duration_seconds', 'Duration of video preview task in seconds')


@celery_app.task(bind=True)
def video_preview_task(self, video_path, voice_path, audio_bg_path, video_out_path, srt_path=None, hardcode_subtitles=False, subtitle_style_dict=None, subtitle_type='translated', is_original_video=False):
    print(f"Invoke video preview task {self.request.id}.")
    print(f"Hardcode subtitles: {hardcode_subtitles}")
    print(f"Subtitle type: {subtitle_type}")
    print(f"Generate original video: {is_original_video}")
    VIDEO_PREVIEW_TASK_INVOKED.inc()
    start_time = time.time()

    try:
        # 如果提供了字幕样式字典，重新创建SubtitleStyle对象
        subtitle_style = None
        if subtitle_style_dict and isinstance(subtitle_style_dict, dict):
            try:
                from src.service.video_synthesis.video_preview import SubtitleStyle
                
                # 获取双语配置
                bilingual_config = subtitle_style_dict.get('bilingual_config', None)
                
                subtitle_style = SubtitleStyle(
                    font_name=subtitle_style_dict.get('font_name', 'Arial'),
                    font_size=subtitle_style_dict.get('font_size', 24),
                    primary_color=subtitle_style_dict.get('primary_color', '&Hffffff'),
                    outline_color=subtitle_style_dict.get('outline_color', '&H000000'),
                    back_color=subtitle_style_dict.get('back_color', '&H000000'),
                    outline_width=subtitle_style_dict.get('outline_width', 2),
                    shadow_depth=subtitle_style_dict.get('shadow_depth', 1),
                    alignment=subtitle_style_dict.get('alignment', 2),
                    margin_v=subtitle_style_dict.get('margin_v', 30),
                    margin_l=subtitle_style_dict.get('margin_l', 10),
                    margin_r=subtitle_style_dict.get('margin_r', 10),
                    auto_scale=subtitle_style_dict.get('auto_scale', True),
                    min_font_size=subtitle_style_dict.get('min_font_size', 16),
                    max_font_size=subtitle_style_dict.get('max_font_size', 32),
                    bilingual_config=bilingual_config
                )
                print(f"字幕样式已重建: {subtitle_style_dict}")
                print(f"bilingual_config: {bilingual_config}")
                print(f"bilingual_config类型: {type(bilingual_config)}")
                if bilingual_config:
                    print(f"双语字幕配置内容: {bilingual_config}")
                else:
                    print("❌ 双语字幕配置为空")
            except Exception as e:
                print(f"字幕样式重建失败: {e}")

        if is_original_video:
            # 生成原始视频（高清视频+原始音频）
            print(f"Generating original video: {video_path} + {voice_path} -> {video_out_path}")
            _ = zhVideoPreview(None, video_path, voice_path, audio_bg_path,
                               srt_path, video_out_path, hardcode_subtitles, subtitle_style, subtitle_type)
        else:
            # 生成预览视频（高清视频+TTS音频+背景音乐）
            print(f"Generating preview video: {video_path} + {voice_path} + {audio_bg_path} -> {video_out_path}")
            _ = zhVideoPreview(None, video_path, voice_path, audio_bg_path,
                               srt_path, video_out_path, hardcode_subtitles, subtitle_style, subtitle_type)
    except SoftTimeLimitExceeded as soft_exception:
        VIDEO_PREVIEW_TASK_SOFT_TIMEOUT.inc()
        print(f"Invoke video preview task {self.request.id} failed with soft timeout: {soft_exception}")
    except Exception as exception:
        VIDEO_PREVIEW_TASK_FAILED.inc()
        print(f"Invoke video preview task {self.request.id} failed with exception: {exception}")
    finally:
        duration = time.time() - start_time
        VIDEO_PREVIEW_TASK_DURATION.observe(duration)
        print(f"Invoke video preview task {self.request.id} took {duration:.2f} seconds.")
