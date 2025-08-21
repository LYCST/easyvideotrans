#!/usr/bin/env python3
"""
调试 OpenAI 客户端代理配置问题
"""

import os
import sys
import traceback

def debug_openai_client():
    """调试 OpenAI 客户端初始化"""
    print("=== 调试 OpenAI 客户端 ===")
    
    # 检查环境变量
    print("\n1. 检查环境变量:")
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            print(f"  {var}: {value}")
        else:
            print(f"  {var}: 未设置")
    
    # 检查 Python 模块
    print("\n2. 检查 Python 模块:")
    try:
        import openai
        print(f"  openai 版本: {openai.__version__}")
        
        # 检查 openai 模块的属性
        print("  openai 模块属性:")
        for attr in dir(openai):
            if not attr.startswith('_'):
                try:
                    value = getattr(openai, attr)
                    print(f"    {attr}: {type(value).__name__}")
                except:
                    print(f"    {attr}: <无法获取>")
    except Exception as e:
        print(f"  导入 openai 失败: {e}")
    
    # 检查 httpx 模块
    print("\n3. 检查 httpx 模块:")
    try:
        import httpx
        print(f"  httpx 版本: {httpx.__version__}")
        
        # 检查 httpx 的默认配置
        print("  httpx 默认配置:")
        try:
            client = httpx.Client()
            print(f"    默认代理: {client.proxies}")
            client.close()
        except Exception as e:
            print(f"    创建 httpx 客户端失败: {e}")
    except Exception as e:
        print(f"  导入 httpx 失败: {e}")
    
    # 尝试直接创建 OpenAI 客户端
    print("\n4. 尝试创建 OpenAI 客户端:")
    try:
        from openai import OpenAI
        
        # 获取 API key
        api_key = os.environ.get('OPENAI_API_KEY', 'test-key')
        print(f"  使用 API Key: {api_key[:10]}...")
        
        # 尝试创建客户端
        print("  正在创建 OpenAI 客户端...")
        client = OpenAI(api_key=api_key)
        print("  ✅ OpenAI 客户端创建成功!")
        
        return True
        
    except Exception as e:
        print(f"  ❌ OpenAI 客户端创建失败: {e}")
        print("  详细错误信息:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_openai_client()
    if success:
        print("\n✅ 调试完成，客户端创建成功!")
    else:
        print("\n❌ 调试完成，发现问题!")
        sys.exit(1)
