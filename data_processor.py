import json
import pandas as pd

class DataProcessor:
    def __init__(self):
        self.data_frame = None
    
    def load_from_file(self, file_path):
        """从文件加载数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 处理数据
            processed_data = self.process_data(data)
            if processed_data:
                self.data_frame = pd.DataFrame(processed_data)
                return True
            return False
        except Exception as e:
            print(f"加载文件时出错: {e}")
            raise
    
    def load_from_captured_data(self, captured_data):
        """从捕获的数据加载"""
        try:
            # 处理数据
            processed_data = self.process_data(captured_data)
            if processed_data:
                self.data_frame = pd.DataFrame(processed_data)
                return True
            return False
        except Exception as e:
            print(f"处理捕获数据时出错: {e}")
            raise
    
    def process_data(self, data):
        """处理JSON数据"""
        # 这里的处理逻辑需要根据实际抓取的数据格式调整
        # 下面是一个简单的示例
        result = []
        
        # 假设data是一个字典，包含一个列表
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    # 提取需要的字段
                    processed_item = {}
                    # 这里需要根据实际数据结构调整字段名
                    for key, value in item.items():
                        processed_item[key] = value
                    result.append(processed_item)
        elif isinstance(data, dict):
            # 如果是单个对象，尝试提取其中的列表
            for key, value in data.items():
                if isinstance(value, list):
                    return self.process_data(value)
            # 如果没有列表，可能是单个数据项
            result.append(data)
        
        return result
    
    def save_to_excel(self, file_path):
        """保存数据到Excel文件"""
        if self.data_frame is not None:
            self.data_frame.to_excel(file_path, index=False)
            return True
        return False
    
    def add_item(self, item):
        """添加单个数据项"""
        if self.data_frame is None:
            self.data_frame = pd.DataFrame([item])
        else:
            # 创建一个新的DataFrame并追加
            new_df = pd.DataFrame([item])
            self.data_frame = pd.concat([self.data_frame, new_df], ignore_index=True)