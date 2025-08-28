#!/bin/bash

# EasyVideoTrans 部署脚本
set -e

echo "🚀 开始部署 EasyVideoTrans..."

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p /home/shuzuan/temp/output
mkdir -p workloads/static/outputs
mkdir -p translation_cache
mkdir -p celery_results

# 复制配置文件
echo "⚙️ 复制配置文件..."
if [ ! -f configs/easyvideotrans.json ]; then
    cp configs/easyvideotrans.json.example configs/easyvideotrans.json
    echo "✅ 已创建 configs/easyvideotrans.json"
fi

if [ ! -f configs/celery.json ]; then
    cp configs/celery.json.example configs/celery.json
    echo "✅ 已创建 configs/celery.json"
fi

# 构建 Docker 镜像
echo "🔨 构建 Docker 镜像..."
docker-compose build

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

echo "✅ 部署完成！"
echo ""
echo "📊 服务访问地址："
echo "  - 主应用: http://localhost:10310"
echo "  - RabbitMQ 管理界面: http://localhost:10311 (guest/guest)"
echo ""
echo "📝 常用命令："
echo "  - 查看日志: docker-compose logs -f"
echo "  - 停止服务: docker-compose down"
echo "  - 重启服务: docker-compose restart"
