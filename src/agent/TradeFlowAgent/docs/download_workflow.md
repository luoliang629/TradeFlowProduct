# 贸易数据下载工作流程

## 回答你的问题

**不需要**先调用 `download_trade_data_artifact_tool` 再调用 `get_artifact_download_url`。

实际上，我们有三个相关的工具，各有不同用途：

## 工具说明

### 1. `download_trade_data_artifact_tool`
- **作用**：实际下载文件到本地磁盘
- **使用场景**：用户明确要求下载文件时

### 2. `get_artifact_download_info_tool`（原 get_artifact_download_url）
- **作用**：获取文件信息和下载方式，但不实际下载
- **使用场景**：用户询问文件大小、内容或下载方式时

### 3. `list_trade_data_artifacts_tool`
- **作用**：列出所有可用的 Artifacts
- **使用场景**：用户想查看有哪些数据可以下载时

## 正确的使用流程

### 场景 1：用户直接要求下载

```
用户：请下载刚才查询的贸易数据

智能体应该：
1. 直接调用 download_trade_data_artifact_tool
2. 返回下载的文件路径
```

### 场景 2：用户询问下载信息

```
用户：这个数据文件有多大？包含什么内容？

智能体应该：
1. 调用 get_artifact_download_info_tool
2. 显示文件大小、记录数、查询信息等
3. 不需要实际下载文件
```

### 场景 3：用户想了解可下载的文件

```
用户：我可以下载哪些数据？

智能体应该：
1. 调用 list_trade_data_artifacts_tool
2. 对每个 artifact，可选择性调用 get_artifact_download_info_tool 获取详情
3. 等待用户选择后再下载
```

## 代码示例

### 直接下载（推荐）

```python
# 用户要求下载时，直接下载
result = await download_trade_data_artifact_tool(
    artifact_id="temp_trade_data_electronics_20240108.csv"
)

# 返回给用户
if result["success"]:
    response = f"""
    ✅ 文件已下载成功！
    
    📁 文件位置：{result['file_path']}
    📄 文件名称：{result['file_name']}
    📊 数据记录：{result['records_count']} 条
    💾 文件大小：{result['size_bytes'] / 1024:.1f} KB
    """
```

### 先查看信息再下载

```python
# 用户询问文件信息
info = await get_artifact_download_info_tool(artifact_id)

if info["success"]:
    response = f"""
    📊 数据文件信息：
    
    文件名：{info['file_name']}
    大小：{info['file_size_readable']}
    记录数：{info['records_count']} 条
    查询类型：{info['query_info']['query_type']}
    
    如需下载，我可以帮您保存到本地。
    """
    
# 如果用户确认要下载
if user_confirms:
    result = await download_trade_data_artifact_tool(artifact_id)
```

## 智能体最佳实践

1. **用户说"下载"时**：直接调用 `download_trade_data_artifact_tool`
2. **用户询问文件信息时**：调用 `get_artifact_download_info_tool`
3. **用户不确定要下载什么时**：先用 `list_trade_data_artifacts_tool` 列出选项

## 为什么不生成下载链接？

在当前的 CLI 环境中：
- 没有 Web 服务器来托管文件
- 没有持久化存储来生成永久链接
- Artifacts 只在会话期间存在

因此，我们直接提供文件下载功能，而不是生成链接。在 Web 应用中，可以扩展 `get_artifact_download_info_tool` 来返回真实的下载 URL。