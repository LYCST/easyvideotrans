# XTTS v2 (Coqui TTS) 使用指南

## 概述

XTTS v2 是一个强大的多语言语音合成模型，支持语音克隆功能。它可以根据提供的参考音频来克隆说话人的声音，并生成高质量的语音输出。

## 功能特点

- **多语言支持**: 支持中文、英文、日文、韩文、西班牙文、法文、德文、意大利文、葡萄牙文、俄文等多种语言
- **语音克隆**: 通过参考音频克隆说话人的声音特征
- **高质量输出**: 生成自然、流畅的语音
- **离线使用**: 完全本地运行，无需网络连接
- **兼容性**: 支持 Python 3.9+ (兼容模式) 和 Python 3.10+ (原生模式)

## 安装依赖

### 方案 1: 兼容版本安装 (Python 3.9)

```bash
# 使用兼容版本安装脚本
./install_xtts_v2_compatible.sh
```

### 方案 2: 原生版本安装 (Python 3.10+)

```bash
# 升级 Python 环境
./upgrade_python_env.sh

# 或手动安装
pip install TTS==0.22.0
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 方案 3: 手动安装

#### 1. 安装 TTS 库

```bash
pip install TTS==0.22.0
```

#### 2. 安装 PyTorch

```bash
# CPU 版本 (兼容模式)
pip install torch torchaudio

# GPU 版本 (原生模式，需要 Python 3.10+)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### 3. 其他依赖

项目会自动下载 XTTS v2 模型，首次使用时会从 Hugging Face 下载模型文件。

## 兼容性说明

### Python 版本兼容性

- **Python 3.9**: 使用兼容模式（命令行接口），功能完整但速度较慢
- **Python 3.10+**: 使用原生模式（Python API），性能最佳

### 模式说明

1. **兼容模式** (Python 3.9)
   - 使用 TTS 命令行工具
   - 避免 Python 版本兼容性问题
   - 处理速度较慢
   - 功能完整

2. **原生模式** (Python 3.10+)
   - 使用 Python API
   - 性能最佳
   - 支持更多高级功能

## 使用方法

### 1. 通过 Web 界面使用

1. 打开 EasyVideoTrans Web 界面
2. 在"中文字幕配音"部分选择 "XTTS v2 (Coqui TTS)"
3. 上传参考音频文件（用于语音克隆）
4. 选择目标语言
5. 点击"Generate TTS"开始生成

### 2. 通过 API 使用

#### 上传参考音频

```bash
curl -X POST -F "file=@reference_audio.wav" http://localhost:5000/upload_reference_audio
```

#### 生成 TTS

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "video_id": "your_video_id",
    "tts_vendor": "xtts_v2",
    "reference_audio_path": "/path/to/reference_audio.wav",
    "language": "zh",
    "model_name": "tts_models/multilingual/multi-dataset/xtts_v2"
  }' \
  http://localhost:5000/tts
```

### 3. 编程接口使用

```python
from src.service.tts import get_tts_client

# 创建 XTTS v2 客户端
tts_client = get_tts_client(
    tts_vendor='xtts_v2',
    reference_audio_path='path/to/reference_audio.wav',
    language='zh',
    model_name='tts_models/multilingual/multi-dataset/xtts_v2'
)

# 生成语音
tts_client.srt_to_voice('subtitle.srt', 'output_directory')
```

## 参数说明

### 必需参数

- **reference_audio_path**: 参考音频文件路径
  - 格式: WAV, MP3, FLAC 等常见音频格式
  - 时长: 建议 10-30 秒，包含清晰的语音
  - 质量: 建议使用高质量、无噪音的音频

### 可选参数

- **language**: 目标语言代码
  - `zh`: 中文
  - `en`: 英文
  - `ja`: 日文
  - `ko`: 韩文
  - `es`: 西班牙文
  - `fr`: 法文
  - `de`: 德文
  - `it`: 意大利文
  - `pt`: 葡萄牙文
  - `ru`: 俄文

- **model_name**: 模型名称
  - 默认: `tts_models/multilingual/multi-dataset/xtts_v2`

## 参考音频要求

### 音频质量要求

1. **清晰度**: 音频应该清晰，没有背景噪音
2. **时长**: 建议 10-30 秒，包含完整的句子
3. **格式**: 支持 WAV, MP3, FLAC 等格式
4. **采样率**: 建议 16kHz 或更高
5. **声道**: 单声道或立体声均可

### 内容建议

1. **多样性**: 包含不同的音调和语速
2. **自然性**: 使用自然的说话方式
3. **完整性**: 包含完整的句子，避免断句
4. **目标语言**: 如果生成中文语音，建议使用中文参考音频

## 性能优化

### 硬件要求

- **CPU**: 建议 4 核以上
- **内存**: 建议 8GB 以上
- **GPU**: 推荐使用 NVIDIA GPU，显存 4GB 以上 (仅原生模式)
- **存储**: 模型文件约 2GB

### 优化建议

1. **批量处理**: 一次性处理多个字幕条目
2. **GPU 加速**: 使用 GPU 可以显著提升处理速度 (仅原生模式)
3. **内存管理**: 处理大量文本时注意内存使用
4. **兼容模式**: 如果使用 Python 3.9，建议升级到 Python 3.10+ 以获得更好性能

## 常见问题

### Q: 模型下载失败怎么办？

A: 可以手动下载模型文件到 `~/.local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2/` 目录。

### Q: 生成的语音质量不理想？

A: 
1. 检查参考音频质量
2. 确保参考音频与目标语言匹配
3. 尝试使用更长的参考音频

### Q: 处理速度很慢？

A:
1. 检查是否使用了 GPU (仅原生模式)
2. 减少批量处理的文本长度
3. 关闭其他占用资源的程序
4. 考虑升级到 Python 3.10+ 使用原生模式

### Q: 内存不足错误？

A:
1. 增加系统内存
2. 减少批量处理的文本数量
3. 使用 CPU 模式（虽然速度较慢）

### Q: Python 版本兼容性问题？

A:
1. 使用兼容模式 (Python 3.9)
2. 升级到 Python 3.10+ 使用原生模式
3. 运行 `./install_xtts_v2_compatible.sh` 安装兼容版本

## 故障排除

### 错误信息

1. **"XTTS v2 not available"**
   - 解决方案: 安装 TTS 库 `pip install TTS==0.22.0`

2. **"Reference audio path is required"**
   - 解决方案: 提供有效的参考音频文件路径

3. **"Reference audio file not found"**
   - 解决方案: 检查音频文件路径是否正确

4. **"Failed to load XTTS v2 model"**
   - 解决方案: 检查网络连接，确保能下载模型文件

5. **"TTS command line tool not available"**
   - 解决方案: 重新安装 TTS 库 `pip install --force-reinstall TTS==0.22.0`

6. **Python 版本兼容性错误**
   - 解决方案: 使用兼容模式或升级 Python 版本

## 更新日志

- **v1.0.0**: 初始版本，支持基本的 XTTS v2 功能
- 支持多语言语音合成
- 支持语音克隆
- 集成到 EasyVideoTrans 工作流程中
- **v1.1.0**: 添加 Python 3.9 兼容性支持
- 支持兼容模式（命令行接口）
- 支持原生模式（Python API）
- 自动检测 Python 版本并选择合适的模式
