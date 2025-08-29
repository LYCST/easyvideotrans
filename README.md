# EasyVideoTrans 🎬🔊🌐

一个强大的视频翻译和语音合成工具，支持多种 TTS 引擎和翻译服务。

## ✨ 特性

- 🎥 **视频下载**: 支持 YouTube 视频下载和处理
- 🗣️ **多引擎 TTS**: Edge TTS、OpenAI TTS、XTTS v2、CosyVoice2
- 🌍 **多语言翻译**: Google、DeepL、GPT (Ollama)
- 🎵 **音频处理**: 人声分离、背景音乐移除
- 📝 **字幕处理**: SRT 格式支持、自动时间轴同步
- 🚀 **高性能**: GPU 加速、异步处理、缓存机制
- 📊 **监控**: Prometheus 指标、实时状态监控

## 🏗️ 架构

```
EasyVideoTrans/
├── app.py                 # 主 Flask 应用
├── inference.py           # GPU 工作负载服务
├── src/
│   ├── service/
│   │   ├── tts/          # TTS 服务 (Edge, OpenAI, XTTS v2, CosyVoice2)
│   │   └── translation/  # 翻译服务 (Google, DeepL, GPT)
│   └── task_manager/     # Celery 任务管理
├── workloads/             # GPU 工作负载
└── configs/              # 配置文件
```

## 🚀 快速开始

### 环境要求

- Python 3.9+ (推荐 3.11)
- CUDA 11.8+ (GPU 加速)
- FFmpeg
- RabbitMQ

### 安装

1. **克隆仓库**
```bash
git clone https://github.com/your-username/easyvideotrans.git
cd easyvideotrans
```

2. **创建虚拟环境**
```bash
conda create -n easy-video python=3.11
conda activate easy-video
```

3. **安装依赖**
```bash
pip install -r requirements.txt
pip install -r workloads/requirements.txt
```

4. **安装 FFmpeg**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg

# macOS
brew install ffmpeg
```

5. **启动 RabbitMQ**
```bash
# 使用 Docker
docker run -d --name rabbitmq -p 5672:5672 -p 10311:15672 rabbitmq:3-management

# 或使用系统包管理器
sudo systemctl start rabbitmq-server
```

### 配置

1. **复制配置文件**
```bash
cp configs/easyvideotrans.json.example configs/easyvideotrans.json
cp configs/celery.json.example configs/celery.json
```

2. **设置环境变量**
```bash
export OPENAI_API_KEY="your-openai-api-key"
export DEEPL_API_KEY="your-deepl-api-key"
```

3. **修改配置**
```json
{
  "OUTPUT_PATH": "./workloads/static/outputs",
  "HOST": "0.0.0.0",
  "PORT": 10310
}
```

### 启动服务

1. **启动主应用**
```bash
python app.py
```

2. **启动 GPU 工作负载服务**
```bash
python workloads/inference.py
```

3. **启动 Celery 工作进程**
```bash
celery -A src.task_manager.celery_tasks.celery_app worker --concurrency 1 -Q video_preview --loglevel=info
```

4. **访问 Web 界面**
```
http://localhost:10310
```

## 📊 API 接口文档

### 基础信息
- **基础URL**: `http://localhost:10310`
- **内容类型**: `application/json`
- **响应格式**: JSON

### 1. 视频上传和下载

#### 1.1 上传视频文件
```bash
curl -X POST http://localhost:10310/video_upload \
  -F "file=@/path/to/your/video.mp4"
```
**参数说明**:
- `file`: 视频文件 (支持 .mp4 格式)

**响应示例**:
```json
{
  "message": "Video video.mp4 uploaded as abc123_video.mp4",
  "video_id": "abc123"
}
```

#### 1.2 下载 YouTube 视频
```bash
curl -X POST http://localhost:10310/yt_download \
  -H "Content-Type: application/json" \
  -d '{"video_id": "Am54LhN2NLk"}'
```
**参数说明**:
- `video_id`: YouTube 视频 ID

**响应示例**:
```json
{
  "message": "YouTube video downloaded successfully",
  "video_id": "Am54LhN2NLk"
}
```

#### 1.3 获取 YouTube 视频缩略图
```bash
curl -X POST http://localhost:10310/yt_thumbnail \
  -H "Content-Type: application/json" \
  -d '{"video_id": "Am54LhN2NLk"}'
```

#### 1.4 下载视频文件
```bash
curl -X GET http://localhost:10310/yt/Am54LhN2NLk
```

### 2. 音频处理

#### 2.1 提取音频
```bash
curl -X POST http://localhost:10310/extra_audio \
  -H "Content-Type: application/json" \
  -d '{"video_id": "Am54LhN2NLk"}'
```

#### 2.2 下载音频文件
```bash
curl -X GET http://localhost:10310/audio/Am54LhN2NLk
```

#### 2.3 移除音频背景音乐
```bash
curl -X POST http://localhost:10310/remove_audio_bg \
  -H "Content-Type: application/json" \
  -d '{"video_id": "Am54LhN2NLk"}'
```

#### 2.4 下载人声音频
```bash
curl -X GET http://localhost:10310/audio_no_bg/Am54LhN2NLk
```

#### 2.5 下载背景音乐
```bash
curl -X GET http://localhost:10310/audio_bg/Am54LhN2NLk
```

### 3. 语音识别和字幕

#### 3.1 语音识别生成字幕
```bash
curl -X POST http://localhost:10310/transcribe \
  -H "Content-Type: application/json" \
  -d '{"video_id": "Am54LhN2NLk"}'
```

#### 3.2 下载英文原始字幕
```bash
curl -X GET http://localhost:10310/srt_en/Am54LhN2NLk
```

#### 3.3 下载英文合并字幕
```bash
curl -X GET http://localhost:10310/srt_en_merged/Am54LhN2NLk
```

### 4. 翻译服务

#### 4.1 翻译字幕为中文
```bash
curl -X POST http://localhost:10310/translate_to_zh \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "Am54LhN2NLk",
    "source_lang": "en",
    "translate_vendor": "google",
    "translate_key": ""
  }'
```
**参数说明**:
- `video_id`: 视频 ID
- `source_lang`: 源语言 (默认: "en")
- `translate_vendor`: 翻译服务商 ("google", "deepl", "gpt-3.5-turbo-0125", "gpt-4", "gpt-4-turbo", "gpt-local")
- `translate_key`: API 密钥 (DeepL/ChatGPT 需要)
- `base_url`: 本地部署 API 地址 (仅 gpt-local 需要)
- `model_name`: 本地部署模型名称 (仅 gpt-local 需要)

#### 4.2 生成双语字幕
```bash
curl -X POST http://localhost:10310/generate_bilingual_srt \
  -H "Content-Type: application/json" \
  -d '{"video_id": "Am54LhN2NLk"}'
```

#### 4.3 下载中文字幕
```bash
curl -X GET http://localhost:10310/srt_zh_merged/Am54LhN2NLk
```

#### 4.4 下载双语字幕
```bash
curl -X GET http://localhost:10310/srt_bilingual/Am54LhN2NLk
```

#### 4.5 上传修改后的中文字幕
```bash
curl -X POST http://localhost:10310/translated_zh_upload \
  -F "video_id=Am54LhN2NLk" \
  -F "file=@/path/to/modified_subtitle.srt"
```

### 5. 语音合成 (TTS)

#### 5.1 生成语音
```bash
curl -X POST http://localhost:10310/tts \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "Am54LhN2NLk",
    "tts_vendor": "edge",
    "tts_character": "zh-CN-XiaoyiNeural"
  }'
```
**参数说明**:
- `video_id`: 视频 ID
- `tts_vendor`: TTS 引擎 ("edge", "openai", "xtts_v2", "cosyvoice2", "fallback")
- `tts_character`: 语音角色 (Edge TTS)
- `voice`: 语音类型 (OpenAI TTS: "alloy", "echo", "fable", "onyx", "nova", "shimmer")
- `model`: 模型类型 (OpenAI TTS: "tts-1", "tts-1-hd")
- `instructions`: 语音指令 (OpenAI TTS)
- `language`: 目标语言 (XTTS v2)
- `model_name`: 模型名称 (XTTS v2)
- `audio_source`: 参考音频来源 ("upload", "video_voice")
- `reference_audio_path`: 参考音频路径
- `speaker_name`: 说话人名称 (CosyVoice2)
- `mode`: 生成模式 (CosyVoice2: "zero_shot", "cross_lingual", "instruct")
- `instruction`: 指令 (CosyVoice2)
- `model_path`: 模型路径 (CosyVoice2)
- `fp16`: 使用 FP16 精度 (CosyVoice2)

#### 5.2 下载生成的语音
```bash
curl -X GET http://localhost:10310/tts/Am54LhN2NLk
```

#### 5.3 上传参考音频
```bash
curl -X POST http://localhost:10310/upload_reference_audio \
  -F "file=@/path/to/reference_audio.wav"
```

### 6. 语音连接

#### 6.1 连接语音和视频
```bash
curl -X POST http://localhost:10310/voice_connect \
  -H "Content-Type: application/json" \
  -d '{"video_id": "Am54LhN2NLk"}'
```

#### 6.2 下载连接的语音
```bash
curl -X GET http://localhost:10310/voice_connect/Am54LhN2NLk
```

#### 6.3 下载语音连接日志
```bash
curl -X GET http://localhost:10310/voice_connect_log/Am54LhN2NLk
```

### 7. 视频合成

#### 7.1 生成视频
```bash
# 基础视频生成
curl -X POST http://localhost:10310/video_preview \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "Am54LhN2NLk",
    "audio_type": "translated",
    "force_render": false,
    "hardcode_subtitles": false
  }'

# 硬编码双语字幕视频生成
curl -X POST http://localhost:10310/video_preview \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "Am54LhN2NLk",
    "audio_type": "translated",
    "hardcode_subtitles": true,
    "subtitle_type": "bilingual",
    "subtitle_style": {
      "font_name": "Arial",
      "font_size": 20,
      "primary_color": "&Hffffff",
      "outline_color": "&H000000",
      "back_color": "&H000000",
      "outline_width": 2,
      "shadow_depth": 1,
      "alignment": 2,
      "margin_v": 30,
      "auto_scale": true,
      "min_font_size": 14,
      "max_font_size": 28,
      "bilingual": {
        "secondary_font_name": "SimHei",
        "secondary_font_size": 24,
        "secondary_color": "&Hcccccc",
        "vertical_spacing": 5
      }
    }
  }'
```
**参数说明**:
- `video_id`: 视频 ID
- `audio_type`: 音频类型 ("original", "translated") - 使用原始音频还是翻译后的音频
- `force_render`: 强制重新渲染 (默认: false)
- `hardcode_subtitles`: 硬编码字幕 (默认: false)
- `subtitle_type`: 字幕类型 ("translated", "original", "bilingual")
- `subtitle_style`: 字幕样式配置对象
  - `font_name`: 字体名称
  - `font_size`: 字体大小
  - `primary_color`: 文字颜色 (ASS 格式)
  - `outline_color`: 描边颜色 (ASS 格式)
  - `back_color`: 背景颜色 (ASS 格式)
  - `outline_width`: 描边宽度
  - `shadow_depth`: 阴影深度
  - `alignment`: 对齐方式 (1-8)
  - `margin_v`: 垂直边距
  - `auto_scale`: 自适应字体大小
  - `min_font_size`: 最小字体大小
  - `max_font_size`: 最大字体大小
  - `bilingual`: 双语字幕配置 (可选)
    - `secondary_font_name`: 副字体名称
    - `secondary_font_size`: 副字体大小
    - `secondary_color`: 副字体颜色 (ASS 格式)
    - `vertical_spacing`: 中英文字幕间距 (默认: 5)

**响应示例**:
```json
{
  "message": "Submitted video rendering task",
  "task_id": "abc123-def456-ghi789",
  "filename": "Am54LhN2NLk_translated.mp4",
  "download_url": "/video_preview/Am54LhN2NLk_translated.mp4",
  "queue_length": 2
}
```

#### 7.2 下载视频
```bash
curl -X GET http://localhost:10310/video_preview/Am54LhN2NLk_translated.mp4
```

#### 7.3 查询任务状态
```bash
curl -X GET http://localhost:10310/video_preview_status/abc123-def456-ghi789
```

### 8. 字幕管理

#### 8.1 下载字幕文件
```bash
# 下载中文字幕
curl -X GET http://localhost:10310/subtitles/Am54LhN2NLk

# 下载双语字幕
curl -X GET http://localhost:10310/srt_bilingual/Am54LhN2NLk
```

#### 8.2 上传修改后的字幕
```bash
curl -X POST http://localhost:10310/subtitles/Am54LhN2NLk \
  -H "Content-Type: application/json" \
  -d '{
    "content": "1\n00:00:01,000 --> 00:00:04,000\n这是修改后的字幕内容\n\n2\n00:00:04,000 --> 00:00:07,000\n第二行字幕内容"
  }'
```

#### 8.3 下载硬编码字幕视频
```bash
curl -X GET "http://localhost:10310/subtitle_hardcoded/Am54LhN2NLk?subtitle_type=translated&font_name=Arial&font_size=24&auto_scale=true"
```

#### 8.4 下载带样式的硬编码字幕视频
```bash
curl -X GET "http://localhost:10310/subtitle_hardcoded_styled/Am54LhN2NLk?subtitle_type=translated&font_name=Arial&font_size=24&auto_scale=true"
```

### 9. 任务状态查询

#### 9.1 查询视频预览任务状态
```bash
curl -X GET http://localhost:10310/video_preview_status/task_id_here
```

## 🎯 使用方法

### 1. 视频翻译流程

1. **下载视频**: 输入 YouTube 视频 ID（支持文件有效性检查）
2. **提取音频**: 自动分离人声和背景音乐
3. **语音识别**: 使用 Whisper 生成字幕
4. **翻译字幕**: 选择翻译服务 (Google/DeepL/GPT)
5. **语音合成**: 选择 TTS 引擎生成语音
6. **视频合成**: 合并音频和视频

### 2. TTS 引擎配置

#### Edge TTS (微软)
- 支持多种语音角色
- 免费使用，无需 API Key

#### OpenAI TTS
- 高质量语音合成
- 支持多种语音类型
- 需要 OpenAI API Key

#### XTTS v2 (Coqui TTS)
- 语音克隆功能
- 支持多语言
- 需要参考音频

#### CosyVoice2 (腾讯)
- 零样本语音克隆
- 跨语种语音生成
- 支持指令控制

### 3. 翻译服务

#### Google Translate
- 免费使用
- 支持 100+ 语言

#### DeepL
- 高质量翻译
- 需要 API Key

#### GPT (Ollama)
- 本地部署
- 支持自定义模型

### 4. 视频合成

#### 硬编码字幕功能
- **默认行为**: 不硬编码字幕，使用 MoviePy 合成视频
- **启用硬编码**: 将中文字幕直接嵌入视频中，使用 FFmpeg 处理
- **参数**: 
  - `hardcode_subtitles` (布尔值，默认 False)
  - `max_chars_per_line` (整数，默认 30) - 每行最大字符数
- **自动换行**: 支持字幕自动换行，在标点符号处智能分割
- **优势**: 
  - 字幕永久嵌入，无法关闭
  - 兼容性更好，所有播放器都支持
  - 自动换行确保字幕可读性
  - 适合最终成品视频

## 🔧 高级配置

### GPU 配置

```python
# 在 workloads/inference.py 中配置
CUDA_VISIBLE_DEVICES = "0"  # 使用第一块 GPU
```

### 缓存配置

```python
# 翻译缓存
CACHE_DIR = "./translation_cache"
CACHE_EXPIRE = 86400  # 24小时
```

### 监控配置

```python
# Prometheus 指标
METRICS_PORT = 8081
ENABLE_METRICS = True
```

## 🐳 Docker 部署

### 使用 Docker Compose

```bash
docker-compose up -d
```

### 构建镜像

```bash
docker build -t easyvideotrans .
docker run -p 10310:10310 easyvideotrans
```

## 🧪 测试

```bash
# 运行测试
pytest tests/

# 代码质量检查
flake8 src/
black --check src/
```

## 📈 性能优化

- **GPU 加速**: 使用 CUDA 加速 TTS 和音频处理
- **异步处理**: Celery 队列处理耗时任务
- **缓存机制**: 翻译结果缓存，避免重复请求
- **文件验证**: 自动检测损坏的视频文件并重新下载
- **并发控制**: 限制并发数量，避免资源过载

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行代码格式化
black src/
isort src/

# 运行测试
pytest tests/ --cov=src/
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Coqui TTS](https://github.com/coqui-ai/TTS) - XTTS v2 语音合成
- [CosyVoice2](https://github.com/TencentGameMate/chinese-xtts-v2) - 中文语音克隆
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper) - 语音识别
- [MoviePy](https://github.com/Zulko/moviepy) - 视频处理

## 📞 支持

- 📧 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/easyvideotrans/issues)
- 📖 文档: [Wiki](https://github.com/your-username/easyvideotrans/wiki)

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！

