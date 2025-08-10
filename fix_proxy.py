#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理问题快速修复脚本
"""

import subprocess
import socket
import os
import sys
import time

def check_port(port):
    """检查端口是否被占用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def kill_mitmdump_processes():
    """终止所有mitmdump进程"""
    try:
        result = subprocess.run(['taskkill', '/F', '/IM', 'mitmdump.exe'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 已终止所有mitmdump进程")
        else:
            print("ℹ️  没有找到运行中的mitmdump进程")
    except Exception as e:
        print(f"❌ 终止进程失败: {e}")

def check_mitmdump():
    """检查mitmdump是否可用"""
    mitmdump_path = os.path.join(os.path.dirname(__file__), 'mitmdump.exe')
    if os.path.exists(mitmdump_path):
        try:
            result = subprocess.run([mitmdump_path, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ 本地mitmdump可用: {mitmdump_path}")
                return True
            else:
                print(f"❌ 本地mitmdump测试失败: {result.stderr}")
        except Exception as e:
            print(f"❌ 本地mitmdump测试异常: {e}")
    else:
        print(f"❌ 未找到本地mitmdump.exe: {mitmdump_path}")
    
    # 尝试系统安装的版本
    try:
        result = subprocess.run(['mitmdump', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ 系统mitmdump可用")
            return True
        else:
            print(f"❌ 系统mitmdump测试失败: {result.stderr}")
    except Exception as e:
        print(f"❌ 系统mitmdump不可用: {e}")
    
    return False

def test_proxy_start():
    """测试启动代理服务器"""
    mitmdump_path = os.path.join(os.path.dirname(__file__), 'mitmdump.exe')
    if not os.path.exists(mitmdump_path):
        mitmdump_path = 'mitmdump'
    
    print("🔄 尝试启动代理服务器...")
    try:
        process = subprocess.Popen([
            mitmdump_path,
            "--listen-port", "8080",
            "--listen-host", "0.0.0.0",
            "--scripts", "mitm_writer.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待2秒检查是否启动成功
        time.sleep(2)
        if process.poll() is None:
            print("✅ 代理服务器启动成功！")
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ 代理服务器启动失败:")
            print(f"错误信息: {stderr.decode('utf-8', errors='ignore')}")
            return False
    except Exception as e:
        print(f"❌ 启动代理服务器异常: {e}")
        return False

def main():
    """主函数"""
    print("🔧 API抓包工具 - 代理问题快速修复")
    print("=" * 50)
    
    # 1. 检查并终止现有进程
    print("\n1. 检查现有进程...")
    if check_port(8080):
        print("⚠️  端口8080被占用，正在终止相关进程...")
        kill_mitmdump_processes()
        time.sleep(1)
        if check_port(8080):
            print("❌ 端口仍被占用，请手动检查并终止占用进程")
            subprocess.run(['netstat', '-ano'], shell=True)
            return
    else:
        print("✅ 端口8080可用")
    
    # 2. 检查mitmdump
    print("\n2. 检查mitmdump...")
    if not check_mitmdump():
        print("❌ mitmdump不可用，请检查安装")
        print("解决方案：")
        print("  - 确保mitmdump.exe文件在当前目录")
        print("  - 或者运行: pip install mitmproxy")
        return
    
    # 3. 检查mitm_writer.py
    print("\n3. 检查脚本文件...")
    if os.path.exists('mitm_writer.py'):
        print("✅ mitm_writer.py存在")
    else:
        print("❌ 未找到mitm_writer.py文件")
        return
    
    # 4. 测试启动
    print("\n4. 测试代理启动...")
    if test_proxy_start():
        print("\n🎉 修复完成！现在可以正常使用代理功能了")
        print("\n📋 使用步骤：")
        print("1. 运行: python main.py")
        print("2. 点击'开始监听'按钮")
        print("3. 配置浏览器代理: 127.0.0.1:8080")
        print("4. 访问 http://mitm.it/ 安装证书")
    else:
        print("\n❌ 修复失败，请查看上述错误信息")
        print("\n🔍 建议检查：")
        print("- 防火墙设置")
        print("- 杀毒软件拦截")
        print("- 管理员权限")

if __name__ == "__main__":
    main()