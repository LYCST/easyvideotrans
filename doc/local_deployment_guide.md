# 本地部署ChatGPT翻译功能使用指南

## 概述

EasyVideoTrans 支持使用本地部署的ChatGPT兼容服务进行字幕翻译，无需依赖OpenAI官方API，保护隐私并降低成本。

## 支持的本地部署方案

### 1. Ollama
- **特点**: 简单易用，支持多种模型
- **安装**: `curl -fsSL https://ollama.ai/install.sh | sh`
- **启动**: `ollama serve`
- **API地址**: `http://localhost:11434/v1/`

### 2. LM Studio
- **特点**: 图形界面，易于管理
- **下载**: [LM Studio官网](https://lmstudio.ai/)
- **API地址**: `http://localhost:1234/v1/`

### 3. OpenLLM
- **特点**: 企业级部署方案
- **安装**: `pip install openllm`
- **API地址**: `http://localhost:3000/v1/`

### 4. vLLM
- **特点**: 高性能推理引擎
- **安装**: `pip install vllm`
- **API地址**: `http://localhost:8000/v1/`

## 使用步骤

### 1. 部署本地服务

#### 使用Ollama (推荐)

1. **安装Ollama**:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **启动服务**:
   ```bash
   ollama serve
   ```

3. **下载模型**:
   ```bash
   # 下载中文友好的模型
   ollama pull qwen2.5:7b
   # 或者下载其他模型
   ollama pull llama3.1:8b
   ollama pull mistral:7b
   ```

#### 使用LM Studio

1. 下载并安装LM Studio
2. 在模型库中下载所需模型
3. 启动本地服务器 (Server → Start Server)

### 2. 配置EasyVideoTrans

1. **在网页界面中选择翻译功能**
2. **选择翻译供应商**: 选择 "本地部署 (自定义URL和模型)"
3. **配置参数**:
   - **API基础URL**: 输入本地服务的API地址
     - Ollama: `http://localhost:11434/v1/`
     - LM Studio: `http://localhost:1234/v1/`
     - OpenLLM: `http://localhost:3000/v1/`
     - vLLM: `http://localhost:8000/v1/`
   - **模型名称**: 输入已下载的模型名称
     - Ollama: `qwen2.5:7b`, `llama3.1:8b`, `mistral:7b`
     - LM Studio: 使用模型的实际名称
   - **API密钥**: 本地部署通常不需要，可以留空

### 3. 开始翻译

1. 输入YouTube视频ID
2. 点击 "Translate to Chinese" 开始翻译

## 推荐模型

### 中文翻译优化模型

1. **Qwen2.5系列** (推荐)
   - `qwen2.5:7b` - 平衡性能和资源消耗
   - `qwen2.5:14b` - 更好的翻译质量
   - `qwen2.5:32b` - 最佳翻译质量

2. **Llama3.1系列**
   - `llama3.1:8b` - 基础版本
   - `llama3.1:70b` - 高质量版本

3. **Mistral系列**
   - `mistral:7b` - 轻量级选择
   - `mistral:large` - 高质量选择

## 性能优化

### 硬件要求

- **最低配置**: 8GB RAM, 4核CPU
- **推荐配置**: 16GB+ RAM, 8核+ CPU, GPU加速
- **GPU加速**: 支持CUDA的NVIDIA显卡

### 优化建议

1. **选择合适的模型大小**:
   - 资源有限: 使用7B参数模型
   - 追求质量: 使用14B+参数模型

2. **调整并发设置**:
   - 在 `src/service/translation/gpt_translator.py` 中调整 `max_workers`
   - 本地部署建议设置为5-10

3. **网络优化**:
   - 确保本地服务稳定运行
   - 监控服务资源使用情况

## 故障排除

### 常见问题

1. **连接失败**
   - 检查本地服务是否启动
   - 验证API地址是否正确
   - 确认端口是否被占用

2. **模型加载失败**
   - 检查模型是否已下载
   - 验证模型名称是否正确
   - 确认有足够的内存

3. **翻译质量不佳**
   - 尝试更大的模型
   - 检查模型是否支持中文
   - 调整翻译参数

### 调试方法

1. **检查服务状态**:
   ```bash
   # Ollama
   curl http://localhost:11434/api/tags
   
   # LM Studio
   curl http://localhost:1234/v1/models
   ```

2. **测试API调用**:
   ```bash
   curl -X POST http://localhost:11434/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "qwen2.5:7b",
       "messages": [{"role": "user", "content": "Hello"}],
       "max_tokens": 100
     }'
   ```

3. **查看日志**:
   - 检查EasyVideoTrans控制台输出
   - 查看本地服务日志

## 安全考虑

1. **网络安全**:
   - 本地部署避免数据外泄
   - 确保本地网络环境安全

2. **模型安全**:
   - 从可信源下载模型
   - 定期更新模型版本

3. **API安全**:
   - 本地服务通常不需要API密钥
   - 如需认证，使用简单的密钥机制

## 成本对比

| 方案 | 初始成本 | 运行成本 | 隐私保护 |
|------|----------|----------|----------|
| OpenAI API | 低 | 高 | 差 |
| 本地部署 | 中 | 低 | 好 |

## 技术支持

如遇到问题，请：
1. 检查本地服务状态
2. 验证配置参数
3. 查看错误日志
4. 参考各服务的官方文档
