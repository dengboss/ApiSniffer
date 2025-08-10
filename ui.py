from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pandas as pd
import os
import json
import time
from data_processor import DataProcessor
from proxy_listener import ProxyListener

class ApiSnifferUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.processor = DataProcessor()
        self.proxy_listener = ProxyListener(port=8080)
        self.proxy_listener.new_data_signal.connect(self.on_new_data)
        self.setupUi()
        # 新增：定时器自动读取抓包数据
        self.last_loaded_count = 0
        self.auto_load_timer = QTimer(self)
        self.auto_load_timer.timeout.connect(self.auto_load_captured_data)
        self.auto_load_timer.start(2000)  # 每2秒自动读取一次
        # 新增：初始化代理状态
        self.proxy_status = '已停止'
        self.update_status_bar()
        
    def setupUi(self):
        # 设置窗口基本属性
        self.setWindowTitle("API接口抓包工具")
        self.resize(800, 600)
        
        # 创建中央窗口部件
        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)
        
        # 创建垂直布局
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        
        # 创建顶部按钮区域
        self.topButtonLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.topButtonLayout)
        
        # 添加开始监听按钮
        self.startButton = QtWidgets.QPushButton("开始监听")
        self.startButton.clicked.connect(self.start_listening)
        self.topButtonLayout.addWidget(self.startButton)
        
        # 添加停止监听按钮
        self.stopButton = QtWidgets.QPushButton("停止监听")
        self.stopButton.clicked.connect(self.stop_listening)
        self.stopButton.setEnabled(False)
        self.topButtonLayout.addWidget(self.stopButton)
        
        
        # 添加导出Excel按钮
        self.exportButton = QtWidgets.QPushButton("导出Excel")
        self.exportButton.clicked.connect(self.export_to_excel)
        self.topButtonLayout.addWidget(self.exportButton)
        
        # 添加清除数据按钮
        self.clearButton = QtWidgets.QPushButton("清除数据")
        self.clearButton.clicked.connect(self.clear_data)
        self.topButtonLayout.addWidget(self.clearButton)
        
        # 添加域名过滤输入框
        self.domainFilterLayout = QtWidgets.QHBoxLayout()
        self.domainFilterLabel = QtWidgets.QLabel("只监听域名（逗号分隔）：")
        self.domainFilterEdit = QtWidgets.QLineEdit()
        self.domainFilterEdit.setPlaceholderText("如: example.com,api.test.com")
        self.domainFilterEdit.textChanged.connect(self.on_domain_filter_changed)
        self.domainFilterLayout.addWidget(self.domainFilterLabel)
        self.domainFilterLayout.addWidget(self.domainFilterEdit)
        self.mainLayout.addLayout(self.domainFilterLayout)
        
        # 创建表格视图
        self.tableWidget = QtWidgets.QTableWidget(self.centralWidget)
        self.mainLayout.addWidget(self.tableWidget)
        
        # 表格右键菜单
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.show_table_context_menu)
        
        # 创建状态栏
        self.statusBar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")
    
    def update_status_bar(self):
        """刷新状态栏，显示代理状态和数据条数"""
        data_count = 0
        if self.processor.data_frame is not None:
            data_count = len(self.processor.data_frame)
        self.statusBar.showMessage(f"代理状态：{self.proxy_status} | 已抓取数据：{data_count} 条")

    def start_listening(self):
        """开始监听网络数据"""
        try:
            self.proxy_listener.start_proxy()
            self.startButton.setEnabled(False)
            self.stopButton.setEnabled(True)
            self.proxy_status = '运行中'
            self.update_status_bar()
            QMessageBox.information(self, "提示", "代理服务器已启动，请在设备上设置代理：\n\n"  
                                   f"IP地址: 127.0.0.1\n端口: {self.proxy_listener.port}\n\n" 
                                   "并访问 http://mitm.it/ 安装证书")
        except Exception as e:
            self.proxy_status = '异常'
            self.update_status_bar()
            QMessageBox.critical(self, "错误", f"启动监听失败: {str(e)}")
    
    def stop_listening(self):
        """停止监听网络数据"""
        try:
            self.proxy_listener.stop_proxy()
            self.startButton.setEnabled(True)
            self.stopButton.setEnabled(False)
            self.proxy_status = '已停止'
            self.update_status_bar()
            
            # 处理捕获的数据
            captured_data = self.proxy_listener.get_captured_data()
            if captured_data:
                self.processor.load_from_captured_data(captured_data)
                self.update_table()
        except Exception as e:
            self.proxy_status = '异常'
            self.update_status_bar()
            QMessageBox.critical(self, "错误", f"停止监听失败: {str(e)}")
    
    def on_new_data(self, data_item):
        """处理新捕获的数据"""
        try:
            # 添加到处理器
            self.processor.add_item(data_item)
            # 更新表格
            self.update_table()
            self.update_status_bar()
        except Exception as e:
            self.statusBar.showMessage(f"处理新数据时出错: {str(e)}")
    
    
    
    def update_table(self):
        """更新表格显示数据"""
        if self.processor.data_frame is None or self.processor.data_frame.empty:
            return
            
        df = self.processor.data_frame
        
        # 设置表格列数和表头
        self.tableWidget.setColumnCount(len(df.columns))
        self.tableWidget.setHorizontalHeaderLabels(df.columns)
        
        # 设置表格行数
        self.tableWidget.setRowCount(len(df))
        
        # 填充表格数据
        for row in range(len(df)):
            for col, column_name in enumerate(df.columns):
                item = QtWidgets.QTableWidgetItem(str(df.iloc[row, col]))
                self.tableWidget.setItem(row, col, item)
        
        # 调整列宽以适应内容
        self.tableWidget.resizeColumnsToContents()
        self.update_status_bar()
    
    def export_to_excel(self):
        """导出数据到Excel"""
        if self.processor.data_frame is None or self.processor.data_frame.empty:
            QMessageBox.warning(self, "警告", "没有数据可导出！")
            return
        # 打开文件保存对话框
        file_path, _ = QFileDialog.getSaveFileName(self, "保存Excel文件", "", "Excel Files (*.xlsx)")
        if not file_path:
            return
        try:
            self.processor.save_to_excel(file_path)
            QMessageBox.information(self, "成功", f"数据已成功导出到 {file_path}")
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}\n详细信息:\n{tb}")
    
    def clear_data(self):
        """清除所有数据"""
        if self.processor.data_frame is not None and not self.processor.data_frame.empty:
            reply = QMessageBox.question(self, "确认", "确定要清除所有数据吗？", 
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.processor.data_frame = None
                self.proxy_listener.clear_data()
                self.tableWidget.setRowCount(0)
                # 新增：清空数据文件
                try:
                    with open('captured_data.json', 'w', encoding='utf-8') as f:
                        f.truncate(0)
                except Exception as e:
                    QMessageBox.warning(self, "警告", f"清空数据文件失败: {str(e)}")
                self.statusBar.showMessage("数据已清除")

    def auto_load_captured_data(self):
        """自动读取captured_data.json并刷新表格"""
        file_path = 'captured_data.json'
        if not os.path.exists(file_path):
            return
        new_items = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # 只加载新增的数据
                for line in lines[self.last_loaded_count:]:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        item = json.loads(line)
                        new_items.append(item)
                    except Exception:
                        continue
            if new_items:
                for item in new_items:
                    self.processor.add_item(item)
                self.update_table()
                self.last_loaded_count += len(new_items)
            self.update_status_bar()
        except Exception as e:
            self.statusBar.showMessage(f"自动加载数据出错: {str(e)}")

    def show_table_context_menu(self, pos):
        item = self.tableWidget.itemAt(pos)
        if item:
            menu = QMenu()
            copyAction = menu.addAction("复制")
            action = menu.exec_(self.tableWidget.viewport().mapToGlobal(pos))
            if action == copyAction:
                clipboard = QApplication.clipboard()
                clipboard.setText(item.text())

    def on_domain_filter_changed(self, text):
        # 域名过滤内容变化时，通知proxy_listener
        domains = [d.strip() for d in text.split(',') if d.strip()]
        self.proxy_listener.set_domain_filter(domains)