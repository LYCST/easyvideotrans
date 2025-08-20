#!/usr/bin/env python3
"""
本地部署GPT翻译功能测试脚本
"""

import requests
import json
import sys

def test_local_gpt_connection(base_url, model_name, api_key=""):
    """
    测试本地GPT服务的连接和基本功能
    
    Args:
        base_url: API基础URL
        model_name: 模型名称
        api_key: API密钥（可选）
    """
    
    # 构建API URL
    api_url = base_url.rstrip('/') + "/chat/completions"
    
    # 构建请求头
    headers = {
        "Content-Type": "application/json",
    }
    
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    # 构建测试请求
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Translate 'Hello, how are you?' to Chinese."
            }
        ],
        "max_tokens": 100
    }
    
    try:
        print(f"测试连接: {api_url}")
        print(f"模型: {model_name}")
        print("发送请求...")
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 连接成功!")
            print(f"响应模型: {result.get('model', 'Unknown')}")
            print(f"翻译结果: {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ 连接失败: HTTP {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误: 无法连接到服务")
        print("请检查:")
        print("1. 本地服务是否已启动")
        print("2. API地址是否正确")
        print("3. 端口是否被占用")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        print("请检查模型是否已加载完成")
        return False
        
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def main():
    """主函数"""
    print("本地部署GPT翻译功能测试")
    print("=" * 50)
    
    # 获取用户输入
    base_url = input("请输入API基础URL (默认: http://localhost:11434/v1/): ").strip()
    if not base_url:
        base_url = "http://localhost:11434/v1/"
    
    model_name = input("请输入模型名称 (默认: qwen2.5:7b): ").strip()
    if not model_name:
        model_name = "qwen2.5:7b"
    
    api_key = input("请输入API密钥 (可选): ").strip()
    
    print("\n开始测试...")
    print("-" * 30)
    
    # 执行测试
    success = test_local_gpt_connection(base_url, model_name, api_key)
    
    if success:
        print("\n✅ 测试通过! 可以在EasyVideoTrans中使用此配置")
        print(f"配置信息:")
        print(f"  API地址: {base_url}")
        print(f"  模型名称: {model_name}")
        if api_key:
            print(f"  API密钥: {api_key[:8]}...")
        else:
            print(f"  API密钥: (无)")
    else:
        print("\n❌ 测试失败! 请检查配置后重试")
        sys.exit(1)

if __name__ == "__main__":
    main()
