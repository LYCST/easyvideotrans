# TTS API 使用示例

## 基本用法

### 1. Edge TTS（不指定供应商）

```json
{
    "video_id": "Am54LhN2NLk",
    "tts_character": "zh-CN-XiaoyiNeural"
}
```

**说明**: 不指定 `tts_vendor`，系统自动推断为 Edge TTS

### 2. Edge TTS（明确指定供应商）

```json
{
    "video_id": "Am54LhN2NLk",
    "tts_vendor": "edge",
    "tts_character": "zh-CN-XiaoyiNeural"
}
```

**说明**: 明确指定使用 Edge TTS

### 3. XTTS v2（不指定供应商）

```json
{
    "video_id": "Am54LhN2NLk",
    "reference_audio_path": "/path/to/reference_audio.wav",
    "language": "zh"
}
```

**说明**: 不指定 `tts_vendor`，但提供 `reference_audio_path`，系统自动推断为 XTTS v2

### 4. XTTS v2（明确指定供应商）

```json
{
    "video_id": "Am54LhN2NLk",
    "tts_vendor": "xtts_v2",
    "reference_audio_path": "/path/to/reference_audio.wav",
    "language": "zh",
    "model_name": "tts_models/multilingual/multi-dataset/xtts_v2"
}
```

**说明**: 明确指定使用 XTTS v2

## cURL 示例

### Edge TTS

```bash
# 方式 1: 不指定供应商
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "video_id": "Am54LhN2NLk",
    "tts_character": "zh-CN-XiaoyiNeural"
  }' \
  http://localhost:5000/tts

# 方式 2: 明确指定供应商
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "video_id": "Am54LhN2NLk",
    "tts_vendor": "edge",
    "tts_character": "zh-CN-XiaoyiNeural"
  }' \
  http://localhost:5000/tts
```

### XTTS v2

```bash
# 方式 1: 不指定供应商（自动推断）
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "video_id": "Am54LhN2NLk",
    "reference_audio_path": "/path/to/reference_audio.wav",
    "language": "zh"
  }' \
  http://localhost:5000/tts

# 方式 2: 明确指定供应商
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "video_id": "Am54LhN2NLk",
    "tts_vendor": "xtts_v2",
    "reference_audio_path": "/path/to/reference_audio.wav",
    "language": "zh"
  }' \
  http://localhost:5000/tts
```

## Python 示例

```python
import requests

# Edge TTS（不指定供应商）
edge_tts_data = {
    "video_id": "Am54LhN2NLk",
    "tts_character": "zh-CN-XiaoyiNeural"
}

response = requests.post("http://localhost:5000/tts", json=edge_tts_data)
print(response.json())

# XTTS v2（不指定供应商，自动推断）
xtts_v2_data = {
    "video_id": "Am54LhN2NLk",
    "reference_audio_path": "/path/to/reference_audio.wav",
    "language": "zh"
}

response = requests.post("http://localhost:5000/tts", json=xtts_v2_data)
print(response.json())
```

## 自动推断规则

| 请求参数 | 自动推断结果 |
|----------|-------------|
| 无 `tts_vendor`，无 `reference_audio_path` | Edge TTS |
| 无 `tts_vendor`，有 `reference_audio_path` | XTTS v2 |
| 有 `tts_vendor` | 使用指定的供应商 |

## 注意事项

1. **向后兼容**: 原有的 Edge TTS 请求格式仍然有效
2. **自动推断**: 系统会根据参数自动选择最合适的 TTS 供应商
3. **明确指定**: 建议在需要特定功能时明确指定 `tts_vendor`
4. **参数验证**: XTTS v2 需要有效的参考音频文件路径
