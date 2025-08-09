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
} from 'antd';
import {
  UserOutlined,
  MailOutlined,
  PhoneOutlined,
  GlobalOutlined,
  ShoppingOutlined,
  DollarOutlined,
  CalendarOutlined,
  TeamOutlined,
  StarOutlined,
  HeartOutlined,
  HeartFilled,
  ContactsOutlined,
  HistoryOutlined,
} from '@ant-design/icons';
import type { Buyer } from '../../types';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

interface BuyerDetailModalProps {
  visible: boolean;
  buyer: Buyer | null;
  onClose: () => void;
  onContact?: (buyer: Buyer) => void;
  onFavorite?: (buyer: Buyer, favorited: boolean) => void;
}

const BuyerDetailModal: React.FC<BuyerDetailModalProps> = ({
  visible,
  buyer,
  onClose,
  onContact,
  onFavorite,
}) => {
  const [isFavorited, setIsFavorited] = useState(false);
  const [loading, setLoading] = useState(false);

  if (!buyer) return null;

  // 处理联系买家
  const handleContact = () => {
    setLoading(true);
    if (onContact) {
      onContact(buyer);
    }
    setTimeout(() => {
      setLoading(false);
      message.success('联系请求已发送！');
    }, 1000);
  };

  // 处理收藏/取消收藏
  const handleFavorite = () => {
    const newFavorited = !isFavorited;
    setIsFavorited(newFavorited);
    if (onFavorite) {
      onFavorite(buyer, newFavorited);
    }
    message.success(newFavorited ? '已收藏' : '已取消收藏');
  };

  // 获取国旗图标
  const getFlagUrl = (countryCode: string) => {
    return `https://flagcdn.com/w20/${countryCode.toLowerCase()}.png`;
  };

  // 获取公司规模描述
  const getCompanySizeDescription = (size: string) => {
    const descriptions = {
      small: '1-50人',
      medium: '51-200人',
      large: '201-1000人',
      enterprise: '1000+人',
    };
    return descriptions[size as keyof typeof descriptions] || size;
  };

  // 模拟的历史交易数据
  const transactionHistory = [
    {
      id: '1',
      date: '2024-01-15',
      product: '电子元器件',
      amount: '$150,000',
      status: '已完成',
    },
    {
      id: '2',
      date: '2023-11-20',
      product: '机械配件',
      amount: '$89,500',
      status: '已完成',
    },
    {
      id: '3',
      date: '2023-08-10',
      product: '纺织原料',
      amount: '$320,000',
      status: '已完成',
    },
  ];

  const transactionColumns = [
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date',
      width: 100,
    },
    {
      title: '产品类别',
      dataIndex: 'product',
      key: 'product',
    },
    {
      title: '交易金额',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount: string) => (
        <Text strong className="text-green-600">{amount}</Text>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color="green">{status}</Tag>
      ),
    },
  ];

  return (
    <Modal
      title={null}
      open={visible}
      onCancel={onClose}
      footer={null}
      width={900}
      bodyStyle={{ padding: 0 }}
      destroyOnClose
    >
      <div className="bg-white">
        {/* 头部信息 */}
        <div className="p-6 border-b bg-gradient-to-r from-blue-50 to-indigo-50">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
              <Avatar
                size={80}
                src={buyer.logo_url}
                icon={<UserOutlined />}
                className="border-4 border-white shadow-lg"
              />
              <div className="flex-1">
                <Title level={3} className="mb-2">
                  {buyer.company_name}
                </Title>
                <div className="flex items-center gap-3 mb-3">
                  <img
                    src={getFlagUrl(buyer.country_code || 'us')}
                    alt={buyer.country}
                    className="w-5 h-4 object-cover rounded-sm"
                  />
                  <Text className="text-gray-600">
                    {buyer.country} · {buyer.city}
                  </Text>
                </div>
                <div className="flex items-center gap-2 mb-3">
                  <Tag color="blue">{buyer.industry}</Tag>
                  <Tag color={buyer.company_size === 'enterprise' ? 'red' : 'default'}>
                    {getCompanySizeDescription(buyer.company_size)}
                  </Tag>
                  <div className="flex items-center gap-1">
                    <StarOutlined className="text-yellow-500" />
                    <span className="text-sm font-medium">
                      {buyer.credit_rating}/5
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Tooltip title={isFavorited ? '取消收藏' : '收藏买家'}>
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
                联系买家
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
                        <Text strong>{buyer.contact_person}</Text>
                      </div>
                      <div className="flex justify-between">
                        <Text type="secondary">职位:</Text>
                        <Text>{buyer.position || '采购经理'}</Text>
                      </div>
                      <div className="flex justify-between">
                        <Text type="secondary">年采购量:</Text>
                        <Text strong className="text-green-600">
                          ${buyer.annual_volume}
                        </Text>
                      </div>
                      <div className="flex justify-between">
                        <Text type="secondary">公司规模:</Text>
                        <Text>{getCompanySizeDescription(buyer.company_size)}</Text>
                      </div>
                    </div>
                  </Card>
                </Col>
                <Col span={12}>
                  <Card title="联系方式" size="small">
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <MailOutlined className="text-gray-400" />
                        <Text>{buyer.contact_info.email || '未公开'}</Text>
                      </div>
                      <div className="flex items-center gap-2">
                        <PhoneOutlined className="text-gray-400" />
                        <Text>{buyer.contact_info.phone || '未公开'}</Text>
                      </div>
                      <div className="flex items-center gap-2">
                        <GlobalOutlined className="text-gray-400" />
                        <Text>{buyer.contact_info.website || '未公开'}</Text>
                      </div>
                    </div>
                  </Card>
                </Col>
              </Row>

              <Divider />

              {/* 采购偏好 */}
              <Card title="采购偏好" size="small">
                <div className="mb-4">
                  <Text type="secondary" className="block mb-2">
                    感兴趣的产品类别:
                  </Text>
                  <div className="flex flex-wrap gap-2">
                    {buyer.products_interested?.map((product, index) => (
                      <Tag key={index} color="blue">
                        {product}
                      </Tag>
                    ))}
                  </div>
                </div>
                <div>
                  <Text type="secondary" className="block mb-2">
                    供应商认证要求:
                  </Text>
                  <div className="flex flex-wrap gap-2">
                    {buyer.certifications?.map((cert, index) => (
                      <Badge key={index} count={cert} color="green" />
                    ))}
                  </div>
                </div>
              </Card>
            </TabPane>

            {/* 信用评估 */}
            <TabPane tab="信用评估" key="credit">
              <Row gutter={24}>
                <Col span={8}>
                  <Card title="信用等级" size="small">
                    <div className="text-center">
                      <div className="mb-3">
                        <Rate
                          disabled
                          value={buyer.credit_rating}
                          className="text-2xl"
                        />
                      </div>
                      <Title level={4} className="text-blue-600">
                        {buyer.credit_rating}/5
                      </Title>
                      <Text type="secondary">
                        {buyer.credit_rating >= 4.5 ? '优秀' : 
                         buyer.credit_rating >= 4 ? '良好' : 
                         buyer.credit_rating >= 3 ? '一般' : '待观察'}
                      </Text>
                    </div>
                  </Card>
                </Col>
                <Col span={8}>
                  <Card title="匹配度" size="small">
                    <div className="text-center">
                      <Progress
                        type="circle"
                        percent={buyer.match_score}
                        status="active"
                        className="mb-3"
                      />
                      <div>
                        <Text strong>匹配度评分</Text>
                      </div>
                    </div>
                  </Card>
                </Col>
                <Col span={8}>
                  <Card title="优先级" size="small">
                    <div className="text-center">
                      <div className="mb-3">
                        <Tag
                          color={
                            buyer.priority === 'high' ? 'red' :
                            buyer.priority === 'medium' ? 'orange' : 'default'
                          }
                          className="text-lg px-4 py-2"
                        >
                          {buyer.priority === 'high' ? '高优先级' :
                           buyer.priority === 'medium' ? '中优先级' : '低优先级'}
                        </Tag>
                      </div>
                      <Text type="secondary">
                        基于AI分析推荐
                      </Text>
                    </div>
                  </Card>
                </Col>
              </Row>

              <Divider />

              {/* 评估指标 */}
              <Card title="详细评估" size="small">
                <Row gutter={16}>
                  <Col span={6}>
                    <div className="text-center mb-4">
                      <Text type="secondary">采购规模</Text>
                      <Progress percent={85} showInfo={false} />
                      <Text strong>85%</Text>
                    </div>
                  </Col>
                  <Col span={6}>
                    <div className="text-center mb-4">
                      <Text type="secondary">付款信用</Text>
                      <Progress percent={92} showInfo={false} />
                      <Text strong>92%</Text>
                    </div>
                  </Col>
                  <Col span={6}>
                    <div className="text-center mb-4">
                      <Text type="secondary">合作稳定性</Text>
                      <Progress percent={78} showInfo={false} />
                      <Text strong>78%</Text>
                    </div>
                  </Col>
                  <Col span={6}>
                    <div className="text-center mb-4">
                      <Text type="secondary">响应速度</Text>
                      <Progress percent={88} showInfo={false} />
                      <Text strong>88%</Text>
                    </div>
                  </Col>
                </Row>
              </Card>
            </TabPane>

            {/* 交易历史 */}
            <TabPane tab="交易历史" key="history">
              <Card title="近期交易记录" size="small">
                <Table
                  columns={transactionColumns}
                  dataSource={transactionHistory}
                  rowKey="id"
                  size="small"
                  pagination={false}
                />
              </Card>
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
              发起商务洽谈
            </Button>
          </Space>
        </div>
      </div>
    </Modal>
  );
};

export default BuyerDetailModal;