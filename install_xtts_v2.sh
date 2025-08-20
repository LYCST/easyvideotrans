#!/bin/bash

# XTTS v2 安装脚本
echo "🚀 开始安装 XTTS v2 (Coqui TTS)..."

# # 检查 conda 环境
# if command -v conda &> /dev/null; then
#     echo "📦 检测到 conda 环境"
#     # 激活 easy-video 环境
#     source ~/miniconda3/etc/profile.d/conda.sh
#     conda activate easy-video
# else
#     echo "⚠️  未检测到 conda 环境，使用系统 Python"
# fi

# # 安装 TTS 库
# echo "🔧 安装 TTS 库..."
# pip install TTS==0.22.0

# # 安装其他依赖
# echo "🔧 安装其他依赖..."
# pip install -r requirements.txt

# 创建必要的目录
echo "📁 创建必要目录..."
mkdir -p output/reference_audio
mkdir -p celery_results

# 下载 XTTS v2 模型（首次使用时会自动下载）
echo "📥 准备下载 XTTS v2 模型..."
python -c "
from TTS.api import TTS
try:
    print('正在下载 XTTS v2 模型...')
    tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
    print('XTTS v2 模型下载完成！')
except Exception as e:
    print(f'模型下载失败: {e}')
    print('首次使用时会自动下载模型')
"

echo "✅ XTTS v2 安装完成！"
echo ""
echo "📖 使用说明："
echo "1. 启动服务: ./start_services.sh"
echo "2. 访问 Web 界面: http://localhost:5000"
echo "3. 在 TTS 部分选择 'XTTS v2 (Coqui TTS)'"
echo "4. 上传参考音频文件"
echo "5. 开始生成语音"
echo ""
echo "📚 详细文档请查看: doc/xtts_v2_guide.md"
