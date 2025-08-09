# 下载贸易数据 Artifacts 使用指南

## 概述

在查询贸易数据时，系统会自动将数据保存为 Artifacts（临时存储的 CSV 文件）。用户可以使用下载工具将这些数据导出到本地文件系统。

## 可用工具

### 1. list_trade_data_artifacts_tool

列出当前会话中所有可用的贸易数据 Artifacts。

```python
# 列出所有 Artifacts
result = await list_trade_data_artifacts_tool()

# 返回格式
{
    "success": True,
    "artifacts": [
        {
            "artifact_id": "temp_trade_data_electronics_20240108_143022.csv",
            "metadata": {
                "total_records": 100,
                "query_type": "product",
                ...
            }
        }
    ],
    "count": 1
}
```

### 2. download_trade_data_artifact_tool

下载指定的 Artifact 为 CSV 文件。

```python
# 下载单个 Artifact
result = await download_trade_data_artifact_tool(
    artifact_id="temp_trade_data_electronics_20240108_143022.csv",
    download_path="downloads"  # 可选，默认为 "downloads"
)

# 返回格式
{
    "success": True,
    "file_path": "/absolute/path/to/downloads/trade_data_electronics_20240108_143022.csv",
    "file_name": "trade_data_electronics_20240108_143022.csv",
    "size_bytes": 72336,
    "records_count": 100,
    "download_message": "文件已下载到: /absolute/path/to/file.csv"
}
```

### 3. export_all_trade_data_artifacts_tool

一次性导出所有贸易数据 Artifacts。

```python
# 导出所有 Artifacts
result = await export_all_trade_data_artifacts_tool(
    download_path="downloads/all"  # 可选，默认为 "downloads"
)

# 返回格式
{
    "success": True,
    "exported_count": 3,
    "failed_count": 0,
    "exported_files": [
        {
            "artifact_id": "temp_trade_data_electronics_20240108_143022.csv",
            "file_name": "trade_data_electronics_20240108_143022.csv",
            "file_path": "/absolute/path/to/file.csv",
            "size_bytes": 72336
        }
    ],
    "download_path": "/absolute/path/to/downloads/all"
}
```

## 使用场景

### 场景 1：查询并下载特定产品的贸易数据

```python
# 1. 查询贸易数据
trade_result = await get_trade_data_tool(
    product_desc="electronic components",
    start_date="2023-01-01",
    end_date="2023-12-31"
)

# 2. 获取 artifact_id
artifact_id = trade_result["artifact_info"]["artifact_id"]

# 3. 下载数据
download_result = await download_trade_data_artifact_tool(
    artifact_id=artifact_id,
    download_path="my_data"
)

print(f"数据已保存到: {download_result['file_path']}")
```

### 场景 2：批量导出会话中的所有数据

```python
# 1. 执行多个查询
await get_trade_data_tool(product_desc="electronics", ...)
await get_trade_data_tool(product_desc="textiles", ...)
await get_trade_data_tool(exporter="ABC Company", ...)

# 2. 导出所有数据
export_result = await export_all_trade_data_artifacts_tool(
    download_path="session_data"
)

print(f"导出了 {export_result['exported_count']} 个文件到 {export_result['download_path']}")
```

### 场景 3：选择性下载

```python
# 1. 列出所有 Artifacts
artifacts = await list_trade_data_artifacts_tool()

# 2. 筛选需要的数据
for artifact in artifacts["artifacts"]:
    metadata = artifact.get("metadata", {})
    
    # 只下载记录数超过 50 的数据
    if metadata.get("total_records", 0) > 50:
        await download_trade_data_artifact_tool(
            artifact_id=artifact["artifact_id"]
        )
```

## 在智能体对话中使用

用户可以通过自然语言请求下载数据：

- "请下载刚才查询的贸易数据"
- "把所有查询结果导出为 CSV 文件"
- "下载电子产品的贸易数据到本地"

智能体会自动调用相应的下载工具。

## CSV 文件格式

下载的 CSV 文件包含以下主要字段：

- `date`: 交易日期
- `importer`: 进口商
- `exporter`: 出口商
- `countryOfOrigin`: 原产国
- `countryOfDestination`: 目的国
- `hsCode`: HS 编码
- `goodsDesc`: 商品描述
- `quantity`: 数量
- `sumOfUsd`: 交易金额（美元）
- 更多字段...

## 注意事项

1. **文件命名**：下载时会自动移除 `temp_` 前缀，保持文件名清晰
2. **目录创建**：如果指定的下载目录不存在，会自动创建
3. **覆盖保护**：如果文件已存在，会覆盖原文件
4. **编码格式**：所有 CSV 文件使用 UTF-8 编码
5. **临时存储**：Artifacts 仅在会话期间有效，会话结束后会被清理

## 高级用法

### 自定义下载路径

```python
# 按日期组织下载
from datetime import datetime

date_folder = datetime.now().strftime("%Y-%m-%d")
await download_trade_data_artifact_tool(
    artifact_id=artifact_id,
    download_path=f"trade_data/{date_folder}"
)
```

### 批量处理下载的文件

```python
import pandas as pd
from pathlib import Path

# 导出所有数据
export_result = await export_all_trade_data_artifacts_tool()

# 合并所有 CSV 文件
all_data = []
for file_info in export_result["exported_files"]:
    df = pd.read_csv(file_info["file_path"])
    all_data.append(df)

# 创建合并的数据集
combined_df = pd.concat(all_data, ignore_index=True)
combined_df.to_csv("combined_trade_data.csv", index=False)
```

## 故障排除

1. **找不到 Artifact**：确保使用正确的 artifact_id，可以先用 `list_trade_data_artifacts_tool` 查看可用的 Artifacts

2. **权限错误**：确保对下载目录有写入权限

3. **磁盘空间**：大量数据下载前请确保有足够的磁盘空间

4. **编码问题**：如果在其他程序中打开 CSV 文件出现乱码，请确保使用 UTF-8 编码打开