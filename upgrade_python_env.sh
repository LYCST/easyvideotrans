#!/bin/bash

# 升级 Python 环境脚本
echo "🚀 开始升级 Python 环境以支持 XTTS v2..."

# 检查当前环境
echo "📊 当前环境信息："
conda info --envs
echo "Python 版本："
python --version

# 创建新的 Python 3.10 环境
echo "🔧 创建新的 Python 3.10 环境..."
conda create -n easy-video-py310 python=3.10 -y

# 激活新环境
echo "🔄 激活新环境..."
conda activate easy-video-py310

# 安装依赖
echo "📦 安装项目依赖..."
pip install -r requirements.txt

# 安装 PyTorch (GPU 版本)
echo "🔧 安装 PyTorch (GPU 版本)..."
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# 安装 TTS 库
echo "🔧 安装 TTS 库..."
pip install TTS==0.22.0

# 创建必要的目录
echo "📁 创建必要目录..."
mkdir -p output/reference_audio
mkdir -p celery_results

echo "✅ 环境升级完成！"
echo ""
echo "📖 使用说明："
echo "1. 激活新环境: conda activate easy-video-py310"
echo "2. 启动服务: ./start_services.sh"
echo "3. 访问 Web 界面: http://localhost:5000"
echo ""
echo "⚠️  注意：请更新 start_services.sh 中的环境名称"
