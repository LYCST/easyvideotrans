#!/bin/bash

# XTTS v2 兼容版本安装脚本 (Python 3.9)
echo "🚀 开始安装 XTTS v2 兼容版本 (Python 3.9)..."

# 检查 conda 环境
if command -v conda &> /dev/null; then
    echo "📦 检测到 conda 环境"
    # 激活 easy-video 环境
    source ~/miniconda3/etc/profile.d/conda.sh
    conda activate easy-video
else
    echo "⚠️  未检测到 conda 环境，使用系统 Python"
fi

# 检查 Python 版本
echo "🐍 Python 版本："
python --version

# 安装 TTS 库
echo "🔧 安装 TTS 库..."
pip install TTS==0.22.0

# 安装 PyTorch (CPU 版本，避免兼容性问题)
echo "🔧 安装 PyTorch (CPU 版本)..."
pip install torch torchaudio

# 安装其他依赖
echo "🔧 安装其他依赖..."
pip install -r requirements.txt

# 创建必要的目录
echo "📁 创建必要目录..."
mkdir -p output/reference_audio
mkdir -p celery_results

# 测试 TTS 命令行工具
echo "🧪 测试 TTS 命令行工具..."
if command -v tts &> /dev/null; then
    echo "✅ TTS 命令行工具可用"
    tts --help | head -5
else
    echo "❌ TTS 命令行工具不可用，尝试重新安装..."
    pip install --force-reinstall TTS==0.22.0
fi

echo "✅ XTTS v2 兼容版本安装完成！"
echo ""
echo "📖 使用说明："
echo "1. 启动服务: ./start_services.sh"
echo "2. 访问 Web 界面: http://localhost:5000"
echo "3. 在 TTS 部分选择 'XTTS v2 (Coqui TTS)'"
echo "4. 上传参考音频文件"
echo "5. 开始生成语音"
echo ""
echo "⚠️  注意：此版本使用命令行接口，处理速度可能较慢"
echo "📚 详细文档请查看: doc/xtts_v2_guide.md"
