import React, { useState } from 'react';
import {
  Modal,
  Card,
  Avatar,
  Typography,
  Row,
  Col,
  Tag,
  Button,
  Space,
  Divider,
  Tabs,
  Table,
  Rate,
  Progress,
  Badge,
  Tooltip,
  message,
  Image,
} from 'antd';
import {
  ShopOutlined,
  MailOutlined,
  PhoneOutlined,
  GlobalOutlined,
  ToolOutlined,
  DollarOutlined,
  CalendarOutlined,
  TeamOutlined,
  StarOutlined,
  HeartOutlined,
  HeartFilled,
  ContactsOutlined,
  SafetyCertificateOutlined,
  CrownOutlined,
  ExportOutlined,
} from '@ant-design/icons';
import type { Supplier } from '../../types';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

interface SupplierDetailModalProps {
  visible: boolean;
  supplier: Supplier | null;
  onClose: () => void;
  onContact?: (supplier: Supplier) => void;
  onFavorite?: (supplier: Supplier, favorited: boolean) => void;
}

const SupplierDetailModal: React.FC<SupplierDetailModalProps> = ({
  visible,
  supplier,
  onClose,
  onContact,
  onFavorite,
}) => {
  const [isFavorited, setIsFavorited] = useState(false);
  const [loading, setLoading] = useState(false);

  if (!supplier) return null;

  // 处理联系供应商
  const handleContact = () => {
    setLoading(true);
    if (onContact) {
      onContact(supplier);
    }
    setTimeout(() => {
      setLoading(false);
      message.success('询价请求已发送！');
    }, 1000);
  };

  // 处理收藏/取消收藏
  const handleFavorite = () => {
    const newFavorited = !isFavorited;
    setIsFavorited(newFavorited);
    if (onFavorite) {
      onFavorite(supplier, newFavorited);
    }
    message.success(newFavorited ? '已收藏' : '已取消收藏');
  };

  // 获取国旗图标
  const getFlagUrl = (countryCode: string) => {
    return `https://flagcdn.com/w20/${countryCode.toLowerCase()}.png`;
  };

  // 获取供应商等级图标和颜色
  const getSupplierLevelInfo = (level: string) => {
    const levelInfo = {
      gold: { icon: <CrownOutlined />, color: '#faad14', text: '金牌供应商' },
      silver: { icon: <SafetyCertificateOutlined />, color: '#d9d9d9', text: '银牌供应商' },
      bronze: { icon: <SafetyCertificateOutlined />, color: '#d4b106', text: '铜牌供应商' },
      verified: { icon: <SafetyCertificateOutlined />, color: '#52c41a', text: '认证供应商' },
    };
    return levelInfo[level as keyof typeof levelInfo] || levelInfo.verified;
  };

  // 模拟的产品展示数据
  const productShowcase = [
    {
      id: '1',
      name: '电子元器件',
      image: 'https://via.placeholder.com/150',
      price: '$0.5-2.0',
      moq: '1000 PCS',
    },
    {
      id: '2',
      name: '机械配件',
      image: 'https://via.placeholder.com/150',
      price: '$10-50',
      moq: '100 PCS',
    },
    {
      id: '3',
      name: '塑料制品',
      image: 'https://via.placeholder.com/150',
      price: '$2-15',
      moq: '500 PCS',
    },
  ];

  // 模拟的客户评价
  const customerReviews = [
    {
      id: '1',
      customer: 'ABC Electronics',
      rating: 5,
      comment: '产品质量优秀，交期准时，合作愉快！',
      date: '2024-01-15',
    },
    {
      id: '2',
      customer: 'Tech Solutions Inc',
      rating: 4,
      comment: '价格合理，服务态度好，推荐合作。',
      date: '2023-12-08',
    },
    {
      id: '3',
      customer: 'Global Trading Co',
      rating: 5,
      comment: '专业的供应商，产品符合国际标准。',
      date: '2023-11-22',
    },
  ];

  const reviewColumns = [
    {
      title: '客户',
      dataIndex: 'customer',
      key: 'customer',
      width: 150,
    },
    {
      title: '评分',
      dataIndex: 'rating',
      key: 'rating',
      width: 120,
      render: (rating: number) => (
        <Rate disabled value={rating} className="text-sm" />
      ),
    },
    {
      title: '评价',
      dataIndex: 'comment',
      key: 'comment',
    },
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date',
      width: 100,
    },
  ];

  const levelInfo = getSupplierLevelInfo(supplier.level);

  return (
    <Modal
      title={null}
      open={visible}
      onCancel={onClose}
      footer={null}
      width={1000}
      bodyStyle={{ padding: 0 }}
      destroyOnClose
    >
      <div className="bg-white">
        {/* 头部信息 */}
        <div className="p-6 border-b bg-gradient-to-r from-green-50 to-blue-50">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
              <Avatar
                size={80}
                src={supplier.logo_url}
                icon={<ShopOutlined />}
                className="border-4 border-white shadow-lg"
              />
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <Title level={3} className="mb-0">
                    {supplier.company_name}
                  </Title>
                  <Tooltip title={levelInfo.text}>
                    <Tag color={levelInfo.color} icon={levelInfo.icon}>
                      {levelInfo.text}
                    </Tag>
                  </Tooltip>
                </div>
                <div className="flex items-center gap-3 mb-3">
                  <img
                    src={getFlagUrl(supplier.country_code || 'cn')}
                    alt={supplier.country}
                    className="w-5 h-4 object-cover rounded-sm"
                  />
                  <Text className="text-gray-600">
                    {supplier.country} · {supplier.city}
                  </Text>
                  <Text type="secondary">
                    成立于 {supplier.established_year}年
                  </Text>
                </div>
                <div className="flex items-center gap-3 mb-3">
                  <div className="flex items-center gap-1">
                    <Rate disabled value={supplier.rating} className="text-sm" />
                    <span className="text-sm font-medium ml-1">
                      {supplier.rating}/5 ({supplier.review_count}评价)
                    </span>
                  </div>
                  <Text type="secondary">
                    员工 {supplier.employee_count}人
                  </Text>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Tooltip title={isFavorited ? '取消收藏' : '收藏供应商'}>
                <Button
                  icon={isFavorited ? <HeartFilled /> : <HeartOutlined />}
                  onClick={handleFavorite}
                  className={isFavorited ? 'text-red-500 border-red-500' : ''}
                >
                  {isFavorited ? '已收藏' : '收藏'}
                </Button>
              </Tooltip>
              <Button
                type="primary"
                icon={<MailOutlined />}
                loading={loading}
                onClick={handleContact}
              >
                立即询价
              </Button>
            </div>
          </div>
        </div>

        {/* 详细信息标签页 */}
        <div className="p-6">
          <Tabs defaultActiveKey="basic">
            {/* 基本信息 */}
            <TabPane tab="基本信息" key="basic">
              <Row gutter={24}>
                <Col span={12}>
                  <Card title="公司信息" size="small">
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <Text type="secondary">联系人:</Text>
                        <Text strong>{supplier.contact_person}</Text>
                      </div>
                      <div className="flex justify-between">
                        <Text type="secondary">职位:</Text>
                        <Text>{supplier.position || '销售经理'}</Text>
                      </div>
                      <div className="flex justify-between">
                        <Text type="secondary">成立年份:</Text>
                        <Text>{supplier.established_year}年</Text>
                      </div>
                      <div className="flex justify-between">
                        <Text type="secondary">员工规模:</Text>
                        <Text>{supplier.employee_count}人</Text>
                      </div>
                      <div className="flex justify-between">
                        <Text type="secondary">最小起订:</Text>
                        <Text strong className="text-orange-600">
                          {supplier.min_order}
                        </Text>
                      </div>
                    </div>
                  </Card>
                </Col>
                <Col span={12}>
                  <Card title="联系方式" size="small">
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <MailOutlined className="text-gray-400" />
                        <Text>{supplier.contact_info.email || '未公开'}</Text>
                      </div>
                      <div className="flex items-center gap-2">
                        <PhoneOutlined className="text-gray-400" />
                        <Text>{supplier.contact_info.phone || '未公开'}</Text>
                      </div>
                      <div className="flex items-center gap-2">
                        <GlobalOutlined className="text-gray-400" />
                        <Text>{supplier.contact_info.website || '未公开'}</Text>
                      </div>
                    </div>
                  </Card>
                </Col>
              </Row>

              <Divider />

              {/* 主营产品 */}
              <Card title="主营产品" size="small">
                <div className="flex flex-wrap gap-2 mb-4">
                  {supplier.main_products?.map((product, index) => (
                    <Tag key={index} color="blue" className="mb-2">
                      {product}
                    </Tag>
                  ))}
                </div>
              </Card>

              {/* 认证资质 */}
              <Card title="认证资质" size="small">
                <div className="flex flex-wrap gap-2">
                  {supplier.certifications?.map((cert, index) => (
                    <Badge key={index} count={cert} color="green" />
                  ))}
                </div>
              </Card>
            </TabPane>

            {/* 贸易能力 */}
            <TabPane tab="贸易能力" key="trade">
              <Row gutter={24}>
                <Col span={8}>
                  <Card title="出口比例" size="small">
                    <div className="text-center">
                      <Progress
                        type="circle"
                        percent={supplier.trade_capacity.export_percentage}
                        format={percent => `${percent}%`}
                        className="mb-3"
                      />
                      <Text strong>出口占比</Text>
                    </div>
                  </Card>
                </Col>
                <Col span={8}>
                  <Card title="年销售额" size="small">
                    <div className="text-center">
                      <Title level={3} className="text-green-600 mb-3">
                        ${supplier.trade_capacity.annual_sales}
                      </Title>
                      <Text strong>年度销售</Text>
                    </div>
                  </Card>
                </Col>
                <Col span={8}>
                  <Card title="供应商等级" size="small">
                    <div className="text-center">
                      <div className="mb-3 text-4xl" style={{ color: levelInfo.color }}>
                        {levelInfo.icon}
                      </div>
                      <Text strong>{levelInfo.text}</Text>
                    </div>
                  </Card>
                </Col>
              </Row>

              <Divider />

              {/* 主要市场 */}
              <Card title="主要出口市场" size="small">
                <div className="flex flex-wrap gap-2">
                  {supplier.trade_capacity.main_markets?.map((market, index) => (
                    <Tag key={index} color="gold">
                      {market}
                    </Tag>
                  ))}
                </div>
              </Card>
            </TabPane>

            {/* 产品展示 */}
            <TabPane tab="产品展示" key="products">
              <div className="grid grid-cols-3 gap-4">
                {productShowcase.map((product) => (
                  <Card key={product.id} size="small" hoverable>
                    <Image
                      src={product.image}
                      alt={product.name}
                      className="w-full h-32 object-cover mb-3 rounded"
                    />
                    <Title level={5} className="mb-2">
                      {product.name}
                    </Title>
                    <div className="flex justify-between items-center">
                      <Text strong className="text-green-600">
                        {product.price}
                      </Text>
                      <Text type="secondary" className="text-sm">
                        起订: {product.moq}
                      </Text>
                    </div>
                  </Card>
                ))}
              </div>
            </TabPane>

            {/* 客户评价 */}
            <TabPane tab="客户评价" key="reviews">
              <Table
                columns={reviewColumns}
                dataSource={customerReviews}
                rowKey="id"
                size="small"
                pagination={false}
              />
            </TabPane>
          </Tabs>
        </div>

        {/* 底部操作栏 */}
        <div className="px-6 py-4 border-t bg-gray-50 flex justify-between">
          <Space>
            <Text type="secondary">
              最后更新: {new Date().toLocaleDateString()}
            </Text>
          </Space>
          <Space>
            <Button onClick={onClose}>
              关闭
            </Button>
            <Button
              type="primary"
              icon={<ContactsOutlined />}
              loading={loading}
              onClick={handleContact}
            >
              发送询价单
            </Button>
          </Space>
        </div>
      </div>
    </Modal>
  );
};

export default SupplierDetailModal;