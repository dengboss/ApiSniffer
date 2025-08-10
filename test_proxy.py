#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试代理服务器是否正常工作的脚本
"""

import requests
import time

def test_proxy():
    """测试代理服务器"""
    proxy_url = "http://127.0.0.1:8080"
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    print("正在测试代理服务器...")
    print(f"代理地址: {proxy_url}")
    
    try:
        # 测试访问 mitm.it
        print("\n1. 测试访问 http://mitm.it/")
        response = requests.get("http://mitm.it/", proxies=proxies, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text[:200]}...")
        
        # 测试访问一个API
        print("\n2. 测试访问 httpbin.org API")
        response = requests.get("http://httpbin.org/json", proxies=proxies, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text[:200]}...")
        
        print("\n✅ 代理服务器工作正常！")
        
    except requests.exceptions.ProxyError as e:
        print(f"❌ 代理连接失败: {e}")
    except requests.exceptions.ConnectTimeout as e:
        print(f"❌ 连接超时: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")

if __name__ == "__main__":
    test_proxy()