"""
预定义函数库

为代码执行环境提供常用的贸易数据分析函数
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd
import numpy as np
from io import StringIO
import logging

logger = logging.getLogger(__name__)

# 全局变量，用于存储artifacts管理器和上下文
_artifacts_manager = None
_execution_context = None


def set_execution_context(artifacts_manager, context):
    """设置执行上下文"""
    global _artifacts_manager, _execution_context
    _artifacts_manager = artifacts_manager
    _execution_context = context


def load_trade_data(artifact_id: str) -> pd.DataFrame:
    """
    从 Artifact 加载贸易数据
    
    Args:
        artifact_id: Artifact ID
        
    Returns:
        贸易数据 DataFrame
    """
    try:
        if not _artifacts_manager:
            raise RuntimeError("Artifacts manager 未初始化")
        
        # 读取 CSV 数据
        load_result = _artifacts_manager.artifacts.get(artifact_id)
        if not load_result:
            raise ValueError(f"未找到 Artifact: {artifact_id}")
        
        csv_content = load_result.get("content", "")
        if not csv_content:
            raise ValueError(f"Artifact {artifact_id} 内容为空")
        
        # 解析CSV为DataFrame
        df = pd.read_csv(StringIO(csv_content))
        
        # 数据类型优化
        df = optimize_dataframe_types(df)
        
        print(f"✅ 成功加载贸易数据: {len(df)} 条记录, {len(df.columns)} 个字段")
        return df
        
    except Exception as e:
        logger.error(f"加载贸易数据失败: {str(e)}")
        raise RuntimeError(f"加载贸易数据失败: {str(e)}")


def optimize_dataframe_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    优化DataFrame数据类型
    
    Args:
        df: 原始DataFrame
        
    Returns:
        优化后的DataFrame
    """
    df_optimized = df.copy()
    
    for col in df_optimized.columns:
        # 尝试转换数值列
        if col in ['quantity', 'sumOfUsd', 'unitPrice', 'weight', 'weightUnitPriceUsd', 'quantityUnitPriceUsd']:
            df_optimized[col] = pd.to_numeric(df_optimized[col], errors='coerce')
        
        # 转换日期列
        elif col in ['date']:
            df_optimized[col] = pd.to_datetime(df_optimized[col], errors='coerce')
        
        # 优化字符串列
        elif df_optimized[col].dtype == 'object':
            df_optimized[col] = df_optimized[col].astype('string')
    
    return df_optimized


def analyze_trade_trends(df: pd.DataFrame, period: str = 'month', value_col: str = 'sumOfUsd') -> pd.DataFrame:
    """
    分析贸易趋势
    
    Args:
        df: 贸易数据DataFrame
        period: 时间周期 ('day', 'month', 'quarter', 'year')
        value_col: 分析的数值列
        
    Returns:
        趋势分析结果DataFrame
    """
    if 'date' not in df.columns:
        raise ValueError("数据中缺少日期列")
    
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'])
    
    # 根据周期分组
    if period == 'day':
        df_copy['period'] = df_copy['date'].dt.date
    elif period == 'month':
        df_copy['period'] = df_copy['date'].dt.to_period('M')
    elif period == 'quarter':
        df_copy['period'] = df_copy['date'].dt.to_period('Q')
    elif period == 'year':
        df_copy['period'] = df_copy['date'].dt.year
    else:
        raise ValueError("不支持的时间周期，请选择: day, month, quarter, year")
    
    # 聚合数据
    trends = df_copy.groupby('period').agg({
        value_col: ['sum', 'mean', 'count'],
        'quantity': 'sum'
    }).round(2)
    
    trends.columns = ['总额', '平均值', '交易次数', '总数量']
    trends = trends.reset_index()
    
    print(f"✅ 生成 {period} 级别趋势分析，共 {len(trends)} 个时间点")
    return trends


def top_importers(df: pd.DataFrame, top_n: int = 10, value_col: str = 'sumOfUsd') -> pd.DataFrame:
    """
    分析最活跃的进口商
    
    Args:
        df: 贸易数据DataFrame
        top_n: 返回前N名
        value_col: 分析的数值列
        
    Returns:
        进口商排名DataFrame
    """
    if 'importer' not in df.columns:
        raise ValueError("数据中缺少进口商列")
    
    importers = df.groupby('importer').agg({
        value_col: 'sum',
        'quantity': 'sum',
        'id': 'count'
    }).round(2)
    
    importers.columns = ['总交易额', '总数量', '交易次数']
    importers = importers.sort_values('总交易额', ascending=False).head(top_n)
    importers = importers.reset_index()
    
    print(f"✅ 分析完成，返回前 {top_n} 名进口商")
    return importers


def top_exporters(df: pd.DataFrame, top_n: int = 10, value_col: str = 'sumOfUsd') -> pd.DataFrame:
    """
    分析最活跃的出口商
    
    Args:
        df: 贸易数据DataFrame
        top_n: 返回前N名
        value_col: 分析的数值列
        
    Returns:
        出口商排名DataFrame
    """
    if 'exporter' not in df.columns:
        raise ValueError("数据中缺少出口商列")
    
    exporters = df.groupby('exporter').agg({
        value_col: 'sum',
        'quantity': 'sum',
        'id': 'count'
    }).round(2)
    
    exporters.columns = ['总交易额', '总数量', '交易次数']
    exporters = exporters.sort_values('总交易额', ascending=False).head(top_n)
    exporters = exporters.reset_index()
    
    print(f"✅ 分析完成，返回前 {top_n} 名出口商")
    return exporters


def trade_volume_by_country(df: pd.DataFrame, country_type: str = 'destination') -> pd.DataFrame:
    """
    按国家分析贸易量
    
    Args:
        df: 贸易数据DataFrame
        country_type: 国家类型 ('origin', 'destination')
        
    Returns:
        国家贸易量DataFrame
    """
    country_col = f'countryOf{country_type.title()}'
    
    if country_col not in df.columns:
        raise ValueError(f"数据中缺少列: {country_col}")
    
    countries = df.groupby(country_col).agg({
        'sumOfUSD': 'sum',
        'quantity': 'sum',
        'id': 'count'
    }).round(2)
    
    countries.columns = ['总交易额', '总数量', '交易次数']
    countries = countries.sort_values('总交易额', ascending=False)
    countries = countries.reset_index()
    
    print(f"✅ 按{country_type}国家分析完成，共 {len(countries)} 个国家")
    return countries


def analyze_product_categories(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """
    分析产品类别
    
    Args:
        df: 贸易数据DataFrame
        top_n: 返回前N名产品类别
        
    Returns:
        产品类别分析DataFrame
    """
    product_columns = [col for col in df.columns if 'goodsDesc' in col or 'productDesc' in col]
    
    if not product_columns:
        raise ValueError("数据中缺少产品描述列")
    
    # 使用第一个找到的产品描述列
    product_col = product_columns[0]
    
    products = df.groupby(product_col).agg({
        'sumOfUsd': 'sum',
        'quantity': 'sum', 
        'id': 'count'
    }).round(2)
    
    products.columns = ['总交易额', '总数量', '交易次数']
    products = products.sort_values('总交易额', ascending=False).head(top_n)
    products = products.reset_index()
    
    print(f"✅ 产品类别分析完成，返回前 {top_n} 个产品类别")
    return products


def generate_summary_report(df: pd.DataFrame) -> Dict[str, Any]:
    """
    生成贸易数据摘要报告
    
    Args:
        df: 贸易数据DataFrame
        
    Returns:
        摘要报告字典
    """
    report = {}
    
    # 基本统计
    report['总记录数'] = len(df)
    report['数据字段数'] = len(df.columns)
    
    # 交易额统计
    if 'sumOfUsd' in df.columns:
        report['总交易额'] = f"${df['sumOfUsd'].sum():,.2f}"
        report['平均交易额'] = f"${df['sumOfUsd'].mean():,.2f}"
        report['最大单笔交易'] = f"${df['sumOfUsd'].max():,.2f}"
        report['最小单笔交易'] = f"${df['sumOfUsd'].min():,.2f}"
    
    # 数量统计
    if 'quantity' in df.columns:
        report['总交易数量'] = f"{df['quantity'].sum():,.0f}"
        report['平均交易数量'] = f"{df['quantity'].mean():,.1f}"
    
    # 时间范围
    if 'date' in df.columns:
        dates = pd.to_datetime(df['date'])
        report['时间范围'] = f"{dates.min().date()} 至 {dates.max().date()}"
        report['数据跨度'] = f"{(dates.max() - dates.min()).days} 天"
    
    # 参与方统计
    if 'importer' in df.columns:
        report['不重复进口商数量'] = df['importer'].nunique()
    
    if 'exporter' in df.columns:
        report['不重复出口商数量'] = df['exporter'].nunique()
    
    # 国家统计
    country_cols = [col for col in df.columns if 'country' in col.lower()]
    for col in country_cols:
        if df[col].nunique() > 0:
            report[f'{col}_数量'] = df[col].nunique()
    
    print("✅ 摘要报告生成完成")
    return report


def calculate_trade_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """
    计算贸易指标
    
    Args:
        df: 贸易数据DataFrame
        
    Returns:
        贸易指标字典
    """
    metrics = {}
    
    if 'sumOfUSD' in df.columns and 'quantity' in df.columns:
        # 平均单价
        df_with_price = df[df['quantity'] > 0].copy()
        if not df_with_price.empty:
            df_with_price['unit_price'] = df_with_price['sumOfUSD'] / df_with_price['quantity']
            metrics['平均单价'] = df_with_price['unit_price'].mean()
            metrics['单价标准差'] = df_with_price['unit_price'].std()
        
        # 交易额集中度（基尼系数近似）
        values = df['sumOfUSD'].sort_values()
        n = len(values)
        if n > 1:
            cumsum = values.cumsum()
            gini = 1 - 2 * (cumsum.sum() / (n * values.sum()))
            metrics['交易额基尼系数'] = gini
    
    # 贸易伙伴多样性
    if 'importer' in df.columns:
        metrics['进口商多样性指数'] = df['importer'].nunique() / len(df)
    
    if 'exporter' in df.columns:
        metrics['出口商多样性指数'] = df['exporter'].nunique() / len(df)
    
    print("✅ 贸易指标计算完成")
    return metrics


# 可视化函数（返回绘图代码字符串）
def plot_trade_timeline(df: pd.DataFrame, group_by: str = 'month') -> str:
    """
    生成贸易时间线图表代码
    
    Args:
        df: 贸易数据DataFrame
        group_by: 分组方式
        
    Returns:
        绘图代码字符串
    """
    plot_code = f"""
import matplotlib.pyplot as plt
import pandas as pd

# 确保日期列是datetime类型
df['date'] = pd.to_datetime(df['date'])

# 按{group_by}分组聚合数据
if '{group_by}' == 'month':
    df['period'] = df['date'].dt.to_period('M')
elif '{group_by}' == 'quarter':
    df['period'] = df['date'].dt.to_period('Q')
elif '{group_by}' == 'year':
    df['period'] = df['date'].dt.year
else:
    df['period'] = df['date'].dt.date

timeline_data = df.groupby('period')['sumOfUSD'].sum()

# 创建图表
plt.figure(figsize=(12, 6))
timeline_data.plot(kind='line', marker='o')
plt.title('贸易额时间趋势图', fontsize=14, pad=20)
plt.xlabel('时间周期', fontsize=12)
plt.ylabel('交易额 (USD)', fontsize=12)
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print(f"✅ 生成 {{len(timeline_data)}} 个时间点的趋势图")
"""
    return plot_code


def plot_top_products(df: pd.DataFrame, top_n: int = 10) -> str:
    """
    生成热门产品图表代码
    
    Args:
        df: 贸易数据DataFrame
        top_n: 显示前N个产品
        
    Returns:
        绘图代码字符串
    """
    plot_code = f"""
import matplotlib.pyplot as plt
import pandas as pd

# 找到产品描述列
product_col = None
for col in df.columns:
    if 'goodsDesc' in col or 'productDesc' in col:
        product_col = col
        break

if product_col is None:
    print("❌ 未找到产品描述列")
else:
    # 分析产品数据
    products = df.groupby(product_col)['sumOfUSD'].sum().sort_values(ascending=False).head({top_n})
    
    # 创建图表
    plt.figure(figsize=(12, 8))
    products.plot(kind='barh')
    plt.title('热门产品交易额排行', fontsize=14, pad=20)
    plt.xlabel('交易额 (USD)', fontsize=12)
    plt.ylabel('产品', fontsize=12)
    plt.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    plt.show()
    
    print(f"✅ 生成前 {{len(products)}} 个热门产品图表")
"""
    return plot_code


def trade_volume_by_country(df: pd.DataFrame, country_type: str = 'destination', top_n: int = 10) -> pd.DataFrame:
    """
    按国家分析贸易量
    
    Args:
        df: 贸易数据DataFrame
        country_type: 分析类型 ('destination' 或 'origin')
        top_n: 返回前N个国家
        
    Returns:
        国家贸易量排名DataFrame
    """
    if country_type == 'destination':
        country_col = 'countryOfDestination'
    elif country_type == 'origin':
        country_col = 'countryOfOrigin'
    else:
        raise ValueError("country_type 必须是 'destination' 或 'origin'")
    
    if country_col not in df.columns:
        raise ValueError(f"数据中缺少 {country_col} 列")
    
    countries = df.groupby(country_col).agg({
        'sumOfUsd': 'sum',
        'quantity': 'sum',
        'id': 'count'
    }).round(2)
    
    countries.columns = ['总交易额', '总数量', '交易次数']
    countries = countries.sort_values('总交易额', ascending=False).head(top_n)
    countries = countries.reset_index()
    
    print(f"✅ 按{country_type}国家分析完成，返回前 {top_n} 个国家")
    return countries


def calculate_trade_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    计算高级贸易指标
    
    Args:
        df: 贸易数据DataFrame
        
    Returns:
        贸易指标字典
    """
    metrics = {}
    
    # 贸易集中度 - 基于出口商
    if 'exporter' in df.columns and 'sumOfUsd' in df.columns:
        exporter_values = df.groupby('exporter')['sumOfUsd'].sum().sort_values(ascending=False)
        total_value = exporter_values.sum()
        if total_value > 0:
            # HHI指数（赫芬达尔-赫希曼指数）
            market_shares = exporter_values / total_value
            hhi = (market_shares ** 2).sum()
            metrics['出口商集中度(HHI)'] = round(hhi, 4)
            
            # CR4 - 前4大出口商的市场份额
            cr4 = market_shares.head(4).sum()
            metrics['前4大出口商份额(CR4)'] = f"{cr4*100:.1f}%"
    
    # 贸易多样性
    if 'goodsDesc' in df.columns:
        unique_products = df['goodsDesc'].nunique()
        metrics['产品多样性'] = unique_products
    
    # 平均单价
    if 'sumOfUsd' in df.columns and 'quantity' in df.columns:
        valid_data = df[(df['sumOfUsd'] > 0) & (df['quantity'] > 0)]
        if len(valid_data) > 0:
            avg_unit_price = valid_data['sumOfUsd'].sum() / valid_data['quantity'].sum()
            metrics['平均单价'] = f"${avg_unit_price:.2f}"
    
    # 贸易频率
    if 'date' in df.columns:
        dates = pd.to_datetime(df['date'])
        date_range = (dates.max() - dates.min()).days + 1
        if date_range > 0:
            trade_frequency = len(df) / date_range
            metrics['日均交易次数'] = round(trade_frequency, 2)
    
    # 国家多样性
    if 'countryOfOrigin' in df.columns:
        origin_countries = df['countryOfOrigin'].nunique()
        metrics['原产国数量'] = origin_countries
    
    if 'countryOfDestination' in df.columns:
        dest_countries = df['countryOfDestination'].nunique()
        metrics['目的国数量'] = dest_countries
    
    return metrics


# 预定义函数映射表
PREBUILT_FUNCTIONS = {
    'load_trade_data': load_trade_data,
    'optimize_dataframe_types': optimize_dataframe_types,
    'analyze_trade_trends': analyze_trade_trends,
    'top_importers': top_importers,
    'top_exporters': top_exporters,
    'analyze_product_categories': analyze_product_categories,
    'generate_summary_report': generate_summary_report,
    'trade_volume_by_country': trade_volume_by_country,
    'calculate_trade_metrics': calculate_trade_metrics,
    'plot_trade_timeline': plot_trade_timeline,
    'plot_top_products': plot_top_products,
}


def get_prebuilt_functions_code() -> str:
    """
    获取预定义函数的完整代码
    
    Returns:
        函数定义代码字符串
    """
    return '''
# === 贸易数据分析函数库 ===

import pandas as pd
import numpy as np
from io import StringIO

def load_trade_data(artifact_id):
    """从 Artifact 加载贸易数据为 DataFrame"""
    # 这个函数会被执行环境特殊处理
    pass

def analyze_trade_trends(df, period='month', value_col='sumOfUsd'):
    """分析贸易趋势"""
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'])
    
    if period == 'month':
        df_copy['period'] = df_copy['date'].dt.to_period('M')
    elif period == 'quarter':
        df_copy['period'] = df_copy['date'].dt.to_period('Q')
    elif period == 'year':
        df_copy['period'] = df_copy['date'].dt.year
    
    trends = df_copy.groupby('period').agg({
        value_col: ['sum', 'mean', 'count'],
        'quantity': 'sum'
    }).round(2)
    
    trends.columns = ['总额', '平均值', '交易次数', '总数量']
    return trends.reset_index()

def top_importers(df, top_n=10, value_col='sumOfUsd'):
    """分析最活跃的进口商"""
    importers = df.groupby('importer').agg({
        value_col: 'sum',
        'quantity': 'sum',
        'id': 'count'
    }).round(2)
    importers.columns = ['总交易额', '总数量', '交易次数']
    return importers.sort_values('总交易额', ascending=False).head(top_n).reset_index()

def top_exporters(df, top_n=10, value_col='sumOfUsd'):
    """分析最活跃的出口商"""
    exporters = df.groupby('exporter').agg({
        value_col: 'sum',
        'quantity': 'sum',
        'id': 'count'
    }).round(2)
    exporters.columns = ['总交易额', '总数量', '交易次数']
    return exporters.sort_values('总交易额', ascending=False).head(top_n).reset_index()

def generate_summary_report(df):
    """生成贸易数据摘要报告"""
    report = {}
    report['总记录数'] = len(df)
    if 'sumOfUsd' in df.columns:
        report['总交易额'] = f"${df['sumOfUsd'].sum():,.2f}"
        report['平均交易额'] = f"${df['sumOfUsd'].mean():,.2f}"
    if 'importer' in df.columns:
        report['不重复进口商数量'] = df['importer'].nunique()
    if 'exporter' in df.columns:
        report['不重复出口商数量'] = df['exporter'].nunique()
    return report

def analyze_product_categories(df, top_n=10):
    """分析产品类别"""
    product_columns = ['productDesc', 'goodsDesc', 'hsCode']
    product_col = None
    for col in product_columns:
        if col in df.columns:
            product_col = col
            break
    
    if not product_col:
        return pd.DataFrame()
    
    products = df.groupby(product_col).agg({
        'sumOfUsd': 'sum',
        'quantity': 'sum', 
        'id': 'count'
    }).round(2)
    
    products.columns = ['总交易额', '总数量', '交易次数']
    return products.sort_values('总交易额', ascending=False).head(top_n).reset_index()

def trade_volume_by_country(df, country_type='destination', top_n=10):
    """按国家分析贸易量"""
    if country_type == 'destination':
        country_col = 'countryOfDestination'
    elif country_type == 'origin':
        country_col = 'countryOfOrigin'
    else:
        raise ValueError("country_type 必须是 'destination' 或 'origin'")
    
    if country_col not in df.columns:
        return pd.DataFrame()
    
    countries = df.groupby(country_col).agg({
        'sumOfUsd': 'sum',
        'quantity': 'sum',
        'id': 'count'
    }).round(2)
    
    countries.columns = ['总交易额', '总数量', '交易次数']
    return countries.sort_values('总交易额', ascending=False).head(top_n).reset_index()

def calculate_trade_metrics(df):
    """计算高级贸易指标"""
    metrics = {}
    
    if 'exporter' in df.columns and 'sumOfUsd' in df.columns:
        exporter_values = df.groupby('exporter')['sumOfUsd'].sum().sort_values(ascending=False)
        total_value = exporter_values.sum()
        if total_value > 0:
            market_shares = exporter_values / total_value
            hhi = (market_shares ** 2).sum()
            metrics['出口商集中度(HHI)'] = round(hhi, 4)
            cr4 = market_shares.head(4).sum()
            metrics['前4大出口商份额(CR4)'] = f"{cr4*100:.1f}%"
    
    if 'goodsDesc' in df.columns:
        metrics['产品多样性'] = df['goodsDesc'].nunique()
    
    if 'sumOfUsd' in df.columns and 'quantity' in df.columns:
        valid_data = df[(df['sumOfUsd'] > 0) & (df['quantity'] > 0)]
        if len(valid_data) > 0:
            avg_unit_price = valid_data['sumOfUsd'].sum() / valid_data['quantity'].sum()
            metrics['平均单价'] = f"${avg_unit_price:.2f}"
    
    return metrics

print("✅ 贸易数据分析函数库已加载")
'''