# TTS API 文档

## 概述

EasyVideoTrans 支持多种 TTS (文本转语音) 供应商，包括 Edge TTS 和 XTTS v2。

## API 端点

### POST /tts

将字幕文件转换为语音文件。

#### 请求参数

**Edge TTS 请求示例：**

```json
{
  "video_id": "Am54LhN2NLk",
  "tts_vendor": "edge",
  "tts_character": "zh-CN-XiaoyiNeural"
}
```

**XTTS v2 请求示例：**

```json
{
  "video_id": "Am54LhN2NLk",
  "tts_vendor": "xtts_v2",
  "reference_audio_path": "/path/to/reference_audio.wav",
  "language": "zh",
  "model_name": "tts_models/multilingual/multi-dataset/xtts_v2"
}
```

#### 参数说明

| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `video_id` | string | ✅ | - | YouTube 视频 ID |
| `tts_vendor` | string | ❌ | 自动推断 | TTS 供应商 ("edge" 或 "xtts_v2")，如果不指定则根据其他参数自动推断 |
| `tts_character` | string | ❌ | "zh-CN-XiaoyiNeural" | Edge TTS 语音角色 |
| `reference_audio_path` | string | ❌ | - | XTTS v2 参考音频文件路径 |
| `language` | string | ❌ | "zh" | XTTS v2 目标语言 |
| `model_name` | string | ❌ | "tts_models/multilingual/multi-dataset/xtts_v2" | XTTS v2 模型名称 |

#### 响应格式

**成功响应 (200)：**

```json
{
  "message": "TTS success using edge.",
  "video_id": "Am54LhN2NLk"
}
```

**错误响应 (400/404/500)：**

```json
{
  "message": "错误信息"
}
```

### POST /upload_reference_audio

上传参考音频文件用于 XTTS v2 语音克隆。

#### 请求格式

使用 `multipart/form-data` 格式上传文件。

#### 请求参数

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `file` | file | ✅ | 音频文件 (WAV, MP3, FLAC 等) |

#### 响应格式

**成功响应 (200)：**

```json
{
  "message": "Reference audio uploaded successfully: filename.wav",
  "file_path": "/path/to/uploaded/file.wav",
  "filename": "filename.wav"
}
```

## 使用示例

### cURL 示例

**Edge TTS：**

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "video_id": "Am54LhN2NLk",
    "tts_vendor": "edge",
    "tts_character": "zh-CN-XiaoyiNeural"
  }' \
  http://localhost:5000/tts
```

**XTTS v2：**

```bash
# 1. 上传参考音频
curl -X POST -F "file=@reference_audio.wav" \
  http://localhost:5000/upload_reference_audio

# 2. 生成 TTS
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "video_id": "Am54LhN2NLk",
    "tts_vendor": "xtts_v2",
    "reference_audio_path": "/path/to/reference_audio.wav",
    "language": "zh"
  }' \
  http://localhost:5000/tts
```

### Python 示例

```python
import requests

# Edge TTS
edge_tts_data = {
    "video_id": "Am54LhN2NLk",
    "tts_vendor": "edge",
    "tts_character": "zh-CN-XiaoyiNeural"
}

response = requests.post("http://localhost:5000/tts", json=edge_tts_data)
print(response.json())

# XTTS v2
xtts_v2_data = {
    "video_id": "Am54LhN2NLk",
    "tts_vendor": "xtts_v2",
    "reference_audio_path": "/path/to/reference_audio.wav",
    "language": "zh"
}

response = requests.post("http://localhost:5000/tts", json=xtts_v2_data)
print(response.json())
```

## 错误代码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 文件或资源不存在 |
| 500 | 服务器内部错误 |

## 自动推断规则

如果不指定 `tts_vendor` 参数，系统会根据其他参数自动推断：

1. **如果提供了 `reference_audio_path`**：自动使用 XTTS v2
2. **如果没有提供 `reference_audio_path`**：自动使用 Edge TTS

## 注意事项

1. **Edge TTS**：无需额外配置，直接使用
2. **XTTS v2**：需要先上传参考音频文件
3. **参考音频要求**：建议 10-30 秒，清晰无噪音
4. **处理时间**：XTTS v2 处理时间较长，请耐心等待
5. **Python 版本**：XTTS v2 在 Python 3.9 下使用兼容模式，性能较慢
