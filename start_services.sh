#!/bin/bash

# 启动EasyVideoTrans服务的脚本
# 使用conda环境：easy-video

echo "🚀 启动EasyVideoTrans服务..."

# 激活conda环境
source ~/miniconda3/etc/profile.d/conda.sh
conda activate easy-video

# 检查当前目录
if [ ! -f "app.py" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 创建必要的目录
mkdir -p output
mkdir -p workloads/static/outputs
mkdir -p celery_results

echo "📁 创建必要目录完成"

# 检查RabbitMQ状态
echo "🐰 检查RabbitMQ状态..."
sudo systemctl status rabbitmq-server --no-pager -l | head -3

# 启动GPU工作负载服务（后台运行）
echo "🎯 启动GPU工作负载服务（端口8199）..."
python inference.py &
INFERENCE_PID=$!
echo "GPU工作负载服务PID: $INFERENCE_PID"

# 等待一下让服务启动
sleep 3

# 启动Celery worker（后台运行）
echo "⚡ 启动Celery worker..."
celery -A src.task_manager.celery_tasks.celery_app worker --concurrency 1 -Q video_preview &
CELERY_PID=$!
echo "Celery worker PID: $CELERY_PID"

# 等待一下让Celery启动
sleep 3

echo "🌐 启动Flask主应用（端口5000）..."
echo "📝 进程ID保存信息："
echo "GPU工作负载服务PID: $INFERENCE_PID"
echo "Celery worker PID: $CELERY_PID"
echo ""
echo "💡 在浏览器中访问: http://localhost:5000"
echo "🛑 按Ctrl+C停止主服务"
echo ""

# 创建停止脚本
cat > stop_services.sh << 'EOF'
#!/bin/bash
echo "🛑 停止EasyVideoTrans服务..."

# 读取PID文件并停止进程
if [ -f ".service_pids" ]; then
    while read line; do
        if [[ $line == inference_pid:* ]]; then
            PID=${line#inference_pid:}
            echo "停止GPU工作负载服务 (PID: $PID)"
            kill $PID 2>/dev/null || echo "进程 $PID 可能已经停止"
        elif [[ $line == celery_pid:* ]]; then
            PID=${line#celery_pid:}
            echo "停止Celery worker (PID: $PID)"
            kill $PID 2>/dev/null || echo "进程 $PID 可能已经停止"
        fi
    done < .service_pids
    rm .service_pids
fi

# 额外清理：按名称杀死相关进程
pkill -f "python inference.py" 2>/dev/null
pkill -f "celery.*worker" 2>/dev/null

echo "✅ 服务停止完成"
EOF

chmod +x stop_services.sh

# 保存PID到文件
echo "inference_pid:$INFERENCE_PID" > .service_pids
echo "celery_pid:$CELERY_PID" >> .service_pids

# 定义清理函数
cleanup() {
    echo ""
    echo "🛑 接收到停止信号，正在清理..."
    kill $INFERENCE_PID 2>/dev/null
    kill $CELERY_PID 2>/dev/null
    rm -f .service_pids
    echo "✅ 清理完成，服务已停止"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 启动Flask主应用（前台运行）
python app.py

