import os
import json
import requests
import zipfile
import shutil
import uuid
from src.service.video_synthesis.voice_connect import connect_voice
from src.service.translation import get_translator
from src.service.tts import get_tts_client
from src.workload_client import EasyVideoTransWorkloadClient
from src.task_manager.celery_tasks.tasks import video_preview_task
from src.task_manager.celery_tasks.celery_utils import get_queue_length
from src.utils.video_validator import validate_video_file
from werkzeug.utils import secure_filename
from pytubefix import YouTube
from moviepy.editor import VideoFileClip
from functools import wraps
from flask import Flask, request, jsonify, render_template, send_from_directory
from prometheus_flask_exporter import PrometheusMetrics
from src.service.video_synthesis.video_preview import get_subtitle_file_path

app = Flask(__name__, template_folder="./appendix/templates", static_folder="./appendix/static")
app.config.from_file("./configs/easyvideotrans.json", load=json.load)
metrics = PrometheusMetrics(app)
metrics.info('pytvzhen_web', 'Pytvzhen backend API', version='1.0.0')

PYTVZHEN_STAGE = 'PYTVZHEN_STAGE'
pytvzhen_api_request_counter = metrics.counter(
    'pytvzhen_api_request_counter', 'Request count by request paths',
    labels={'base_url': lambda: url_rule_to_base(request.url_rule), 'stage': lambda: pytvzhen_stage(),
            'method': lambda: request.method, 'status': lambda r: r.status_code}
)

tts_request_counter = metrics.counter(
    'tts_request_counter', 'TTS request count by vendor',
    labels={'vendor': lambda: getattr(request, '_tts_vendor', 'unknown'), 'stage': lambda: pytvzhen_stage()}
)

tts_duration_histogram = metrics.histogram(
    'tts_duration_seconds', 'TTS processing duration in seconds',
    labels={'vendor': lambda: getattr(request, '_tts_vendor', 'unknown'), 'stage': lambda: pytvzhen_stage()}
)

# Setup workloads client to submit any GPU workloads to EasyVideoTrans compute backend
gpu_workload = EasyVideoTransWorkloadClient(
    audio_separation_endpoint=app.config['VOICE_BACKGROUND_SEPARATION_ENDPOINT'],
    audio_transcribe_endpoint=app.config['AUDIO_TRANSCRIBE_ENDPOINT'],
)


def pytvzhen_stage():
    return os.environ[PYTVZHEN_STAGE] if PYTVZHEN_STAGE in os.environ else 'default'


def log_info_return_str(message):
    app.logger.info(message)
    return message


def log_error_return_str(message):
    app.logger.error(message)
    return message


def log_warning_return_str(message):
    app.logger.warning(message)
    return message


def url_rule_to_base(url_rule):
    base_path = str(url_rule)
    return base_path.split('<')[0].rstrip('/')


def require_video_id_from_post_request(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        if not request.is_json:
            return jsonify({"message": "Missing JSON in request"}), 400

        data = request.get_json()

        if 'video_id' not in data:
            return jsonify({"message": "Missing 'video_id' in request"}), 400

        video_id = data['video_id']
        return func(video_id)

    return decorated_func


log_info_return_str(f"Launching Pytvzhen config: \n\t{app.config}")


@app.route('/', methods=['GET'])
@metrics.do_not_track()
def index():
    return render_template('index.html')


ALLOWED_EXTENSIONS = {'mp4'}


def video_extension_allowed(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()


def unique_video_fn_with_extension(extension):
    video_id = str(uuid.uuid4())
    return video_id, video_id + '.' + extension


@app.route('/video_upload', methods=['POST'])
@pytvzhen_api_request_counter
def video_upload():
    output_path = app.config['OUTPUT_PATH']

    # check if the post request has the file part
    if 'file' not in request.files:
        return jsonify(error='No file part in the POST request'), 400

    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify(error='No selected file from frontend'), 400

    if file and video_extension_allowed(file.filename):
        filename = secure_filename(file.filename)
        file_ext = get_extension(filename)
        video_id, video_fn = unique_video_fn_with_extension(file_ext)

        file.save(os.path.join(output_path, video_fn))
        return jsonify({"message": log_info_return_str(f"Video {file.filename} uploaded as {video_fn}"),
                        "video_id": video_id})
    else:
        return jsonify({"message", log_error_return_str(f"Video upload failed: {file.filename} extension not allowed")})


@app.route('/yt_thumbnail', methods=['POST'])
@pytvzhen_api_request_counter
@require_video_id_from_post_request
def yt_thumbnail(video_id):
    output_path = app.config['OUTPUT_PATH']
    thumbnail_fn = f"{video_id}_thumbnail.png"

    if os.path.isfile(thumbnail_fn):
        return send_from_directory(output_path, thumbnail_fn, mimetype='image/png')

    thumbnail_save_path = os.path.join(output_path, thumbnail_fn)
    try:
        yt = YouTube(f'https://www.youtube.com/watch?v={video_id}', proxies=None)

        response = requests.get(yt.thumbnail_url)
        if response.status_code == 200:
            with open(thumbnail_save_path, 'wb') as file:
                file.write(response.content)
            return send_from_directory(output_path, thumbnail_fn, mimetype='image/png')

        raise Exception(f"thumbnail download failed: {response.status_code} {response.content}")
    except Exception as e:
        exception = e

    return jsonify({"message": log_error_return_str(
        f'An error occurred while downloading video thumbnail {video_id} to {thumbnail_save_path}: {exception}')}), 500


@app.route('/yt_download', methods=['POST'])
@pytvzhen_api_request_counter
@require_video_id_from_post_request
def yt_download(video_id):
    """下载 YouTube 视频：分离下载音频和高清视频"""
    output_path = app.config['OUTPUT_PATH']

    # 文件命名
    audio_fn = f"{video_id}_audio.wav"  # 音频文件
    video_hd_fn = f"{video_id}_hd.mp4"  # 高清视频（无音频）
    audio_save_path = os.path.join(output_path, audio_fn)
    video_hd_save_path = os.path.join(output_path, video_hd_fn)

    # 检查文件是否存在且有效
    need_download_audio = True
    need_download_hd = True
    
    # 检查音频文件
    if os.path.exists(audio_save_path):
        file_size = os.path.getsize(audio_save_path)
        if file_size > 0:
            need_download_audio = False
            app.logger.info(f"音频文件已存在，跳过下载: {audio_save_path} ({file_size/1024:.2f} KB)")
        else:
            app.logger.warning(f"音频文件无效，将重新下载: {audio_save_path}")
            try:
                os.remove(audio_save_path)
            except Exception as e:
                app.logger.error(f"删除无效音频文件失败: {e}")
    
    # 检查高清视频文件
    if os.path.exists(video_hd_save_path):
        is_valid, error_msg = validate_video_file(video_hd_save_path)
        if is_valid:
            need_download_hd = False
            app.logger.info(f"高清视频文件已存在，跳过下载: {video_hd_save_path}")
        else:
            app.logger.warning(f"高清视频文件无效，将重新下载: {video_hd_save_path}, 错误: {error_msg}")
            try:
                os.remove(video_hd_save_path)
            except Exception as e:
                app.logger.error(f"删除无效高清视频文件失败: {e}")

    # 如果两个文件都有效，直接返回
    if not need_download_audio and not need_download_hd:
        return jsonify({"message": log_info_return_str(f"Audio and HD video already exist and are valid, skip downloading."),
                        "video_id": video_id,
                        "audio_file": audio_fn,
                        "hd_video_file": video_hd_fn}), 200

    try:
        # 限制视频长度
        yt = YouTube(f'https://www.youtube.com/watch?v={video_id}', proxies=None)
        if yt.length > app.config['VIDEO_MAX_DURATION']:
            return jsonify({"message": log_error_return_str(
                f'Video duration is too long. Please select videos with duration less than {app.config["VIDEO_MAX_DURATION"]} seconds. ')}), 400

        # 下载音频
        if need_download_audio:
            app.logger.info(f"开始下载音频: {video_id}")
            audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            if audio_stream:
                audio_stream.download(output_path=output_path, filename=audio_fn)
                app.logger.info(f"音频下载完成: {audio_save_path}")
            else:
                return jsonify({"message": log_error_return_str("No audio stream found")}), 500

        # 下载高清视频（无音频）
        if need_download_hd:
            app.logger.info(f"开始下载高清视频: {video_id}")
            video_stream = yt.streams.filter(progressive=False, file_extension='mp4').order_by('resolution').desc().first()
            if video_stream:
                video_stream.download(output_path=output_path, filename=video_hd_fn)
                
                # 验证下载的文件
                is_valid, error_msg = validate_video_file(video_hd_save_path)
                if not is_valid:
                    return jsonify({"message": log_error_return_str(
                        f'Downloaded HD video file is invalid: {error_msg}')}), 500
                
                app.logger.info(f"高清视频下载完成: {video_hd_save_path}")
            else:
                return jsonify({"message": log_error_return_str("No HD video stream found")}), 500

        return jsonify({"message": log_info_return_str(
            f"Download audio and HD video for {video_id} successfully."),
            "video_id": video_id,
            "audio_file": audio_fn,
            "hd_video_file": video_hd_fn}), 200
    except Exception as e:
        exception = e
        return jsonify({"message": log_error_return_str(
            f'An error occurred while downloading {video_id}: {exception}')}), 500


@app.route('/yt/<video_id>', methods=['GET'])
@pytvzhen_api_request_counter
def yt_serve(video_id):
    output_path = app.config['OUTPUT_PATH']
    video_fn = f'{video_id}.mp4'

    if os.path.exists(os.path.join(output_path, video_fn)):
        return send_from_directory(output_path, video_fn, as_attachment=True)

    return jsonify({"message": log_warning_return_str(f'Video {video_fn} not found at {output_path}')}), 404


@app.route('/extra_audio', methods=['POST'])
@pytvzhen_api_request_counter
@require_video_id_from_post_request
def extra_audio(video_id):
    output_path = app.config['OUTPUT_PATH']

    # 使用下载的音频文件，而不是从视频提取
    audio_fn = f'{video_id}_audio.wav'
    audio_path = os.path.join(output_path, audio_fn)

    if os.path.exists(audio_path):
        return jsonify({"message": log_info_return_str(f"Audio already exists at {audio_path}, skip extracting."),
                        "video_id": video_id}), 200

    # 如果下载的音频不存在，尝试从标清视频提取（兼容性）
    video_fn = f'{video_id}.mp4'
    video_path = os.path.join(output_path, video_fn)
    
    if not os.path.exists(video_path):
        return jsonify({"message": log_warning_return_str(
            f'Downloaded audio {audio_fn} not found at {output_path}, and video {video_fn} not found, please download first')}), 404

    try:
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)
        return jsonify({"message": log_info_return_str(f"Extracted audio {audio_fn} from {video_path} successfully."),
                        "video_id": video_id}), 200

    except Exception as e:
        exception = e

    return jsonify({"message": log_error_return_str(
        f'An error occurred while extracting audio {audio_fn} from {video_fn}: {exception}')}), 500


@app.route('/audio/<video_id>', methods=['GET'])
@pytvzhen_api_request_counter
def audio_serve(video_id):
    output_path = app.config['OUTPUT_PATH']

    # 优先使用下载的音频文件
    audio_fn = f'{video_id}_audio.wav'
    audio_path = os.path.join(output_path, audio_fn)

    if os.path.exists(audio_path):
        return send_from_directory(output_path, audio_fn, as_attachment=True)

    # 兼容性：如果下载的音频不存在，尝试使用提取的音频
    audio_fn_legacy = f'{video_id}.wav'
    audio_path_legacy = os.path.join(output_path, audio_fn_legacy)

    if os.path.exists(audio_path_legacy):
        return send_from_directory(output_path, audio_fn_legacy, as_attachment=True)

    return jsonify({"message": log_warning_return_str(f'Audio {audio_fn} or {audio_fn_legacy} not found at {output_path}')}), 404


@app.route('/remove_audio_bg', methods=['POST'])
@pytvzhen_api_request_counter
@require_video_id_from_post_request
def remove_audio_bg(video_id):
    output_path = app.config['OUTPUT_PATH']

    # 优先使用下载的音频文件
    audio_fn = f'{video_id}_audio.wav'
    audio_path = os.path.join(output_path, audio_fn)
    
    # 如果下载的音频不存在，尝试使用提取的音频（兼容性）
    if not os.path.exists(audio_path):
        audio_fn = f'{video_id}.wav'
        audio_path = os.path.join(output_path, audio_fn)
    
    audio_no_bg_fn, audio_bg_fn = f'{video_id}_no_bg.wav', f'{video_id}_bg.wav'
    audio_no_bg_path, audio_bg_fn_path = (os.path.join(output_path, audio_no_bg_fn),
                                         os.path.join(output_path, audio_bg_fn))

    if os.path.exists(audio_no_bg_path) and os.path.exists(audio_bg_fn_path):
        return jsonify({"message": log_info_return_str(
            f"Audio already exists at {audio_no_bg_path} and {audio_bg_fn_path}, skip removing background music."),
            "video_id": video_id}), 200

    if not os.path.exists(audio_path):
        return jsonify({"message": log_warning_return_str(
            f'Audio to remove background music for {audio_fn} '
            f'not found at {output_path}, please download or extract it first')}), 404

    try:
        audio_bg_fn_path, audio_no_bg_fn = gpu_workload.separate_audio(audio_fn)
        
        # 重命名文件以匹配期望的文件名格式
        # 从 Am54LhN2NLk_audio_bg.wav 重命名为 Am54LhN2NLk_bg.wav
        # 从 Am54LhN2NLk_audio_no_bg.wav 重命名为 Am54LhN2NLk_no_bg.wav
        expected_bg_fn = f'{video_id}_bg.wav'
        expected_no_bg_fn = f'{video_id}_no_bg.wav'
        
        audio_bg_path = os.path.join(output_path, audio_bg_fn_path)
        audio_no_bg_path = os.path.join(output_path, audio_no_bg_fn)
        expected_bg_path = os.path.join(output_path, expected_bg_fn)
        expected_no_bg_path = os.path.join(output_path, expected_no_bg_fn)
        
        # 重命名文件
        if os.path.exists(audio_bg_path) and audio_bg_path != expected_bg_path:
            os.rename(audio_bg_path, expected_bg_path)
            app.logger.info(f"Renamed {audio_bg_fn_path} to {expected_bg_fn}")
            
        if os.path.exists(audio_no_bg_path) and audio_no_bg_path != expected_no_bg_path:
            os.rename(audio_no_bg_path, expected_no_bg_path)
            app.logger.info(f"Renamed {audio_no_bg_fn} to {expected_no_bg_fn}")
        
        return jsonify({"message": log_info_return_str(
            f"Remove background music for {audio_fn} as {expected_no_bg_fn} and {expected_bg_fn} successfully."),
            "video_id": video_id}), 200

    except Exception as e:
        exception = e

    return jsonify({"message": log_error_return_str(
        f'An error occurred while removing background music for {audio_fn} as {expected_no_bg_fn} and {expected_bg_fn}: {exception}')}), 500


@app.route('/audio_no_bg/<video_id>', methods=['GET'])
@pytvzhen_api_request_counter
def audio_no_bg_serve(video_id):
    output_path = app.config['OUTPUT_PATH']

    audio_no_bg_fn = f'{video_id}_no_bg.wav'
    audio_no_bg_path = os.path.join(output_path, audio_no_bg_fn)

    if os.path.exists(audio_no_bg_path):
        return send_from_directory(output_path, audio_no_bg_fn, as_attachment=True)

    return jsonify({"message": log_warning_return_str(
        f'Audio without background music {audio_no_bg_fn} not found at {audio_no_bg_path}')}), 404


@app.route('/audio_bg/<video_id>', methods=['GET'])
@pytvzhen_api_request_counter
def audio_bg_serve(video_id):
    output_path = app.config['OUTPUT_PATH']

    audio_bg_fn = f'{video_id}_bg.wav'
    audio_bg_path = os.path.join(output_path, audio_bg_fn)

    if os.path.exists(audio_bg_path):
        return send_from_directory(output_path, audio_bg_fn, as_attachment=True)

    return jsonify({"message": log_warning_return_str(
        f'Audio with background music only {audio_bg_fn} not found at {audio_bg_path}')}), 404


@app.route('/transcribe', methods=['POST'])
@pytvzhen_api_request_counter
@require_video_id_from_post_request
def transcribe(video_id):
    output_path = app.config['OUTPUT_PATH']

    en_srt_fn, en_srt_merged_fn, audio_no_bg_fn = f'{video_id}_en.srt', f'{video_id}_en_merged.srt', f'{video_id}_no_bg.wav'

    en_srt_path, en_srt_merged_path, audio_no_bg_path = (os.path.join(output_path, en_srt_fn),
                                                         os.path.join(output_path, en_srt_merged_fn),
                                                         os.path.join(output_path, audio_no_bg_fn))

    if os.path.exists(en_srt_path) and os.path.exists(en_srt_merged_path):
        return jsonify({"message": log_info_return_str(
            f"English subtitles already exists at {en_srt_fn} and {en_srt_merged_fn}, skip generating."),
            "video_id": video_id}), 200

    if not os.path.exists(audio_no_bg_path):
        jsonify({"message": log_warning_return_str(
            f'Audio with voice '
            f'not found at {audio_no_bg_path}, please extract it first')}), 404

    try:
        gpu_workload.transcribe_audio(audio_no_bg_fn, [en_srt_fn, en_srt_merged_fn])
        return jsonify({"message": log_info_return_str(
            f"Transcribed SRT from {audio_no_bg_fn} as {en_srt_fn} and {en_srt_merged_fn} successfully."),
            "video_id": video_id}), 200

    except Exception as e:
        exception = e

    return jsonify({"message": log_error_return_str(
        f'An error occurred while transcribing SRT from {audio_no_bg_fn} as {en_srt_fn} and {en_srt_merged_fn}: {exception}')}), 500


@app.route('/srt_en/<video_id>', methods=['GET'])
def srt_en_serve(video_id):
    output_path = app.config['OUTPUT_PATH']

    en_srt_fn = f'{video_id}_en.srt'
    en_srt_path = os.path.join(output_path, en_srt_fn)

    if os.path.exists(en_srt_path):
        return send_from_directory(output_path, en_srt_fn, as_attachment=True)

    return jsonify({"message": log_warning_return_str(
        f'Transcribed English SRT {en_srt_fn} not found at {en_srt_path}')}), 404


@app.route('/translate_to_zh', methods=['POST'])
@pytvzhen_api_request_counter
@require_video_id_from_post_request
def transhlate_to_zh(video_id):
    output_path = app.config['OUTPUT_PATH']
    en_srt_merged_fn = f'{video_id}_en_merged.srt'
    zh_srt_merged_fn = f'{video_id}_zh_merged.srt'
    en_srt_merged_path = os.path.join(output_path, en_srt_merged_fn)
    zh_srt_merged_path = os.path.join(output_path, zh_srt_merged_fn)
    data = request.get_json()
    translateVendor = data['translate_vendor']
    api_key = data['translate_key']
    
    # 获取本地部署相关参数
    base_url = data.get('base_url', None)
    model_name = data.get('model_name', None)

    if not os.path.exists(en_srt_merged_path):
        return jsonify({"message": log_warning_return_str(
            f'English SRT {en_srt_merged_fn} not found at {en_srt_merged_path}')}), 404

    # 检查支持的翻译厂商
    if translateVendor not in ["google", "deepl"] and "gpt" not in translateVendor:
        return jsonify({"message": log_warning_return_str("Unsupported translate vendor.")}), 404

    try:
        # 设置缓存目录在output_path下
        cache_dir = os.path.join(output_path, "translation_cache")
        translator = get_translator(translateVendor, api_key, proxies=None, base_url=base_url, model_name=model_name, cache_dir=cache_dir)
        ret = translator.translate_srt(source_file_name_and_path=en_srt_merged_path,
                                       output_file_name_and_path=zh_srt_merged_path)
        if ret:
            return jsonify({"message": log_info_return_str(
                f"using {translateVendor} translate to translate SRT from {en_srt_merged_fn} to {zh_srt_merged_fn} successfully."),
                "video_id": video_id}), 200
        else:
            return jsonify({"message": log_warning_return_str(f"{translateVendor} translate failed.")}), 404
    except ValueError as e:
        return jsonify({"message": log_warning_return_str(str(e))}), 404


@app.route('/srt_en_merged/<video_id>', methods=['GET'])
@pytvzhen_api_request_counter
def srt_en_merged_serve(video_id):
    output_path = app.config['OUTPUT_PATH']

    en_srt_merged_fn = f'{video_id}_en_merged.srt'
    en_srt_merged_path = os.path.join(output_path, en_srt_merged_fn)

    if os.path.exists(en_srt_merged_path):
        return send_from_directory(output_path, en_srt_merged_fn, as_attachment=True)

    return jsonify({"message": log_warning_return_str(
        f'Transcribed English SRT {en_srt_merged_fn} not found at {en_srt_merged_path}')}), 404


@app.route('/generate_bilingual_srt', methods=['POST'])
@pytvzhen_api_request_counter
@require_video_id_from_post_request
def generate_bilingual_srt(video_id):
    """生成中英文双语字幕"""
    output_path = app.config['OUTPUT_PATH']
    
    # 字幕文件路径
    en_srt_merged_fn = f'{video_id}_en_merged.srt'
    zh_srt_merged_fn = f'{video_id}_zh_merged.srt'
    bilingual_srt_fn = f'{video_id}_bilingual.srt'
    
    en_srt_merged_path = os.path.join(output_path, en_srt_merged_fn)
    zh_srt_merged_path = os.path.join(output_path, zh_srt_merged_fn)
    bilingual_srt_path = os.path.join(output_path, bilingual_srt_fn)
    
    # 检查双语字幕是否已存在
    if os.path.exists(bilingual_srt_path):
        return jsonify({"message": log_info_return_str(
            f"Bilingual SRT {bilingual_srt_fn} already exists at {bilingual_srt_path}"),
            "video_id": video_id}), 200
    
    # 检查英文和中文字幕是否存在
    if not os.path.exists(en_srt_merged_path):
        return jsonify({"message": log_warning_return_str(
            f'English SRT {en_srt_merged_fn} not found at {en_srt_merged_path}')}), 404
    
    if not os.path.exists(zh_srt_merged_path):
        return jsonify({"message": log_warning_return_str(
            f'Chinese SRT {zh_srt_merged_fn} not found at {zh_srt_merged_path}')}), 404
    
    try:
        # 生成双语字幕
        success = _merge_bilingual_srt(en_srt_merged_path, zh_srt_merged_path, bilingual_srt_path)
        
        if success:
            return jsonify({"message": log_info_return_str(
                f"Generated bilingual SRT {bilingual_srt_fn} successfully."),
                "video_id": video_id}), 200
        else:
            return jsonify({"message": log_error_return_str(
                f"Failed to generate bilingual SRT {bilingual_srt_fn}")}), 500
            
    except Exception as e:
        return jsonify({"message": log_error_return_str(
            f'An error occurred while generating bilingual SRT: {str(e)}')}), 500


@app.route('/srt_bilingual/<video_id>', methods=['GET'])
@pytvzhen_api_request_counter
def srt_bilingual_serve(video_id):
    """下载双语字幕文件"""
    output_path = app.config['OUTPUT_PATH']
    
    bilingual_srt_fn = f'{video_id}_bilingual.srt'
    bilingual_srt_path = os.path.join(output_path, bilingual_srt_fn)
    
    if os.path.exists(bilingual_srt_path):
        return send_from_directory(output_path, bilingual_srt_fn, as_attachment=True)
    
    return jsonify({"message": log_warning_return_str(
        f'Bilingual SRT {bilingual_srt_fn} not found at {bilingual_srt_path}')}), 404


@app.route('/translated_zh_upload', methods=['POST'])
@pytvzhen_api_request_counter
def translated_zh_upload():
    video_id = request.form['video_id']
    output_path = app.config['OUTPUT_PATH']
    # check if the post request has the file part
    if 'file' not in request.files:
        return jsonify(error='No file part in the POST request'), 400

    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file and get_extension(file.filename):
        filename = video_id + "_zh_merged.srt"
        print("save:" + filename)
        file.save(os.path.join(output_path, filename))
        return jsonify({"message": log_info_return_str(f"SRT {filename} uploaded")})
    else:
        return jsonify({"message", log_error_return_str(f"Video upload failed: {file.filename} extension not allowed")})


@app.route('/srt_zh_merged/<video_id>', methods=['GET'])
@pytvzhen_api_request_counter
def srt_zh_merged_serve(video_id):
    output_path = app.config['OUTPUT_PATH']

    zh_srt_merged_fn = f'{video_id}_zh_merged.srt'
    zh_srt_merged_path = os.path.join(output_path, zh_srt_merged_fn)

    if os.path.exists(zh_srt_merged_path):
        return send_from_directory(output_path, zh_srt_merged_fn, as_attachment=True)

    return jsonify({"message": log_warning_return_str(
        f'Transcribed English SRT {zh_srt_merged_fn} not found at {zh_srt_merged_path}')}), 404


@app.route('/voice_connect', methods=['POST'])
@pytvzhen_api_request_counter
@require_video_id_from_post_request
def voice_connect(video_id):
    output_path = app.config['OUTPUT_PATH']

    data = request.get_json()
    voiceDir = os.path.join(output_path, video_id + "_zh_source")
    voice_connect_fn = video_id + "_zh.wav"
    voice_connect_path = os.path.join(output_path, voice_connect_fn)
    warning_log_fn = video_id + "_connect_warning.log"
    warning_log_path = os.path.join(output_path, warning_log_fn)

    if not os.path.exists(voiceDir):
        return jsonify({"message": log_warning_return_str(
            f'Voice directory {voiceDir} not found at {output_path}')}), 404

    ret = connect_voice(app.logger, voiceDir, voice_connect_path, warning_log_path)
    if ret:
        return jsonify({"message": log_info_return_str(
            f"Voice connect {voice_connect_fn} successfully."),
            "video_id": video_id}), 200
    else:
        return jsonify({"message": log_warning_return_str("Voice connect failed.")}), 404


@app.route('/voice_connect_log/<video_id>', methods=['GET'])
@pytvzhen_api_request_counter
def voice_connect_log_serve(video_id):
    output_path = app.config['OUTPUT_PATH']

    warning_log_fn = video_id + "_connect_warning.log"
    warning_log_path = os.path.join(output_path, warning_log_fn)

    if os.path.exists(warning_log_path):
        return send_from_directory(output_path, warning_log_fn, as_attachment=True)

    return jsonify({"message": log_warning_return_str(
        f'Voice connect {warning_log_path} not found at {warning_log_path}')}), 404


@app.route('/voice_connect/<video_id>', methods=['GET'])
@pytvzhen_api_request_counter
def voice_connect_serve(video_id):
    output_path = app.config['OUTPUT_PATH']

    voice_connect_fn = video_id + "_zh.wav"
    voice_connect_path = os.path.join(output_path, voice_connect_fn)

    if os.path.exists(voice_connect_path):
        return send_from_directory(output_path, voice_connect_fn, as_attachment=True)

    return jsonify({"message": log_warning_return_str(
        f'Voice connect {voice_connect_fn} not found at {voice_connect_path}')}), 404


@app.route('/tts', methods=['POST'])
@pytvzhen_api_request_counter
@tts_request_counter
@tts_duration_histogram
@require_video_id_from_post_request
def tts(video_id):
    import time
    import json

    start_time = time.time()
    output_path = app.config['OUTPUT_PATH']

    data = request.get_json()
    srt_fn = f'{video_id}_zh_merged.srt'
    srt_path = os.path.join(output_path, srt_fn)
    tts_dir = os.path.join(output_path, video_id + "_zh_source")
    
    # 获取 TTS 参数
    tts_vendor = data.get('tts_vendor')
    character = data.get('tts_character', '')
    reference_audio_path = data.get('reference_audio_path')
    language = data.get('language', 'zh')
    model_name = data.get('model_name', 'tts_models/multilingual/multi-dataset/xtts_v2')
    tts_params = data.get('tts_params', {})
    # Set vendor for metrics
    request._tts_vendor = tts_vendor
    
    if not os.path.exists(srt_path):
        return jsonify({"message": log_warning_return_str(
            f'Chinese SRT {srt_fn} not found at {output_path}')}), 404

    if os.path.exists(tts_dir):
        # delete old tts dir
        shutil.rmtree(tts_dir)

    try:
        # 根据 TTS 供应商创建客户端
        if tts_vendor == 'xtts_v2':
            # Parse XTTS v2 parameters from request data
            language = data.get('language', 'zh')
            model_name = data.get('model_name', 'tts_models/multilingual/multi-dataset/xtts_v2')
            audio_source = data.get('audio_source', 'video_voice')
            
            # 如果选择使用视频人声，自动查找视频的人声文件
            if audio_source == 'video_voice' and not reference_audio_path:
                video_voice_path = os.path.join(output_path, f'{video_id}_no_bg.wav')
                if os.path.exists(video_voice_path):
                    reference_audio_path = video_voice_path
                    print(f"Using video voice as reference for XTTS v2: {reference_audio_path}")
                else:
                    return jsonify({"message": log_warning_return_str(
                        f"Video voice file not found: {video_voice_path}. Please process the video first.")}), 404
            
            if not reference_audio_path:
                return jsonify({"message": log_warning_return_str(
                    "Reference audio path is required for XTTS v2")}), 400
            
            if not os.path.exists(reference_audio_path):
                return jsonify({"message": log_warning_return_str(
                    f"Reference audio file not found: {reference_audio_path}")}), 404
            
            tts_client = get_tts_client(
                tts_vendor, 
                character=character,
                reference_audio_path=reference_audio_path,
                language=language,
                model_name=model_name
            )
        elif tts_vendor == 'openai':
            # Parse OpenAI parameters
            if isinstance(tts_params, str):
                try:
                    tts_params = json.loads(tts_params) if tts_params else {}
                except json.JSONDecodeError:
                    tts_params = {}

            voice = character or tts_params.get('voice', 'alloy')
            model = tts_params.get('model', 'tts-1')
            instructions = tts_params.get('instructions', None)

            tts_client = get_tts_client("openai", voice=voice, model=model, instructions=instructions)
        elif tts_vendor == 'edge':
            tts_client = get_tts_client("edge", character)
        elif tts_vendor == 'cosyvoice2':
            # Parse CosyVoice2 parameters from request data with defaults
            model_path = data.get('model_path', 'pretrained_models/CosyVoice2-0.5B')
            reference_audio_path = data.get('reference_audio_path')
            # 使用 tts_character 作为 speaker_name，如果没有则使用 speaker_name
            speaker_name = data.get('tts_character') or data.get('speaker_name', '')
            mode = data.get('mode', 'cross_lingual')
            instruction = data.get('instruction', '')
            fp16 = data.get('fp16', False)
            audio_source = data.get('audio_source', 'video_voice')

            # 如果选择使用视频人声，自动查找视频的人声文件
            if audio_source == 'video_voice' and not reference_audio_path:
                video_voice_path = os.path.join(output_path, f'{video_id}_no_bg.wav')
                if os.path.exists(video_voice_path):
                    reference_audio_path = video_voice_path
                    print(f"Using video voice as reference: {reference_audio_path}")
                else:
                    return jsonify({"message": log_warning_return_str(
                        f"Video voice file not found: {video_voice_path}. Please process the video first.")}), 404

            tts_client = get_tts_client(
                "cosyvoice2",
                model_path=model_path,
                reference_audio_path=reference_audio_path,
                speaker_name=speaker_name,
                mode=mode,
                instruction=instruction,
                fp16=fp16
            )
        elif tts_vendor == 'fallback':
            tts_client = get_tts_client("fallback", character)
        else:
             return jsonify({"message": log_warning_return_str(f"Unsupported TTS vendor: {tts_vendor}")}), 400
        
        tts_client.srt_to_voice(srt_path, tts_dir)
        duration = time.time() - start_time
        return jsonify({"message": log_info_return_str(f"TTS success using {tts_vendor} (took {duration:.2f}s)."),"video_id": video_id, "duration": duration}), 200

    except Exception as e:
        exception = e

    return jsonify({"message": log_error_return_str(f"TTS failed: {exception}")}), 500


@app.route('/tts/<video_id>', methods=['GET'])
@pytvzhen_api_request_counter
def tts_serve(video_id):
    output_path = app.config['OUTPUT_PATH']

    tts_dir = os.path.join(output_path, video_id + "_zh_source")
    tts_zip_fn = video_id + "_zh_source.zip"
    tts_zip_path = os.path.join(output_path, tts_zip_fn)
    if not os.path.exists(tts_dir):
        return jsonify({"message": log_warning_return_str(
            f'Voice directory {tts_dir} not found at {output_path}')}), 404

    zipf = zipfile.ZipFile(tts_zip_path, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(tts_dir):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, output_path)
            zipf.write(file_path, relative_path)

    zipf.close()
    return send_from_directory(output_path, tts_zip_fn, as_attachment=True)


@app.route('/upload_reference_audio', methods=['POST'])
@pytvzhen_api_request_counter
def upload_reference_audio():
    """上传参考音频文件用于 XTTS v2 语音克隆"""
    output_path = app.config['OUTPUT_PATH']
    reference_audio_dir = os.path.join(output_path, "reference_audio")
    
    if not os.path.exists(reference_audio_dir):
        os.makedirs(reference_audio_dir)
    
    if 'file' not in request.files:
        return jsonify({"message": log_warning_return_str("No file provided")}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": log_warning_return_str("No file selected")}), 400
    
    if file:
        filename = secure_filename(file.filename)
        # 确保文件名唯一
        base_name, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(os.path.join(reference_audio_dir, filename)):
            filename = f"{base_name}_{counter}{ext}"
            counter += 1
        
        file_path = os.path.join(reference_audio_dir, filename)
        file.save(file_path)
        
        return jsonify({
            "message": log_info_return_str(f"Reference audio uploaded successfully: {filename}"),
            "file_path": file_path,
            "filename": filename
        }), 200


@app.route('/video_preview', methods=['POST'])
@pytvzhen_api_request_counter
@require_video_id_from_post_request
def video_preview(video_id):
    output_path = app.config['OUTPUT_PATH']

    data = request.get_json()
    
    # 使用新的视频文件路径
    video_hd_path = os.path.join(output_path, f"{video_id}_hd.mp4")  # 新的高清视频
    video_legacy_path = os.path.join(output_path, f"{video_id}.mp4")  # 兼容旧的标清视频
    video_fhd_legacy_path = os.path.join(output_path, f"{video_id}_fhd.mp4")  # 兼容旧的高清视频
    
    # 获取音频类型参数，默认为 'translated'
    audio_type = data.get('audio_type', 'translated')  # 'original', 'translated'
    
    # 获取硬编码字幕参数，默认为False
    hardcode_subtitles = data.get('hardcode_subtitles', False)
    
    # 获取字幕类型参数
    subtitle_type = data.get('subtitle_type', 'translated')  # 'original', 'translated', 'bilingual'
    
    # 获取字幕样式配置
    subtitle_style_config = data.get('subtitle_style', {})
    
    # 获取强制重新渲染参数，默认为False
    force_render = data.get('force_render', False)
    
    # 根据字幕类型获取字幕文件路径
    if hardcode_subtitles:
        srt_path = get_subtitle_file_path(output_path, video_id, subtitle_type)
        
        # 检查字幕文件是否存在
        if not os.path.exists(srt_path):
            return jsonify({"message": log_error_return_str(
                f"Subtitle file not found for hardcoding: {srt_path}. Please generate subtitle first.")}), 404
    else:
        # 不硬编码时使用默认字幕文件
        srt_path = os.path.join(output_path, f"{video_id}_zh_merged.srt")

    # 检查视频
    if (not os.path.exists(video_hd_path)) and (not os.path.exists(video_legacy_path)) and (not os.path.exists(video_fhd_legacy_path)):
        return jsonify({"message": log_warning_return_str(
            f"No video found. Expected one of: {video_id}_hd.mp4, {video_id}.mp4, or {video_id}_fhd.mp4")}), 404

    # 选择最佳分辨率的视频（优先使用新的高清视频）
    if os.path.exists(video_hd_path):
        video_source_path = video_hd_path
        app.logger.info(f"Using new HD video: {video_hd_path}")
    elif os.path.exists(video_fhd_legacy_path):
        video_source_path = video_fhd_legacy_path
        app.logger.info(f"Using legacy FHD video: {video_fhd_legacy_path}")
    else:
        video_source_path = video_legacy_path
        app.logger.info(f"Using legacy SD video: {video_legacy_path}")

    # 根据音频类型选择音频文件
    if audio_type == 'translated':
        # 使用翻译后的音频（需要人声和背景音乐）
        voice_connect_path = os.path.join(output_path, video_id + "_zh.wav")
        audio_bg_path = os.path.join(output_path, f'{video_id}_bg.wav')
        
        # 检查翻译后的音频文件是否存在
        if (not os.path.exists(voice_connect_path)) or (not os.path.exists(audio_bg_path)):
            return jsonify({"message": log_warning_return_str(
                f'Chinese Voice {video_id + "_zh.wav"} or background music not found at {output_path}')}), 404
    else:
        # 使用原始音频
        voice_connect_path = os.path.join(output_path, f"{video_id}_audio.wav")
        audio_bg_path = None
        
        # 检查原始音频文件是否存在
        if not os.path.exists(voice_connect_path):
            return jsonify({"message": log_warning_return_str(
                f'Original audio {video_id}_audio.wav not found at {output_path}')}), 404

    blocking = data.get('blocking', False)
    tasks = []

    # 创建字幕样式对象
    subtitle_style = None
    subtitle_style_dict = None
    if hardcode_subtitles and subtitle_style_config:
        try:
            from src.service.video_synthesis.video_preview import SubtitleStyle
            
            # 获取双语字幕配置
            bilingual_config = subtitle_style_config.get('bilingual', None)
            app.logger.info(f"双语字幕配置: {bilingual_config}")
            app.logger.info(f"双语字幕配置类型: {type(bilingual_config)}")
            if bilingual_config:
                app.logger.info(f"双语字幕配置内容: {bilingual_config}")
            
            subtitle_style = SubtitleStyle(
                font_name=subtitle_style_config.get('font_name', 'Arial'),
                font_size=subtitle_style_config.get('font_size', 24),
                primary_color=subtitle_style_config.get('primary_color', '&Hffffff'),
                outline_color=subtitle_style_config.get('outline_color', '&H000000'),
                back_color=subtitle_style_config.get('back_color', '&H000000'),
                outline_width=subtitle_style_config.get('outline_width', 2),
                shadow_depth=subtitle_style_config.get('shadow_depth', 1),
                alignment=subtitle_style_config.get('alignment', 2),
                margin_v=subtitle_style_config.get('margin_v', 30),
                margin_l=subtitle_style_config.get('margin_l', 10),
                margin_r=subtitle_style_config.get('margin_r', 10),
                auto_scale=subtitle_style_config.get('auto_scale', True),
                min_font_size=subtitle_style_config.get('min_font_size', 16),
                max_font_size=subtitle_style_config.get('max_font_size', 32),
                bilingual_config=bilingual_config
            )
            # 转换为字典格式用于Celery序列化
            subtitle_style_dict = {
                'font_name': subtitle_style.font_name,
                'font_size': subtitle_style.font_size,
                'primary_color': subtitle_style.primary_color,
                'outline_color': subtitle_style.outline_color,
                'back_color': subtitle_style.back_color,
                'outline_width': subtitle_style.outline_width,
                'shadow_depth': subtitle_style.shadow_depth,
                'alignment': subtitle_style.alignment,
                'margin_v': subtitle_style.margin_v,
                'margin_l': subtitle_style.margin_l,
                'margin_r': subtitle_style.margin_r,
                'auto_scale': subtitle_style.auto_scale,
                'min_font_size': subtitle_style.min_font_size,
                'max_font_size': subtitle_style.max_font_size,
                'bilingual_config': subtitle_style.bilingual_config
            }
            app.logger.info(f"字幕样式配置: {subtitle_style_config}")
            app.logger.info(f"subtitle_style_dict: {subtitle_style_dict}")
        except Exception as e:
            app.logger.warning(f"字幕样式配置失败: {e}")

    # 生成视频文件名（考虑音频类型、硬编码字幕配置）
    video_filename = get_video_filename_with_audio_and_subtitle_config(
        video_id, audio_type, hardcode_subtitles, subtitle_type, subtitle_style_config
    )
    video_path = os.path.join(output_path, video_filename)
    
    # 检查是否已存在相同配置的视频
    if os.path.exists(video_path) and not force_render:
        app.logger.info(f"视频已存在: {video_filename}")
        return jsonify({
            "message": log_info_return_str(f"Video already exists: {video_filename}"),
            "task_id": None,
            "filename": video_filename,
            "download_url": f"/video_preview/{video_filename}"
        }), 200
    
    # 如果启用硬编码字幕，检查字幕文件是否存在
    if hardcode_subtitles and not os.path.exists(srt_path):
        return jsonify({"message": log_warning_return_str(
            f'Subtitle file not found for hardcoding: {srt_path}')}), 404
    
    # 如果是双语字幕且有双语配置，创建ASS字幕文件
    app.logger.info(f"检查双语字幕条件: hardcode_subtitles={hardcode_subtitles}, subtitle_type={subtitle_type}")
    app.logger.info(f"subtitle_style_dict存在: {subtitle_style_dict is not None}")
    if subtitle_style_dict:
        app.logger.info(f"bilingual_config存在: {subtitle_style_dict.get('bilingual_config') is not None}")
        app.logger.info(f"bilingual_config内容: {subtitle_style_dict.get('bilingual_config')}")
    
    if hardcode_subtitles and subtitle_type == 'bilingual' and subtitle_style_dict and subtitle_style_dict.get('bilingual_config'):
        try:
            from src.service.video_synthesis.video_preview import create_bilingual_ass_subtitle, SubtitleStyle
            
            # 重新创建SubtitleStyle对象
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
                bilingual_config=subtitle_style_dict.get('bilingual_config')
            )
            
            # 创建ASS字幕文件
            ass_srt_path = create_bilingual_ass_subtitle(srt_path, subtitle_style)
            if ass_srt_path and os.path.exists(ass_srt_path):
                app.logger.info(f"✅ 双语ASS字幕文件已创建: {ass_srt_path}")
                srt_path = ass_srt_path  # 使用ASS字幕文件路径
            else:
                app.logger.error(f"❌ 双语ASS字幕创建失败，无法继续渲染")
                return jsonify({"message": log_error_return_str(
                    f'Failed to create bilingual ASS subtitle file for: {srt_path}')}), 500
        except Exception as e:
            app.logger.error(f"❌ 创建双语ASS字幕时出错: {e}")
            return jsonify({"message": log_error_return_str(
                f'Error creating bilingual ASS subtitle: {str(e)}')}), 500
    
    # 最终检查：确保字幕文件存在且可读
    if hardcode_subtitles:
        if not os.path.exists(srt_path):
            return jsonify({"message": log_error_return_str(
                f'Subtitle file not found: {srt_path}')}), 404
        
        # 检查文件大小，确保不是空文件
        if os.path.getsize(srt_path) == 0:
            return jsonify({"message": log_error_return_str(
                f'Subtitle file is empty: {srt_path}')}), 400
        
        app.logger.info(f"✅ 字幕文件检查通过: {srt_path} (大小: {os.path.getsize(srt_path)} 字节)")
    
    # 生成视频任务
    task = video_preview_task.delay(video_source_path, voice_connect_path, audio_bg_path, video_path, srt_path, hardcode_subtitles, subtitle_style_dict, subtitle_type, False)
    tasks.append(('video', task))

    # 如果是阻塞模式，等待所有任务完成
    if blocking:
        for task_type, task in tasks:
            try:
                task.get()  # 等待任务完成
            except Exception as e:
                return jsonify({"message": log_error_return_str(
                    f"Failed to render video: {str(e)}")}), 500
        
        return jsonify({
            "message": log_info_return_str(f"Successfully rendered video: {video_filename}"),
            "task_id": None,
            "filename": video_filename,
            "download_url": f"/video_preview/{video_filename}"
        }), 200

    # 返回任务信息
    task_id = tasks[0][1].id if tasks else None
    queue_length = get_queue_length('video_preview')
    
    return jsonify({
        "message": log_info_return_str(f"Submitted video rendering task"),
        "task_id": task_id,
        "filename": video_filename,
        "download_url": f"/video_preview/{video_filename}",
        'queue_length': queue_length
    }), 202




@app.route('/video_preview_status/<task_id>', methods=['GET'])
@pytvzhen_api_request_counter
def video_preview_status(task_id):
    task = video_preview_task.AsyncResult(task_id)
    queue_length = get_queue_length('video_preview')
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': f'Video preview task {task_id} pending...',
            'queue_length': queue_length
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': str(task.info),
            'queue_length': queue_length
        }
    else:
        response = {
            'state': task.state,
            'status': str(task.info),
            'result': str(task.result),
            'queue_length': queue_length
        }
    return jsonify(response)


@app.route('/video_preview/<filename>', methods=['GET'])
@pytvzhen_api_request_counter
def video_preview_serve(filename):
    output_path = app.config['OUTPUT_PATH']
    
    file_path = os.path.join(output_path, filename)
    if os.path.exists(file_path):
        return send_from_directory(output_path, filename, as_attachment=True)

    return jsonify({"message": log_warning_return_str(
        f'Video file not found: {filename}')}), 404





@app.route('/subtitles/<video_id>', methods=['GET'])
@pytvzhen_api_request_counter
def download_subtitles(video_id):
    """Download Chinese translated SRT file for editing"""
    output_path = app.config['OUTPUT_PATH']

    # Look for the Chinese merged SRT file
    srt_fn = f'{video_id}_zh_merged.srt'
    srt_path = os.path.join(output_path, srt_fn)

    if not os.path.exists(srt_path):
        return jsonify({"message": log_warning_return_str(
            f'Chinese SRT {srt_fn} not found at {output_path}')}), 404

    try:
        with open(srt_path, 'r', encoding='utf-8') as file:
            content = file.read()

        return content, 200, {
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Disposition': f'attachment; filename="{srt_fn}"'
        }
    except Exception as e:
        return jsonify({"message": log_warning_return_str(
            f"Failed to read subtitle file: {str(e)}")}), 500


@app.route('/subtitles/<video_id>', methods=['POST'])
@pytvzhen_api_request_counter
def upload_subtitles(video_id):
    """Upload modified Chinese SRT file"""
    output_path = app.config['OUTPUT_PATH']

    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"message": log_warning_return_str(
            "No subtitle content provided")}), 400

    content = data['content']

    # Validate SRT content (basic check)
    if not content.strip():
        return jsonify({"message": log_warning_return_str(
            "Subtitle content cannot be empty")}), 400

    # Save to the Chinese merged SRT file
    srt_fn = f'{video_id}_zh_merged.srt'
    srt_path = os.path.join(output_path, srt_fn)

    try:
        # Create backup of original file
        if os.path.exists(srt_path):
            backup_path = srt_path + '.backup'
            shutil.copy2(srt_path, backup_path)

        # Write the new content
        with open(srt_path, 'w', encoding='utf-8') as file:
            file.write(content)

        return jsonify({
            "message": log_info_return_str(f"Subtitle file {srt_fn} updated successfully"),
            "video_id": video_id
        }), 200

    except Exception as e:
        return jsonify({"message": log_warning_return_str(
            f"Failed to save subtitle file: {str(e)}")}), 500


def get_video_filename_with_audio_and_subtitle_config(video_id, audio_type, hardcode_subtitles=False, subtitle_type=None, subtitle_style=None):
    """
    根据音频类型和字幕配置生成视频文件名
    
    Args:
        video_id: 视频ID
        audio_type: 音频类型 ('original', 'translated')
        hardcode_subtitles: 是否硬编码字幕
        subtitle_type: 字幕类型
        subtitle_style: 字幕样式配置
    
    Returns:
        str: 视频文件名
    """
    # 基础文件名
    if audio_type == 'original':
        base_name = f"{video_id}_original"
    else:
        base_name = f"{video_id}_translated"
    
    # 如果硬编码字幕，添加标识
    if hardcode_subtitles:
        base_name += "_hardcoded"
    
    return f"{base_name}.mp4"


def get_video_filename_with_subtitle_config(video_id, video_type, hardcode_subtitles=False, subtitle_type=None, subtitle_style=None):
    """
    根据字幕配置生成视频文件名
    
    Args:
        video_id: 视频ID
        video_type: 视频类型 ('preview', 'original')
        hardcode_subtitles: 是否硬编码字幕
        subtitle_type: 字幕类型
        subtitle_style: 字幕样式配置
    
    Returns:
        str: 视频文件名
    """
    if not hardcode_subtitles:
        # 不硬编码字幕时使用简单文件名
        return f"{video_id}_{video_type}.mp4"
    else:
        # 硬编码字幕时使用简单标识
        return f"{video_id}_{video_type}_hardcoded.mp4"


def get_download_url(video_id, video_type, hardcode_subtitles=False, subtitle_type=None, subtitle_style=None, base_url=None):
    """
    根据视频配置生成下载URL
    
    Args:
        video_id: 视频ID
        video_type: 视频类型 ('preview', 'original')
        hardcode_subtitles: 是否硬编码字幕
        subtitle_type: 字幕类型
        subtitle_style: 字幕样式配置 (dict)
        base_url: 基础URL，如果为None则使用相对路径
    
    Returns:
        str: 下载URL
    """
    # 构建基础URL
    if base_url:
        url = f"{base_url}/video_{video_type}/{video_id}"
    else:
        url = f"/video_{video_type}/{video_id}"
    
    # 如果启用了硬编码字幕，添加参数
    if hardcode_subtitles:
        url += '?hardcode_subtitles=true'
    
    return url


def _merge_bilingual_srt(en_srt_path, zh_srt_path, output_path):
    """
    合并英文和中文字幕为双语字幕
    
    Args:
        en_srt_path: 英文字幕文件路径
        zh_srt_path: 中文字幕文件路径
        output_path: 输出双语字幕文件路径
        
    Returns:
        bool: 是否成功
    """
    try:
        import srt
        
        # 读取英文字幕
        with open(en_srt_path, 'r', encoding='utf-8') as f:
            en_content = f.read()
        en_subs = list(srt.parse(en_content))
        
        # 读取中文字幕
        with open(zh_srt_path, 'r', encoding='utf-8') as f:
            zh_content = f.read()
        zh_subs = list(srt.parse(zh_content))
        
        # 检查字幕数量是否匹配
        if len(en_subs) != len(zh_subs):
            app.logger.warning(f"Subtitle count mismatch: English={len(en_subs)}, Chinese={len(zh_subs)}")
            # 使用较少的字幕数量
            min_count = min(len(en_subs), len(zh_subs))
            en_subs = en_subs[:min_count]
            zh_subs = zh_subs[:min_count]
        
        # 合并字幕
        bilingual_subs = []
        for i, (en_sub, zh_sub) in enumerate(zip(en_subs, zh_subs)):
            # 使用英文字幕的时间轴，中文在上，英文在下
            bilingual_sub = srt.Subtitle(
                index=i + 1,
                start=en_sub.start,
                end=en_sub.end,
                content=f"{zh_sub.content}\n{en_sub.content}"
            )
            bilingual_subs.append(bilingual_sub)
        
        # 写入双语字幕文件
        bilingual_content = srt.compose(bilingual_subs)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(bilingual_content)
        
        app.logger.info(f"Generated bilingual SRT with {len(bilingual_subs)} entries")
        return True
        
    except Exception as e:
        app.logger.error(f"Failed to merge bilingual SRT: {e}")
        return False


@app.route('/subtitle_hardcoded/<video_id>', methods=['GET'])
@pytvzhen_api_request_counter
def subtitle_hardcoded_serve(video_id):
    """下载硬编码字幕文件"""
    output_path = app.config['OUTPUT_PATH']
    
    # 获取查询参数
    subtitle_type = request.args.get('type', 'translated')  # 'original', 'translated', 'bilingual'
    
    # 根据字幕类型获取字幕文件路径
    if subtitle_type == 'original':
        subtitle_filename = f'{video_id}_en_merged.srt'
    elif subtitle_type == 'translated':
        subtitle_filename = f'{video_id}_zh_merged.srt'
    elif subtitle_type == 'bilingual':
        subtitle_filename = f'{video_id}_bilingual.srt'
    else:
        return jsonify({"message": log_warning_return_str(
            f'Invalid subtitle type: {subtitle_type}')}), 400
    
    subtitle_path = os.path.join(output_path, subtitle_filename)
    
    if os.path.exists(subtitle_path):
        return send_from_directory(output_path, subtitle_filename, as_attachment=True)
    
    return jsonify({"message": log_warning_return_str(
        f'Hardcoded subtitle {subtitle_filename} not found at {subtitle_path}')}), 404


@app.route('/subtitle_hardcoded_styled/<video_id>', methods=['GET'])
@pytvzhen_api_request_counter
def subtitle_hardcoded_styled_serve(video_id):
    """下载带样式的硬编码字幕文件"""
    output_path = app.config['OUTPUT_PATH']
    
    # 获取查询参数
    subtitle_type = request.args.get('type', 'translated')  # 'original', 'translated', 'bilingual'
    font_name = request.args.get('font_name', 'Arial')
    font_size = request.args.get('font_size', '24')
    auto_scale = request.args.get('auto_scale', 'false')
    
    # 根据字幕类型获取字幕文件路径
    if subtitle_type == 'original':
        base_subtitle_filename = f'{video_id}_en_merged.srt'
    elif subtitle_type == 'translated':
        base_subtitle_filename = f'{video_id}_zh_merged.srt'
    elif subtitle_type == 'bilingual':
        base_subtitle_filename = f'{video_id}_bilingual.srt'
    else:
        return jsonify({"message": log_warning_return_str(
            f'Invalid subtitle type: {subtitle_type}')}), 400
    
    base_subtitle_path = os.path.join(output_path, base_subtitle_filename)
    
    if not os.path.exists(base_subtitle_path):
        return jsonify({"message": log_warning_return_str(
            f'Base subtitle {base_subtitle_filename} not found at {base_subtitle_path}')}), 404
    
    # 生成带样式的字幕文件名
    styled_filename = f'{video_id}_{subtitle_type}_styled.srt'
    styled_path = os.path.join(output_path, styled_filename)
    
    # 如果带样式的文件不存在，尝试生成
    if not os.path.exists(styled_path):
        try:
            from src.service.video_synthesis.video_preview import SubtitleStyle, create_adaptive_subtitle_srt
            
            # 创建字幕样式配置
            style_config = SubtitleStyle(
                font_name=font_name,
                font_size=int(font_size),
                auto_scale=auto_scale.lower() == 'true'
            )
            
            # 生成带样式的字幕文件
            styled_path = create_adaptive_subtitle_srt(base_subtitle_path, style_config)
            
            if not os.path.exists(styled_path):
                return jsonify({"message": log_warning_return_str(
                    f'Failed to generate styled subtitle file')}), 500
                
        except Exception as e:
            app.logger.error(f"生成带样式字幕文件失败: {e}")
            return jsonify({"message": log_error_return_str(
                f'Failed to generate styled subtitle: {str(e)}')}), 500
    
    return send_from_directory(output_path, os.path.basename(styled_path), as_attachment=True)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10310)
