# ChatGPT 翻译功能使用指南

## 概述

EasyVideoTrans 已经支持使用 ChatGPT 进行字幕翻译，提供高质量的英文到中文翻译服务。

## 支持的模型

- **GPT-3.5 Turbo**: 性价比高，翻译质量良好
- **GPT-4**: 翻译质量更高，但成本较高
- **GPT-4 Turbo**: 最新模型，翻译质量最佳

## 使用步骤

### 1. 获取 OpenAI API 密钥

1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册或登录账户
3. 在 API Keys 页面创建新的 API 密钥
4. 复制并保存 API 密钥

### 2. 使用 ChatGPT 翻译

1. 在网页界面中选择 "翻译英文以生成配音字幕"
2. 输入 YouTube 视频 ID
3. 在 "Translation vendor" 下拉菜单中选择 ChatGPT 模型：
   - `gpt-3.5-turbo-0125` (推荐)
   - `gpt-4`
   - `gpt-4-turbo`
4. 在 "Translation API Key" 字段中输入你的 OpenAI API 密钥
5. 点击 "Translate to Chinese" 开始翻译

## 功能特点

### 专业术语翻译
- 系统内置专业术语翻译对照表 (`configs/gpt_terms.json`)
- 自动识别并正确翻译技术术语
- 支持自定义术语翻译规则

### 智能翻译优化
- 基于上下文的智能翻译
- 自动纠正明显的单词错误
- 生成符合中文表达习惯的字幕

### 并发处理
- 支持多线程并发翻译
- 提高翻译效率
- 自动重试机制确保翻译成功

## 成本说明

- **GPT-3.5 Turbo**: 约 $0.0015 / 1K tokens
- **GPT-4**: 约 $0.03 / 1K tokens  
- **GPT-4 Turbo**: 约 $0.01 / 1K tokens

*价格可能因 OpenAI 政策调整而变化*

## 配置说明

### 术语翻译配置

编辑 `configs/gpt_terms.json` 文件来自定义专业术语翻译：

```json
{
    "agent": "智能体",
    "environment": "环境",
    "state": "状态",
    "action": "动作",
    "reward": "奖励"
}
```

### 翻译参数配置

在 `src/service/translation/gpt_translator.py` 中可以调整：

- `max_tokens`: 单次翻译的最大 token 数 (默认: 1200)
- `max_workers`: 并发翻译线程数 (默认: 30)
- 重试策略和超时设置

## 故障排除

### 常见问题

1. **API 密钥错误**
   - 检查 API 密钥是否正确
   - 确认账户有足够的余额

2. **翻译失败**
   - 检查网络连接
   - 确认 OpenAI API 服务状态
   - 查看日志获取详细错误信息

3. **翻译质量不佳**
   - 尝试使用更高级的模型 (GPT-4)
   - 检查术语翻译配置
   - 调整翻译参数

### 日志查看

翻译过程中的详细日志会输出到控制台，包括：
- 翻译进度
- API 调用统计
- 错误信息

## 最佳实践

1. **选择合适的模型**
   - 一般内容：使用 GPT-3.5 Turbo
   - 专业内容：使用 GPT-4 或 GPT-4 Turbo

2. **优化术语翻译**
   - 根据视频内容更新术语翻译表
   - 保持术语翻译的一致性

3. **成本控制**
   - 监控 API 使用量
   - 合理设置并发数
   - 使用适当的 token 限制

## 技术支持

如遇到问题，请：
1. 查看控制台日志
2. 检查配置文件
3. 确认 API 密钥和网络连接
4. 联系技术支持团队
