#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mitmproxy 独立版本自动下载配置脚本
用于下载并配置独立版本的 mitmdump.exe
"""

import os
import sys
import urllib.request
import zipfile
import tempfile
import shutil
from pathlib import Path
import json

def get_latest_release_info():
    """获取最新版本信息"""
    try:
        url = "https://api.github.com/repos/mitmproxy/mitmproxy/releases/latest"
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read()
            return json.loads(data.decode('utf-8'))
    except Exception as e:
        print(f"获取版本信息失败: {e}")
        return None

def download_file_with_progress(url, filename):
    """下载文件并显示进度"""
    try:
        print(f"正在下载: {filename}")
        
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                percent = min(100, (block_num * block_size * 100) // total_size)
                print(f"\r下载进度: {percent}%", end='', flush=True)
        
        urllib.request.urlretrieve(url, filename, progress_hook)
        print()  # 换行
        return True
    except Exception as e:
        print(f"\n下载失败: {e}")
        return False

def download_mitmproxy_windows():
    """下载 Windows 独立版本的 mitmproxy"""
    print("正在下载 mitmproxy 独立版本...")
    
    # 获取最新版本信息
    release_info = get_latest_release_info()
    if not release_info:
        return try_direct_download()
    
    # 查找 Windows 独立版本的下载链接
    windows_asset = None
    for asset in release_info.get('assets', []):
        name = asset['name'].lower()
        if 'windows' in name and '.zip' in name:
            windows_asset = asset
            break
    
    if not windows_asset:
        return try_direct_download()
    
    # 下载文件
    download_url = windows_asset['browser_download_url']
    filename = windows_asset['name']
    
    # 下载到临时文件
    temp_file = tempfile.mktemp(suffix='.zip')
    
    if not download_file_with_progress(download_url, temp_file):
        return try_direct_download()
    
    return extract_mitmdump(temp_file)

def try_direct_download():
    """尝试直接下载已知的稳定版本"""
    print("尝试下载稳定版本...")
    
    # 已知的稳定版本下载链接
    stable_urls = [
        "https://snapshots.mitmproxy.org/10.1.6/mitmproxy-10.1.6-windows-x86_64.zip",
        "https://snapshots.mitmproxy.org/10.1.5/mitmproxy-10.1.5-windows-x86_64.zip",
        "https://snapshots.mitmproxy.org/10.1.4/mitmproxy-10.1.4-windows-x86_64.zip"
    ]
    
    for url in stable_urls:
        try:
            filename = url.split('/')[-1]
            temp_file = tempfile.mktemp(suffix='.zip')
            
            print(f"尝试下载: {filename}")
            if download_file_with_progress(url, temp_file):
                if extract_mitmdump(temp_file):
                    return True
        except Exception as e:
            print(f"下载失败: {e}")
            continue
    
    return False

def extract_mitmdump(zip_path):
    """从压缩包中提取 mitmdump.exe"""
    try:
        print("正在解压...")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 查找 mitmdump.exe
            mitmdump_found = False
            for file_info in zip_ref.filelist:
                if file_info.filename.endswith('mitmdump.exe') or file_info.filename.endswith('mitmdump'):
                    # 提取到当前目录
                    with zip_ref.open(file_info) as source:
                        with open('mitmdump.exe', 'wb') as target:
                            shutil.copyfileobj(source, target)
                    mitmdump_found = True
                    print("mitmdump.exe 已成功提取到当前目录")
                    break
            
            if not mitmdump_found:
                print("在压缩包中未找到 mitmdump.exe")
                return False
        
        # 清理临时文件
        try:
            os.unlink(zip_path)
        except:
            pass
        
        # 验证文件
        if os.path.exists('mitmdump.exe'):
            # 设置执行权限（Windows 下通常不需要，但保险起见）
            try:
                os.chmod('mitmdump.exe', 0o755)
            except:
                pass
            print("配置完成！")
            return True
        else:
            print("配置失败：mitmdump.exe 未找到")
            return False
            
    except Exception as e:
        print(f"解压失败: {e}")
        return False

def test_mitmdump():
    """测试 mitmdump 是否可用"""
    if not os.path.exists('mitmdump.exe'):
        return False
    
    try:
        import subprocess
        result = subprocess.run(['mitmdump.exe', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"mitmdump 测试成功: {result.stdout.strip()}")
            return True
        else:
            print(f"mitmdump 测试失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"mitmdump 测试异常: {e}")
        return False

def main():
    """主函数"""
    current_dir = Path.cwd()
    print(f"当前目录: {current_dir}")
    
    # 检查是否已存在 mitmdump.exe
    if os.path.exists('mitmdump.exe'):
        print("mitmdump.exe 已存在，正在备份...")
        if os.path.exists('mitmdump_old.exe'):
            try:
                os.remove('mitmdump_old.exe')
            except:
                pass
        try:
            os.rename('mitmdump.exe', 'mitmdump_old.exe')
        except:
            pass
    
    # 下载独立版本
    success = download_mitmproxy_windows()
    
    if success:
        # 测试是否可用
        if test_mitmdump():
            print("\n✅ 配置完成！现在可以运行程序了：")
            print("python main.py")
            return 0
        else:
            print("\n⚠️ mitmdump.exe 下载成功但无法正常运行")
    
    print("\n❌ 自动下载失败，请手动下载：")
    print("1. 访问：https://mitmproxy.org/downloads/")
    print("2. 下载 Windows Standalone Binaries")
    print("3. 解压后将 mitmdump.exe 复制到当前目录")
    print("4. 或者尝试从以下链接直接下载：")
    print("   https://snapshots.mitmproxy.org/10.1.6/mitmproxy-10.1.6-windows-x86_64.zip")
    return 1

if __name__ == "__main__":
    sys.exit(main())