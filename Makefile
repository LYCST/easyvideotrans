.PHONY: help install test lint format clean docker-build docker-run docker-stop

help: ## 显示帮助信息
	@echo "EasyVideoTrans 项目管理工具"
	@echo ""
	@echo "可用命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## 安装依赖
	pip install -r requirements.txt
	pip install -r workloads/requirements.txt

install-dev: ## 安装开发依赖
	pip install -r requirements-dev.txt

test: ## 运行测试
	pytest tests/ -v

lint: ## 代码质量检查
	flake8 src/
	black --check src/
	isort --check-only src/

format: ## 格式化代码
	black src/
	isort src/

clean: ## 清理临时文件
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/

docker-build: ## 构建 Docker 镜像
	docker build -t easyvideotrans:latest .
	docker build -f Dockerfile.gpu -t easyvideotrans-gpu:latest .

docker-run: ## 启动 Docker 服务
	docker-compose up -d

docker-stop: ## 停止 Docker 服务
	docker-compose down

docker-logs: ## 查看 Docker 日志
	docker-compose logs -f

docker-clean: ## 清理 Docker 资源
	docker-compose down -v
	docker system prune -f

start-services: ## 启动所有服务
	@echo "启动 RabbitMQ..."
	@docker run -d --name rabbitmq -p 5672:5672 -p 10311:15672 rabbitmq:3-management || true
	@echo "启动主应用..."
	@python app.py &
	@echo "启动 GPU 工作负载..."
	@python workloads/inference.py &
	@echo "启动 Celery 工作进程..."
	@celery -A src.task_manager.celery_tasks.celery_app worker --concurrency 1 -Q video_preview --loglevel=info &
	@echo "所有服务已启动"

stop-services: ## 停止所有服务
	@pkill -f "python app.py" || true
	@pkill -f "python workloads/inference.py" || true
	@pkill -f "celery" || true
	@docker stop rabbitmq || true
	@docker rm rabbitmq || true
	@echo "所有服务已停止"
