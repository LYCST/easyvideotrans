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

## 🎯 使用方法

### 1. 视频翻译流程

1. **下载视频**: 输入 YouTube 视频 ID
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

## 📊 API 接口

### 主要端点

- `POST /yt_download` - 下载 YouTube 视频
- `POST /extra_audio` - 提取音频
- `POST /transcribe` - 语音识别
- `POST /translate_to_zh` - 翻译字幕
- `POST /tts` - 语音合成
- `POST /voice_connect` - 连接语音和视频

### 请求示例

```bash
# 下载视频
curl -X POST http://localhost:10310/yt_download \
  -H "Content-Type: application/json" \
  -d '{"video_id": "Am54LhN2NLk"}'

# 语音合成
curl -X POST http://localhost:10310/tts \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "Am54LhN2NLk",
    "tts_vendor": "cosyvoice2",
    "tts_character": "zh-CN-XiaoyiNeural",
    "audio_source": "video_voice"
  }'
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

