"""
CSV 转换工具模块

用于将贸易数据 JSON 转换为 CSV 格式，便于后续分析
"""

import csv
import io
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


def trade_records_to_csv(trade_records: List[Dict[str, Any]]) -> str:
    """
    将贸易记录列表转换为 CSV 格式字符串
    
    Args:
        trade_records: 贸易记录列表，来自 Tendata API 响应
        
    Returns:
        str: CSV 格式的字符串数据
    """
    if not trade_records:
        return ""
    
    # 分析所有记录的字段，获取完整的字段列表
    all_fields = set()
    for record in trade_records:
        flattened = _flatten_trade_record(record)
        all_fields.update(flattened.keys())
    
    # 排序字段名，保证输出一致性
    fieldnames = sorted(all_fields)
    
    # 使用 StringIO 创建 CSV 内容
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator='\n')
    
    # 写入表头
    writer.writeheader()
    
    # 写入数据行
    for record in trade_records:
        flattened = _flatten_trade_record(record)
        # 确保所有字段都存在，缺失的填空值
        row = {field: flattened.get(field, '') for field in fieldnames}
        writer.writerow(row)
    
    csv_content = output.getvalue()
    output.close()
    
    logger.info(f"转换完成：{len(trade_records)} 条记录，{len(fieldnames)} 个字段")
    return csv_content


def _flatten_trade_record(record: Dict[str, Any]) -> Dict[str, str]:
    """
    扁平化单个贸易记录，处理嵌套结构和数组
    
    Args:
        record: 单个贸易记录
        
    Returns:
        扁平化的字段字典
    """
    flattened = {}
    
    for key, value in record.items():
        if value is None:
            flattened[key] = ''
        elif isinstance(value, (str, int, float, bool)):
            flattened[key] = str(value)
        elif isinstance(value, list):
            # 数组字段处理
            if not value:
                flattened[key] = ''
            elif len(value) == 1:
                # 单个元素直接展开
                flattened[key] = str(value[0])
            else:
                # 多个元素：用分号分隔，同时创建索引字段
                flattened[key] = '; '.join(str(item) for item in value)
                # 为主要数组字段创建单独的索引字段
                if key in ['goodsDesc', 'hsCode', 'productDesc']:
                    for i, item in enumerate(value):
                        flattened[f"{key}_{i+1}"] = str(item)
        elif isinstance(value, dict):
            # 嵌套字典处理
            for nested_key, nested_value in value.items():
                combined_key = f"{key}_{nested_key}"
                if nested_value is None:
                    flattened[combined_key] = ''
                else:
                    flattened[combined_key] = str(nested_value)
        else:
            # 其他类型转为字符串
            flattened[key] = str(value)
    
    return flattened


def generate_csv_filename(query_params: Dict[str, Any], timestamp: Optional[datetime] = None) -> str:
    """
    生成 CSV 文件名
    
    Args:
        query_params: 查询参数
        timestamp: 时间戳，默认为当前时间
        
    Returns:
        生成的文件名
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    # 基础时间戳
    time_str = timestamp.strftime("%Y%m%d_%H%M%S")
    
    # 构建描述性前缀
    prefix_parts = []
    
    if query_params.get('product_desc'):
        product = str(query_params['product_desc'])[:20]  # 截取前20个字符
        # 清理文件名中的特殊字符
        product = _clean_filename_part(product)
        prefix_parts.append(product)
    
    if query_params.get('hs_code'):
        prefix_parts.append(f"HS{query_params['hs_code']}")
    
    if query_params.get('exporter'):
        exporter = str(query_params['exporter'])[:15]  # 截取前15个字符
        exporter = _clean_filename_part(exporter)
        prefix_parts.append(f"exp_{exporter}")
    
    if query_params.get('importer'):
        importer = str(query_params['importer'])[:15]  # 截取前15个字符  
        importer = _clean_filename_part(importer)
        prefix_parts.append(f"imp_{importer}")
    
    # 组合文件名
    if prefix_parts:
        prefix = "_".join(prefix_parts)
        filename = f"trade_data_{prefix}_{time_str}.csv"
    else:
        filename = f"trade_data_{time_str}.csv"
    
    # 确保文件名长度合理
    if len(filename) > 100:
        filename = f"trade_data_{time_str}.csv"
    
    return filename


def _clean_filename_part(text: str) -> str:
    """
    清理文件名部分，移除特殊字符
    
    Args:
        text: 原始文本
        
    Returns:
        清理后的文本
    """
    import re
    # 保留字母、数字、中文字符，替换其他字符为下划线
    cleaned = re.sub(r'[^\w\u4e00-\u9fff]+', '_', text)
    # 移除开头结尾的下划线
    cleaned = cleaned.strip('_')
    return cleaned


def create_csv_metadata(query_params: Dict[str, Any], total_records: int, filename: str) -> Dict[str, Any]:
    """
    创建 CSV 文件的元数据信息
    
    Args:
        query_params: 查询参数
        total_records: 总记录数
        filename: 文件名
        
    Returns:
        元数据字典
    """
    return {
        "filename": filename,
        "created_at": datetime.now().isoformat(),
        "query_params": query_params,
        "total_records": total_records,
        "file_type": "csv",
        "mime_type": "text/csv",
        "description": f"贸易数据查询结果：{total_records} 条记录",
        "source": "Tendata API"
    }