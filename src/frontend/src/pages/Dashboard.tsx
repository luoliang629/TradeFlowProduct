import { Card, Row, Col, Statistic, Typography, Space, Button } from 'antd';
import { 
  MessageOutlined,
  TeamOutlined,
  ShoppingOutlined,
  TrendingUpOutlined,
  PlusOutlined 
} from '@ant-design/icons';

const { Title, Text } = Typography;

const Dashboard: React.FC = () => {
  return (
    <div className="p-6 bg-gray-50 min-h-full">
      <div className="max-w-7xl mx-auto">
        {/* 页面标题 */}
        <div className="mb-6">
          <Title level={2} className="mb-2">
            工作台
          </Title>
          <Text className="text-gray-600">
            欢迎回来！这里是您的TradeFlow工作台概览。
          </Text>
        </div>

        {/* 统计数据卡片 */}
        <Row gutter={[16, 16]} className="mb-6">
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="本月对话"
                value={87}
                prefix={<MessageOutlined />}
                valueStyle={{ color: '#3f8600' }}
                suffix="次"
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="活跃客户"
                value={23}
                prefix={<TeamOutlined />}
                valueStyle={{ color: '#1890ff' }}
                suffix="家"
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="新增买家"
                value={12}
                prefix={<ShoppingOutlined />}
                valueStyle={{ color: '#722ed1' }}
                suffix="个"
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="匹配成功率"
                value={78.5}
                prefix={<TrendingUpOutlined />}
                valueStyle={{ color: '#f5222d' }}
                suffix="%"
              />
            </Card>
          </Col>
        </Row>

        {/* 快速操作 */}
        <Card className="mb-6">
          <Title level={4} className="mb-4">
            快速操作
          </Title>
          <Space size="middle" wrap>
            <Button type="primary" icon={<MessageOutlined />} size="large">
              开始新对话
            </Button>
            <Button icon={<PlusOutlined />} size="large">
              添加客户
            </Button>
            <Button icon={<ShoppingOutlined />} size="large">
              寻找买家
            </Button>
            <Button icon={<TeamOutlined />} size="large">
              供应商匹配
            </Button>
          </Space>
        </Card>

        {/* 最近活动 */}
        <Row gutter={16}>
          <Col xs={24} lg={12}>
            <Card title="最近对话" extra={<a href="/chat">查看全部</a>}>
              <div className="space-y-4">
                <div className="flex justify-between items-center py-2 border-b">
                  <div>
                    <Text strong>寻找电子产品买家</Text>
                    <br />
                    <Text className="text-gray-500 text-sm">2小时前</Text>
                  </div>
                  <Button size="small" type="link">
                    继续
                  </Button>
                </div>
                <div className="flex justify-between items-center py-2 border-b">
                  <div>
                    <Text strong>供应商质量评估</Text>
                    <br />
                    <Text className="text-gray-500 text-sm">5小时前</Text>
                  </div>
                  <Button size="small" type="link">
                    继续
                  </Button>
                </div>
                <div className="flex justify-between items-center py-2">
                  <div>
                    <Text strong>市场价格分析</Text>
                    <br />
                    <Text className="text-gray-500 text-sm">1天前</Text>
                  </div>
                  <Button size="small" type="link">
                    继续
                  </Button>
                </div>
              </div>
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="推荐买家" extra={<a href="/trade/buyers">查看全部</a>}>
              <div className="space-y-4">
                <div className="flex justify-between items-center py-2 border-b">
                  <div>
                    <Text strong>TechGlobal Solutions</Text>
                    <br />
                    <Text className="text-gray-500 text-sm">美国 · 消费电子</Text>
                  </div>
                  <Text className="text-green-600 font-medium">95%</Text>
                </div>
                <div className="flex justify-between items-center py-2 border-b">
                  <div>
                    <Text strong>EuroElectronics Ltd</Text>
                    <br />
                    <Text className="text-gray-500 text-sm">德国 · 电子零售</Text>
                  </div>
                  <Text className="text-green-600 font-medium">87%</Text>
                </div>
                <div className="flex justify-between items-center py-2">
                  <div>
                    <Text strong>AsiaTrading Co.</Text>
                    <br />
                    <Text className="text-gray-500 text-sm">新加坡 · 贸易公司</Text>
                  </div>
                  <Text className="text-green-600 font-medium">82%</Text>
                </div>
              </div>
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default Dashboard;