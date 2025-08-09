"""
演示供应商联系信息增强功能
展示如何使用系统找到具体供应商并获取联系信息
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from trade_flow.tools.contact_info_aggregator import contact_info_aggregator
from trade_flow.tools.contact_validator import validate_contact_info


async def demo_contact_extraction():
    """演示联系信息提取和验证功能"""
    
    print("=== TradeFlowAgent 供应商联系信息功能演示 ===\n")
    
    # 模拟从不同渠道获取的供应商信息
    print("📌 场景：用户查询 'LED灯供应商'")
    print("系统从多个渠道收集到以下信息：\n")
    
    # B2B平台数据
    b2b_data = {
        'supplier_name': '深圳光明电子有限公司',
        'contact': {
            'email': 'sales@brightled.cn',
            'phone': '+86-755-88886666',
            'whatsapp': '+86-13888888888'
        },
        'snippet': '专业LED灯制造商，10年出口经验，月产能100万件。联系人：王经理 WhatsApp: +86-13888888888'
    }
    
    # 企业信息数据
    company_data = {
        'name': '深圳光明电子有限公司',
        'email': 'info@brightled.cn',
        'phone': '0755-88886666',
        'address': '深圳市宝安区龙华新区工业园A栋',
        'website': 'www.brightled.cn',
        'contact_person': '王经理'
    }
    
    # 网页分析数据
    web_data = {
        'merchant_info': {
            'contact_info': {
                'emails': ['sales@brightled.cn', 'export@brightled.cn'],
                'phones': ['+86-755-88886666'],
                'whatsapp': '+86-13888888888',
                'wechat': 'LED_bright_2024',
                'address': '深圳市宝安区龙华新区工业园A栋3楼'
            }
        }
    }
    
    print("1️⃣ B2B平台（阿里巴巴）发现：")
    print(f"   - 公司：{b2b_data['supplier_name']}")
    print(f"   - 邮箱：{b2b_data['contact']['email']}")
    print(f"   - 电话：{b2b_data['contact']['phone']}")
    print(f"   - WhatsApp：{b2b_data['contact']['whatsapp']}\n")
    
    print("2️⃣ 企业信息查询结果：")
    print(f"   - 公司：{company_data['name']}")
    print(f"   - 邮箱：{company_data['email']}")
    print(f"   - 电话：{company_data['phone']}")
    print(f"   - 地址：{company_data['address']}\n")
    
    print("3️⃣ 网页深度分析发现：")
    print(f"   - 邮箱：{web_data['merchant_info']['contact_info']['emails']}")
    print(f"   - 微信：{web_data['merchant_info']['contact_info']['wechat']}\n")
    
    # 使用联系信息聚合器
    print("🔄 正在聚合和验证联系信息...\n")
    
    aggregated = await contact_info_aggregator(
        supplier_name='深圳光明电子有限公司',
        data_sources=[
            {'source_type': 'b2b', 'data': b2b_data, 'confidence': 0.9},
            {'source_type': 'company', 'data': company_data, 'confidence': 0.85},
            {'source_type': 'web', 'data': web_data, 'confidence': 0.7}
        ]
    )
    
    # 展示聚合结果
    print("✅ 聚合后的供应商联系信息：\n")
    print(f"🏢 **{aggregated['supplier_name']}**")
    print(f"   综合可信度：{aggregated['confidence_level']} ({aggregated['confidence_score']:.2f})\n")
    
    primary = aggregated['primary_contacts']
    print("📞 **主要联系方式**：")
    if 'email' in primary:
        print(f"   📧 邮箱：{primary['email']} (可信度: {primary['email_confidence']:.2f})")
    if 'phone' in primary:
        print(f"   📱 电话：{primary['phone']} (可信度: {primary['phone_confidence']:.2f})")
    if 'whatsapp' in primary:
        print(f"   💬 WhatsApp：{primary['whatsapp']} (可信度: {primary['whatsapp_confidence']:.2f})")
    if 'wechat' in primary:
        print(f"   💬 微信：{primary['wechat']} (可信度: {primary['wechat_confidence']:.2f})")
    if 'address' in primary:
        print(f"   🏢 地址：{primary['address']} (可信度: {primary['address_confidence']:.2f})")
    if 'website' in primary:
        print(f"   🌐 网站：{primary['website']} (可信度: {primary['website_confidence']:.2f})")
    if 'contact_person' in primary:
        print(f"   👤 联系人：{primary['contact_person']} (可信度: {primary['contact_person_confidence']:.2f})")
    
    # 验证联系信息
    print("\n🔍 验证联系信息有效性...\n")
    
    validation = await validate_contact_info(primary)
    
    print(f"验证结果：{validation['validation_level']} (整体有效性: {validation['overall_validity']:.2f})")
    
    # 显示验证细节
    if 'field_validations' in validation:
        print("\n验证细节：")
        for field, details in validation['field_validations'].items():
            status = "✅" if details['is_valid'] else "❌"
            print(f"   {status} {field}: ", end="")
            if details['is_valid']:
                print(f"有效 (可信度: {details['confidence']:.2f})")
            else:
                if details.get('warnings'):
                    print(f"无效 - {details['warnings'][0]}")
    
    # 行动建议
    print("\n💡 **行动建议**：")
    print("1. 优先通过 WhatsApp (+86-13888888888) 联系王经理，响应最快")
    print("2. 发送邮件至 sales@brightled.cn 获取产品目录和报价")
    print("3. 访问 www.brightled.cn 了解更多产品信息")
    print("4. 所有联系方式已通过多源验证，可信度高")
    
    print("\n✨ 演示完成！系统成功找到具体供应商并提供了完整的联系信息。")


if __name__ == "__main__":
    asyncio.run(demo_contact_extraction())