# -*- coding:utf-8 -*-
"""
导出功能模块
支持将OCR识别结果导出为Excel或CSV格式

Author: ZhangSY
Created time:2024/08/20
"""
import csv
import os
from openpyxl import Workbook

class ExportUtils:
    """导出工具类"""
    
    @staticmethod
    def export_to_csv(results, output_path):
        """将识别结果导出为CSV文件"""
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            
            # 写入表头
            writer.writerow(['图片文件名', '识别文本', '置信度', '状态'])
            
            # 写入数据
            for item in results:
                filename = item['filename']
                status = item['status']
                
                if status == 'success' and item['result']:
                    # 处理识别成功的结果
                    for line in item['result']:
                        try:
                            text = line[1][0] if isinstance(line, list) and len(line) > 1 else ""
                            confidence = line[1][1] if isinstance(line, list) and len(line) > 1 else 0.0
                            writer.writerow([filename, text, confidence, status])
                        except:
                            writer.writerow([filename, "", 0.0, status])
                else:
                    # 处理识别失败的结果
                    error = item.get('error', '')
                    writer.writerow([filename, error, 0.0, status])
        
        return True
    
    @staticmethod
    def export_to_excel(results, output_path):
        """将识别结果导出为Excel文件"""
        wb = Workbook()
        ws = wb.active
        ws.title = "OCR识别结果"
        
        # 写入表头
        headers = ['图片文件名', '识别文本', '置信度', '状态']
        ws.append(headers)
        
        # 写入数据
        for item in results:
            filename = item['filename']
            status = item['status']
            
            if status == 'success' and item['result']:
                # 处理识别成功的结果
                for line in item['result']:
                    try:
                        text = line[1][0] if isinstance(line, list) and len(line) > 1 else ""
                        confidence = line[1][1] if isinstance(line, list) and len(line) > 1 else 0.0
                        ws.append([filename, text, confidence, status])
                    except:
                        ws.append([filename, "", 0.0, status])
            else:
                # 处理识别失败的结果
                error = item.get('error', '')
                ws.append([filename, error, 0.0, status])
        
        wb.save(output_path)
        return True
    
    @staticmethod
    def export(results, output_path, export_format="csv"):
        """通用导出方法"""
        if export_format.lower() == "csv":
            return ExportUtils.export_to_csv(results, output_path)
        elif export_format.lower() == "excel" or export_format.lower() == "xlsx":
            return ExportUtils.export_to_excel(results, output_path)
        else:
            raise ValueError(f"不支持的导出格式: {export_format}")
