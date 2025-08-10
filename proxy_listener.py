# 移除对mitmproxy模块的直接导入，改为通过subprocess调用
import json
import os
import threading
import asyncio
from PyQt5.QtCore import QObject, pyqtSignal
import sys
import subprocess
import time

class ProxyListener(QObject):
    # 定义信号，用于通知UI有新数据
    new_data_signal = pyqtSignal(dict)
    
    def __init__(self, port=8080):
        super().__init__()
        self.port = port
        self.captured_data = []
        self.is_running = False
        self.proxy_process = None
        self.allowed_domains = []  # 新增：允许的域名列表
        
    def get_mitmdump_path(self):
        """获取mitmdump可执行文件路径，优先系统安装的版本"""
        import os
        import subprocess
        
        # 首先尝试系统安装的mitmdump
        try:
            result = subprocess.run(['mitmdump', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return 'mitmdump'
        except:
            pass
        
        # 然后尝试本地目录的mitmdump.exe
        if getattr(sys, 'frozen', False):
            # 被PyInstaller打包
            base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        mitmdump_path = os.path.join(base_path, 'mitmdump.exe')
        if os.path.exists(mitmdump_path):
            # 测试本地mitmdump.exe是否可用
            try:
                result = subprocess.run([mitmdump_path, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return mitmdump_path
            except:
                pass
        
        # 最后兜底
        return 'mitmdump'

    def start_proxy(self):
        """启动mitmproxy代理服务器"""
        if self.is_running:
            return
        try:
            self.is_running = True
            import subprocess, os
            env = os.environ.copy()
            env['ALLOWED_DOMAINS'] = ','.join(self.allowed_domains)
            mitmdump_exe = self.get_mitmdump_path()
            
            # 先测试mitmdump是否可用
            try:
                test_result = subprocess.run([mitmdump_exe, '--version'], 
                                           capture_output=True, text=True, timeout=5)
                if test_result.returncode != 0:
                    raise Exception(f"mitmdump测试失败: {test_result.stderr}")
            except subprocess.TimeoutExpired:
                raise Exception("mitmdump响应超时，可能版本不兼容")
            except FileNotFoundError:
                raise Exception("未找到mitmdump程序，请先安装mitmproxy: pip install mitmproxy")
            
            self.proxy_process = subprocess.Popen([
                mitmdump_exe,
                "--listen-port", str(self.port),
                "--listen-host", "0.0.0.0",
                "--scripts", "mitm_writer.py"
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待一小段时间检查进程是否正常启动
            import time
            time.sleep(1)
            if self.proxy_process.poll() is not None:
                # 进程已经退出，获取错误信息
                stdout, stderr = self.proxy_process.communicate()
                error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "未知错误"
                raise Exception(f"mitmdump启动失败: {error_msg}")
                
        except Exception as e:
            self.is_running = False
            print(f"启动代理服务器失败: {e}")
            raise
        
    def _run_proxy_server(self):
        """使用mitmdump方式运行代理服务器"""
        import subprocess
        import sys
        
        # 使用命令行方式启动mitmdump
        cmd = [
            "mitmdump",
            "--listen-port", str(self.port),
            "--listen-host", "0.0.0.0",
            "--scripts", "mitm_writer.py"
        ]
        
        try:
            subprocess.run(cmd)
        except Exception as e:
            print(f"启动代理服务器失败: {e}")
        finally:
            self.is_running = False
            # 关闭事件循环
            try:
                loop.close()
            except:
                pass
    
    def stop_proxy(self):
        """停止代理服务器"""
        self.is_running = False
        # 终止mitmdump进程
        try:
            if hasattr(self, 'proxy_process') and self.proxy_process:
                self.proxy_process.terminate()
                self.proxy_process.wait(timeout=5)
                self.proxy_process = None
        except Exception as e:
            print(f"停止代理服务器失败: {e}")
    
    def get_captured_data(self):
        """获取所有捕获的数据"""
        return self.captured_data
    
    def clear_data(self):
        """清除所有捕获的数据"""
        self.captured_data = []
    
    def save_to_file(self, file_path):
        """将捕获的数据保存到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.captured_data, f, ensure_ascii=False, indent=2)

    def set_domain_filter(self, domains):
        """设置允许的域名列表"""
        self.allowed_domains = domains