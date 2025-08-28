# 新的视频处理工作流程

## 概述

新的工作流程采用分离式下载策略，分别下载高清视频和音频文件，然后进行音频处理，最后进行视频合成。

## 工作流程

### 1. 下载阶段

#### 新的下载策略 (`both`)
```bash
# 下载高清视频和音频文件
curl -X POST http://localhost:5000/yt_download \
  -H "Content-Type: application/json" \
  -d '{"video_id": "6qmaOIhqG5Y", "download_strategy": "both"}'
```

**下载内容**:
- `{video_id}_fhd.mp4` - 高清视频（仅视频流，无音频）
- `{video_id}.wav` - 音频文件（高质量音频）

#### 传统下载策略 (`legacy`)
```bash
# 下载普通视频和高清视频
curl -X POST http://localhost:5000/yt_download_legacy \
  -H "Content-Type: application/json" \
  -d '{"video_id": "6qmaOIhqG5Y"}'
```

**下载内容**:
- `{video_id}.mp4` - 普通视频（包含音频）
- `{video_id}_fhd.mp4` - 高清视频（仅视频流）

### 2. 音频处理阶段

#### 新流程（推荐）
```bash
# 1. 音频背景分离（直接使用下载的音频）
curl -X POST http://localhost:5000/remove_audio_bg \
  -H "Content-Type: application/json" \
  -d '{"video_id": "6qmaOIhqG5Y"}'

# 2. 语音识别（使用分离后的音频）
curl -X POST http://localhost:5000/transcribe \
  -H "Content-Type: application/json" \
  -d '{"video_id": "6qmaOIhqG5Y"}'

# 3. 字幕翻译
curl -X POST http://localhost:5000/translate_to_zh \
  -H "Content-Type: application/json" \
  -d '{"video_id": "6qmaOIhqG5Y", "translate_vendor": "gpt-local"}'

# 4. 语音合成
curl -X POST http://localhost:5000/tts \
  -H "Content-Type: application/json" \
  -d '{"video_id": "6qmaOIhqG5Y", "TTS": "edge"}'

# 5. 音频合并
curl -X POST http://localhost:5000/voice_connect \
  -H "Content-Type: application/json" \
  -d '{"video_id": "6qmaOIhqG5Y"}'
```

#### 传统流程（兼容）
```bash
# 1. 音频提取（从普通视频中提取）
curl -X POST http://localhost:5000/extra_audio \
  -H "Content-Type: application/json" \
  -d '{"video_id": "6qmaOIhqG5Y"}'

# 后续步骤相同...
```

### 3. 视频合成阶段

```bash
# 视频预览合成（使用高清视频）
curl -X POST http://localhost:5000/video_preview \
  -H "Content-Type: application/json" \
  -d '{"video_id": "6qmaOIhqG5Y", "hardcode_subtitles": true}'
```

## 优势对比

### 新流程优势

| 方面 | 新流程 | 传统流程 |
|------|--------|----------|
| **下载速度** | 更快（分离下载） | 较慢（完整视频） |
| **存储空间** | 更少（无重复音频） | 更多（视频包含音频） |
| **音频质量** | 更高（直接下载高质量音频） | 一般（从视频提取） |
| **处理效率** | 更高（无需音频提取） | 较低（需要音频提取） |
| **错误处理** | 更简单（直接使用音频） | 复杂（音频提取可能失败） |

### 文件结构对比

#### 新流程文件结构
```
output/
├── 6qmaOIhqG5Y_fhd.mp4     # 高清视频（无音频）
├── 6qmaOIhqG5Y.wav         # 高质量音频
├── 6qmaOIhqG5Y_no_bg.wav   # 分离后的人声
├── 6qmaOIhqG5Y_bg.wav      # 分离后的背景音乐
├── 6qmaOIhqG5Y_zh.wav      # 中文TTS音频
├── 6qmaOIhqG5Y_en.srt      # 英文字幕
├── 6qmaOIhqG5Y_zh_merged.srt # 中文字幕
└── 6qmaOIhqG5Y_preview.mp4 # 最终合成视频
```

#### 传统流程文件结构
```
output/
├── 6qmaOIhqG5Y.mp4         # 普通视频（包含音频）
├── 6qmaOIhqG5Y_fhd.mp4     # 高清视频（无音频）
├── 6qmaOIhqG5Y.wav         # 从普通视频提取的音频
├── 6qmaOIhqG5Y_no_bg.wav   # 分离后的人声
├── 6qmaOIhqG5Y_bg.wav      # 分离后的背景音乐
├── 6qmaOIhqG5Y_zh.wav      # 中文TTS音频
├── 6qmaOIhqG5Y_en.srt      # 英文字幕
├── 6qmaOIhqG5Y_zh_merged.srt # 中文字幕
└── 6qmaOIhqG5Y_preview.mp4 # 最终合成视频
```

## 使用建议

### 推荐使用新流程
- **新项目**: 直接使用 `both` 下载策略
- **高质量要求**: 新流程提供更好的音频质量
- **存储空间有限**: 新流程节省存储空间

### 兼容性考虑
- **现有项目**: 可以继续使用传统流程
- **迁移**: 可以逐步迁移到新流程
- **API兼容**: 所有API接口保持兼容

## 技术细节

### 下载策略说明

#### `both` 策略
```python
# 高清视频下载
video = yt.streams.filter(progressive=False, file_extension='mp4').order_by('resolution').desc().first()

# 音频下载
audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
```

#### `legacy` 策略
```python
# 普通视频下载
video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').asc().first()

# 高清视频下载
video = yt.streams.filter(progressive=False, file_extension='mp4').order_by('resolution').desc().first()
```

### 音频处理流程

#### 新流程
1. 直接使用下载的音频文件
2. 进行背景音乐分离
3. 使用分离后的人声进行语音识别
4. 生成字幕并进行翻译
5. 使用TTS生成中文音频
6. 合并音频文件

#### 传统流程
1. 从普通视频中提取音频
2. 进行背景音乐分离
3. 后续步骤相同...

## 总结

新的工作流程通过分离式下载策略，实现了更高效、更高质量的音频处理，同时保持了与现有系统的兼容性。推荐在新项目中使用新流程，以获得更好的性能和用户体验。
