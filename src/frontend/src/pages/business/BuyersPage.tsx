import React, { useState, useEffect } from 'react';
import {
  Layout,
  Card,
  Table,
  Button,
  Input,
  Select,
  Space,
  Tag,
  Avatar,
  Typography,
  Row,
  Col,
  Statistic,
  message,
  Spin,
  Empty,
  Tooltip,
  Badge,
} from 'antd';
import {
  SearchOutlined,
  FilterOutlined,
  ExportOutlined,
  UserOutlined,
  GlobalOutlined,
  ShoppingOutlined,
  DollarOutlined,
  RiseOutlined,
  EyeOutlined,
  HeartOutlined,
  MailOutlined,
  PhoneOutlined,
  StarOutlined,
} from '@ant-design/icons';
import { useAppSelector } from '../../store/hooks';
import { apiService } from '../../services';
import type { Buyer } from '../../types';

const { Content } = Layout;
const { Title, Text } = Typography;
const { Search } = Input;
const { Option } = Select;

interface BuyerSearchParams {
  keyword?: string;
  country?: string;
  industry?: string;
  company_size?: string;
  annual_volume?: string;
  certification?: string;
  page?: number;
  page_size?: number;
}

const BuyersPage: React.FC = () => {
  const { user } = useAppSelector(state => state.auth);
  const [loading, setLoading] = useState(false);
  const [buyers, setBuyers] = useState<Buyer[]>([]);
  const [total, setTotal] = useState(0);
  const [statistics, setStatistics] = useState({
    totalBuyers: 0,
    activeBuyers: 0,
    topCountries: [] as { country: string; count: number }[],
    topIndustries: [] as { industry: string; count: number }[],
  });
  
  // 搜索和筛选参数
  const [searchParams, setSearchParams] = useState<BuyerSearchParams>({
    page: 1,
    page_size: 20,
  });

  // 加载买家数据
  const loadBuyers = async (params: BuyerSearchParams = searchParams) => {
    setLoading(true);
    try {
      const response = await apiService.buyers.search(params);
      if (response.success) {
        setBuyers(response.data?.buyers || []);
        setTotal(response.data?.total || 0);
        
        // 加载统计数据
        if (params.page === 1) {
          loadStatistics();
        }
      }
    } catch (error) {
      console.error('加载买家数据失败:', error);
      message.error('加载买家数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载统计数据
  const loadStatistics = async () => {
    try {
      const response = await apiService.buyers.getStatistics();
      if (response.success) {
        setStatistics(response.data || {});
      }
    } catch (error) {
      console.error('加载统计数据失败:', error);
    }
  };

  // 处理搜索
  const handleSearch = (keyword: string) => {
    const params = { ...searchParams, keyword, page: 1 };
    setSearchParams(params);
    loadBuyers(params);
  };

  // 处理筛选
  const handleFilter = (field: keyof BuyerSearchParams, value: any) => {
    const params = { ...searchParams, [field]: value, page: 1 };
    setSearchParams(params);
    loadBuyers(params);
  };

  // 处理分页
  const handlePageChange = (page: number, pageSize?: number) => {
    const params = { 
      ...searchParams, 
      page, 
      page_size: pageSize || searchParams.page_size 
    };
    setSearchParams(params);
    loadBuyers(params);
  };

  // 查看买家详情
  const viewBuyerDetail = (buyer: Buyer) => {
    // TODO: 打开买家详情弹窗或跳转详情页
    message.info(`查看买家详情: ${buyer.company_name}`);
  };

  // 联系买家
  const contactBuyer = (buyer: Buyer) => {
    message.success(`已发起对 ${buyer.company_name} 的联系请求`);
  };

  // 收藏买家
  const favoriteBuyer = (buyer: Buyer) => {
    message.success(`已收藏 ${buyer.company_name}`);
  };

  // 导出买家列表
  const exportBuyers = () => {
    message.info('买家列表导出功能开发中...');
  };

  // 获取国旗图标
  const getFlagUrl = (countryCode: string) => {
    return `https://flagcdn.com/w20/${countryCode.toLowerCase()}.png`;
  };

  // 获取公司规模标签颜色
  const getCompanySizeColor = (size: string) => {
    const colorMap: { [key: string]: string } = {
      'small': 'green',
      'medium': 'blue',
      'large': 'orange',
      'enterprise': 'red',
    };
    return colorMap[size] || 'default';
  };

  // 表格列定义
  const columns = [
    {
      title: '公司信息',
      key: 'company',
      width: 300,
      render: (record: Buyer) => (
        <div className="flex items-start gap-3">
          <Avatar 
            size={48} 
            src={record.logo_url} 
            icon={<UserOutlined />}
            className="flex-shrink-0"
          />
          <div className="flex-1 min-w-0">
            <div className="font-semibold text-gray-900 mb-1 truncate">
              {record.company_name}
            </div>
            <div className="text-sm text-gray-600 mb-1">
              {record.contact_person} · {record.position}
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <img 
                src={getFlagUrl(record.country_code || 'us')} 
                alt={record.country}
                className="w-4 h-3 object-cover rounded-sm"
              />
              <span>{record.country}</span>
              <span>·</span>
              <span>{record.city}</span>
            </div>
          </div>
        </div>
      ),
    },
    {
      title: '行业领域',
      dataIndex: 'industry',
      key: 'industry',
      width: 120,
      render: (industry: string) => (
        <Tag color="blue" className="text-xs">
          {industry}
        </Tag>
      ),
    },
    {
      title: '公司规模',
      dataIndex: 'company_size',
      key: 'company_size',
      width: 100,
      render: (size: string) => (
        <Tag color={getCompanySizeColor(size)} className="text-xs">
          {size === 'small' ? '小型' : 
           size === 'medium' ? '中型' : 
           size === 'large' ? '大型' : '企业级'}
        </Tag>
      ),
    },
    {
      title: '年采购量',
      dataIndex: 'annual_volume',
      key: 'annual_volume',
      width: 120,
      render: (volume: string) => (
        <div className="text-right">
          <Text strong className="text-green-600">${volume}</Text>
        </div>
      ),
    },
    {
      title: '信用等级',
      dataIndex: 'credit_rating',
      key: 'credit_rating',
      width: 100,
      render: (rating: number) => (
        <div className="flex items-center gap-1">
          <StarOutlined className="text-yellow-500" />
          <span className="text-sm font-medium">{rating}/5</span>
        </div>
      ),
    },
    {
      title: '认证状态',
      dataIndex: 'certifications',
      key: 'certifications',
      width: 120,
      render: (certifications: string[]) => (
        <div className="flex flex-wrap gap-1">
          {certifications?.slice(0, 2).map((cert, index) => (
            <Badge key={index} count={cert} showZero={false} color="green" />
          ))}
          {certifications?.length > 2 && (
            <Badge count={`+${certifications.length - 2}`} color="gray" />
          )}
        </div>
      ),
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (record: Buyer) => (
        <Space>
          <Tooltip title="查看详情">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => viewBuyerDetail(record)}
            />
          </Tooltip>
          <Tooltip title="联系买家">
            <Button
              type="text"
              size="small"
              icon={<MailOutlined />}
              onClick={() => contactBuyer(record)}
            />
          </Tooltip>
          <Tooltip title="收藏">
            <Button
              type="text"
              size="small"
              icon={<HeartOutlined />}
              onClick={() => favoriteBuyer(record)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  useEffect(() => {
    loadBuyers();
  }, []);

  return (
    <Content className="p-6 bg-gray-50 min-h-full">
      {/* 页面标题 */}
      <div className="mb-6">
        <Title level={2} className="mb-2">
          <ShoppingOutlined className="mr-2" />
          全球买家推荐
        </Title>
        <Text type="secondary">
          基于AI分析的精准买家匹配，帮您找到优质采购商
        </Text>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} className="mb-6">
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="总买家数"
              value={statistics.totalBuyers}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="活跃买家"
              value={statistics.activeBuyers}
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="覆盖国家"
              value={statistics.topCountries?.length || 0}
              prefix={<GlobalOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="行业领域"
              value={statistics.topIndustries?.length || 0}
              prefix={<FilterOutlined />}
              valueStyle={{ color: '#f5222d' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 搜索和筛选区域 */}
      <Card className="mb-6">
        <Row gutter={16} align="middle">
          <Col xs={24} md={8}>
            <Search
              placeholder="搜索公司名称、联系人..."
              allowClear
              onSearch={handleSearch}
              className="w-full"
            />
          </Col>
          <Col xs={12} md={4}>
            <Select
              placeholder="选择国家"
              allowClear
              className="w-full"
              onChange={(value) => handleFilter('country', value)}
            >
              <Option value="US">美国</Option>
              <Option value="DE">德国</Option>
              <Option value="UK">英国</Option>
              <Option value="FR">法国</Option>
              <Option value="JP">日本</Option>
              <Option value="KR">韩国</Option>
            </Select>
          </Col>
          <Col xs={12} md={4}>
            <Select
              placeholder="选择行业"
              allowClear
              className="w-full"
              onChange={(value) => handleFilter('industry', value)}
            >
              <Option value="Electronics">电子产品</Option>
              <Option value="Machinery">机械设备</Option>
              <Option value="Textiles">纺织服装</Option>
              <Option value="Chemicals">化工原料</Option>
              <Option value="Automotive">汽车配件</Option>
            </Select>
          </Col>
          <Col xs={12} md={4}>
            <Select
              placeholder="公司规模"
              allowClear
              className="w-full"
              onChange={(value) => handleFilter('company_size', value)}
            >
              <Option value="small">小型企业</Option>
              <Option value="medium">中型企业</Option>
              <Option value="large">大型企业</Option>
              <Option value="enterprise">企业集团</Option>
            </Select>
          </Col>
          <Col xs={12} md={4}>
            <Button
              type="primary"
              icon={<ExportOutlined />}
              onClick={exportBuyers}
              className="w-full"
            >
              导出列表
            </Button>
          </Col>
        </Row>
      </Card>

      {/* 买家列表 */}
      <Card>
        <div className="flex justify-between items-center mb-4">
          <div>
            <Text strong>找到 {total} 个匹配的买家</Text>
            {searchParams.keyword && (
              <Text type="secondary" className="ml-2">
                关键词: "{searchParams.keyword}"
              </Text>
            )}
          </div>
        </div>

        <Table
          columns={columns}
          dataSource={buyers}
          rowKey="id"
          loading={loading}
          pagination={{
            current: searchParams.page,
            pageSize: searchParams.page_size,
            total: total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
            onChange: handlePageChange,
            onShowSizeChange: handlePageChange,
          }}
          scroll={{ x: 1200 }}
          locale={{
            emptyText: (
              <Empty
                image={<UserOutlined className="text-4xl text-gray-400" />}
                description="暂无买家数据"
              />
            ),
          }}
        />
      </Card>
    </Content>
  );
};

export default BuyersPage;