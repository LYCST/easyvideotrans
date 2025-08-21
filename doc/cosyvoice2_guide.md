# CosyVoice2 集成指南

## 概述

CosyVoice2 是一个强大的多语言语音合成模型，支持零样本语音克隆和跨语种语音生成。本指南介绍如何在 easyvideotrans 项目中集成和使用 CosyVoice2。

## 功能特性

- **零样本语音克隆**：通过参考音频复刻说话人的声音
- **跨语种语音生成**：支持中文、英文、日文、粤语、韩语等
- **指令控制**：通过指令控制语音风格和情感
- **细粒度控制**：支持笑声、呼吸等细节控制

## 安装要求

1. **环境要求**：
   - Python 3.8+
   - PyTorch 2.0+
   - CUDA 支持（推荐）

2. **目录结构**：
   ```
   easy-video/
   ├── CosyVoice/          # CosyVoice 项目
   └── easyvideotrans/     # 当前项目
   ```

3. **依赖安装**：
   ```bash
   cd /home/shuzuan/prj/easy-video/CosyVoice
   pip install -e .
   ```

## 使用方法

### 1. 基本使用

```python
from src.service.tts import get_tts_client

# 创建 CosyVoice2 客户端
cosyvoice_client = get_tts_client(
    'cosyvoice2',
    model_path='pretrained_models/CosyVoice2-0.5B',
    reference_audio_path='/path/to/reference.wav',
    speaker_name='说话人名称',
    fp16=False
)

# 生成语音
result = cosyvoice_client.srt_to_voice(
    'input.srt', 
    'output_dir', 
    mode='zero_shot'
)
```

### 2. 零样本模式

```python
# 零样本语音克隆
cosyvoice_client = get_tts_client(
    'cosyvoice2',
    reference_audio_path='/path/to/reference.wav',
    speaker_name='希望你以后能够做的比我还好呦。'
)

result = cosyvoice_client.srt_to_voice(
    'input.srt', 
    'output_dir', 
    mode='zero_shot'
)
```

### 3. 跨语种模式

```python
# 跨语种语音生成
result = cosyvoice_client.srt_to_voice(
    'input.srt', 
    'output_dir', 
    mode='cross_lingual'
)
```

### 4. 指令模式

```python
# 指令控制语音风格
result = cosyvoice_client.srt_to_voice(
    'input.srt', 
    'output_dir', 
    mode='instruct',
    instruction='用四川话说这句话'
)
```

## API 参数说明

### get_tts_client 参数

- `tts_vendor`: 固定为 'cosyvoice2'
- `model_path`: 模型路径，默认为 'pretrained_models/CosyVoice2-0.5B'
- `reference_audio_path`: 参考音频路径（必需）
- `speaker_name`: 说话人名称（用于零样本模式）
- `load_jit`: 是否加载 JIT 模型，默认 False
- `load_trt`: 是否加载 TensorRT 模型，默认 False
- `load_vllm`: 是否加载 vLLM 模型，默认 False
- `fp16`: 是否使用 FP16 精度，默认 False

### srt_to_voice 参数

- `srt_file_path`: SRT 字幕文件路径
- `output_dir`: 输出目录
- `mode`: 生成模式
  - `'zero_shot'`: 零样本模式
  - `'cross_lingual'`: 跨语种模式
  - `'instruct'`: 指令模式
- `instruction`: 指令（仅用于 instruct 模式）

## 高级功能

### 1. 说话人管理

```python
# 添加零样本说话人
success = cosyvoice_client.add_zero_shot_speaker(
    '说话人名称',
    prompt_speech,
    'speaker_id'
)

# 保存说话人信息
cosyvoice_client.save_speaker_info()

# 列出可用说话人
speakers = cosyvoice_client.list_available_speakers()
```

### 2. 细粒度控制

在文本中使用特殊标记进行细粒度控制：

- `[laughter]`: 笑声
- `[breath]`: 呼吸声
- `<strong></strong>`: 强调
- `<|zh|>`, `<|en|>`, `<|jp|>`, `<|yue|>`, `<|ko|>`: 语言标记

示例：
```
在他讲述那个荒诞故事的过程中，他突然[laughter]停下来，因为他自己也被逗笑了[laughter]。
```

### 3. 流式生成

```python
# 使用生成器作为输入
def text_generator():
    yield '第一句话，'
    yield '第二句话，'
    yield '第三句话。'

for i, result in enumerate(cosyvoice_client.cosyvoice.inference_zero_shot(
    text_generator(), speaker_name, prompt_speech, stream=False)):
    torchaudio.save(f'output_{i}.wav', result['tts_speech'], cosyvoice_client.cosyvoice.sample_rate)
```

## 配置示例

### 1. 基本配置

```json
{
  "COSYVOICE2_MODEL_PATH": "pretrained_models/CosyVoice2-0.5B",
  "COSYVOICE2_REFERENCE_AUDIO": "/path/to/reference.wav",
  "COSYVOICE2_SPEAKER_NAME": "说话人名称",
  "COSYVOICE2_FP16": false
}
```

### 2. 高级配置

```json
{
  "COSYVOICE2_MODEL_PATH": "pretrained_models/CosyVoice2-0.5B",
  "COSYVOICE2_REFERENCE_AUDIO": "/path/to/reference.wav",
  "COSYVOICE2_SPEAKER_NAME": "说话人名称",
  "COSYVOICE2_LOAD_JIT": false,
  "COSYVOICE2_LOAD_TRT": false,
  "COSYVOICE2_LOAD_VLLM": false,
  "COSYVOICE2_FP16": false
}
```

## 故障排除

### 1. 常见错误

- **模型加载失败**：检查模型路径是否正确
- **参考音频加载失败**：确保音频文件存在且格式正确
- **内存不足**：尝试使用 FP16 模式或减少批处理大小

### 2. 性能优化

- 使用 FP16 模式可以提高推理速度
- 使用 TensorRT 可以进一步优化性能
- 使用 vLLM 可以支持更高的并发

### 3. 调试技巧

```python
# 检查模型状态
print(f"Model loaded: {cosyvoice_client.cosyvoice is not None}")
print(f"Reference audio loaded: {cosyvoice_client.prompt_speech is not None}")

# 检查可用说话人
speakers = cosyvoice_client.list_available_speakers()
print(f"Available speakers: {speakers}")
```

## 示例代码

完整的示例代码请参考 `test_cosyvoice2_integration.py` 文件。

## 注意事项

1. **参考音频要求**：参考音频应该是清晰的语音，时长建议 3-10 秒
2. **模型大小**：CosyVoice2-0.5B 模型较大，需要足够的显存
3. **语言支持**：支持中文、英文、日文、粤语、韩语等
4. **实时性**：首次加载模型需要时间，后续推理较快

## 相关链接

- [CosyVoice2 GitHub](https://github.com/FunAudioLLM/CosyVoice)
- [官方文档](https://funaudiollm.github.io/cosyvoice2)
- [模型下载](https://huggingface.co/FunAudioLLM/CosyVoice2)
