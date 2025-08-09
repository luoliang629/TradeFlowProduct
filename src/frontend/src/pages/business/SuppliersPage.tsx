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
  Rate,
} from 'antd';
import {
  SearchOutlined,
  FilterOutlined,
  ExportOutlined,
  ShopOutlined,
  GlobalOutlined,
  ToolOutlined,
  DollarOutlined,
  RiseOutlined,
  EyeOutlined,
  HeartOutlined,
  MailOutlined,
  PhoneOutlined,
  SafetyCertificateOutlined,
  CrownOutlined,
} from '@ant-design/icons';
import { useAppSelector } from '../../store/hooks';
import { apiService } from '../../services';
import type { Supplier } from '../../types';

const { Content } = Layout;
const { Title, Text } = Typography;
const { Search } = Input;
const { Option } = Select;

interface SupplierSearchParams {
  keyword?: string;
  country?: string;
  industry?: string;
  company_size?: string;
  min_order?: string;
  certification?: string;
  page?: number;
  page_size?: number;
}

const SuppliersPage: React.FC = () => {
  const { user } = useAppSelector(state => state.auth);
  const [loading, setLoading] = useState(false);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [total, setTotal] = useState(0);
  const [statistics, setStatistics] = useState({
    totalSuppliers: 0,
    verifiedSuppliers: 0,
    topCountries: [] as { country: string; count: number }[],
    topCategories: [] as { category: string; count: number }[],
  });
  
  // 搜索和筛选参数
  const [searchParams, setSearchParams] = useState<SupplierSearchParams>({
    page: 1,
    page_size: 20,
  });

  // 加载供应商数据
  const loadSuppliers = async (params: SupplierSearchParams = searchParams) => {
    setLoading(true);
    try {
      const response = await apiService.suppliers.search(params);
      if (response.success) {
        setSuppliers(response.data?.suppliers || []);
        setTotal(response.data?.total || 0);
        
        // 加载统计数据
        if (params.page === 1) {
          loadStatistics();
        }
      }
    } catch (error) {
      console.error('加载供应商数据失败:', error);
      message.error('加载供应商数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载统计数据
  const loadStatistics = async () => {
    try {
      const response = await apiService.suppliers.getStatistics();
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
    loadSuppliers(params);
  };

  // 处理筛选
  const handleFilter = (field: keyof SupplierSearchParams, value: any) => {
    const params = { ...searchParams, [field]: value, page: 1 };
    setSearchParams(params);
    loadSuppliers(params);
  };

  // 处理分页
  const handlePageChange = (page: number, pageSize?: number) => {
    const params = { 
      ...searchParams, 
      page, 
      page_size: pageSize || searchParams.page_size 
    };
    setSearchParams(params);
    loadSuppliers(params);
  };

  // 查看供应商详情
  const viewSupplierDetail = (supplier: Supplier) => {
    // TODO: 打开供应商详情弹窗或跳转详情页
    message.info(`查看供应商详情: ${supplier.company_name}`);
  };

  // 联系供应商
  const contactSupplier = (supplier: Supplier) => {
    message.success(`已发起对 ${supplier.company_name} 的询价请求`);
  };

  // 收藏供应商
  const favoriteSupplier = (supplier: Supplier) => {
    message.success(`已收藏 ${supplier.company_name}`);
  };

  // 导出供应商列表
  const exportSuppliers = () => {
    message.info('供应商列表导出功能开发中...');
  };

  // 获取国旗图标
  const getFlagUrl = (countryCode: string) => {
    return `https://flagcdn.com/w20/${countryCode.toLowerCase()}.png`;
  };

  // 获取供应商等级颜色
  const getSupplierLevelColor = (level: string) => {
    const colorMap: { [key: string]: string } = {
      'gold': '#faad14',
      'silver': '#d9d9d9',
      'bronze': '#d4b106',
      'verified': '#52c41a',
    };
    return colorMap[level] || '#d9d9d9';
  };

  // 获取供应商等级图标
  const getSupplierLevelIcon = (level: string) => {
    switch (level) {
      case 'gold':
        return <CrownOutlined style={{ color: '#faad14' }} />;
      case 'verified':
        return <SafetyCertificateOutlined style={{ color: '#52c41a' }} />;
      default:
        return <SafetyCertificateOutlined />;
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '供应商信息',
      key: 'company',
      width: 300,
      render: (record: Supplier) => (
        <div className="flex items-start gap-3">
          <Avatar 
            size={48} 
            src={record.logo_url} 
            icon={<ShopOutlined />}
            className="flex-shrink-0"
          />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="font-semibold text-gray-900 truncate">
                {record.company_name}
              </span>
              {record.level && (
                <Tooltip title={`${record.level}级供应商`}>
                  {getSupplierLevelIcon(record.level)}
                </Tooltip>
              )}
            </div>
            <div className="text-sm text-gray-600 mb-1">
              {record.contact_person} · {record.position}
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <img 
                src={getFlagUrl(record.country_code || 'cn')} 
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
      title: '主营产品',
      dataIndex: 'main_products',
      key: 'main_products',
      width: 200,
      render: (products: string[]) => (
        <div className="flex flex-wrap gap-1">
          {products?.slice(0, 2).map((product, index) => (
            <Tag key={index} color="blue" className="text-xs mb-1">
              {product}
            </Tag>
          ))}
          {products?.length > 2 && (
            <Tag color="default" className="text-xs">
              +{products.length - 2}
            </Tag>
          )}
        </div>
      ),
    },
    {
      title: '成立年份',
      dataIndex: 'established_year',
      key: 'established_year',
      width: 100,
      render: (year: number) => (
        <Text className="text-sm">{year}年</Text>
      ),
    },
    {
      title: '员工数量',
      dataIndex: 'employee_count',
      key: 'employee_count',
      width: 100,
      render: (count: string) => (
        <Text className="text-sm">{count}人</Text>
      ),
    },
    {
      title: '最小起订量',
      dataIndex: 'min_order',
      key: 'min_order',
      width: 120,
      render: (minOrder: string) => (
        <Text strong className="text-orange-600">{minOrder}</Text>
      ),
    },
    {
      title: '供应商评级',
      key: 'rating',
      width: 120,
      render: (record: Supplier) => (
        <div className="text-center">
          <Rate 
            disabled 
            defaultValue={record.rating} 
            className="text-xs"
            style={{ fontSize: 12 }}
          />
          <div className="text-xs text-gray-500 mt-1">
            {record.rating}/5 ({record.review_count}评价)
          </div>
        </div>
      ),
    },
    {
      title: '认证资质',
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
      render: (record: Supplier) => (
        <Space>
          <Tooltip title="查看详情">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => viewSupplierDetail(record)}
            />
          </Tooltip>
          <Tooltip title="询价">
            <Button
              type="text"
              size="small"
              icon={<MailOutlined />}
              onClick={() => contactSupplier(record)}
            />
          </Tooltip>
          <Tooltip title="收藏">
            <Button
              type="text"
              size="small"
              icon={<HeartOutlined />}
              onClick={() => favoriteSupplier(record)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  useEffect(() => {
    loadSuppliers();
  }, []);

  return (
    <Content className="p-6 bg-gray-50 min-h-full">
      {/* 页面标题 */}
      <div className="mb-6">
        <Title level={2} className="mb-2">
          <ToolOutlined className="mr-2" />
          全球供应商搜索
        </Title>
        <Text type="secondary">
          海量优质供应商资源，智能匹配您的采购需求
        </Text>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} className="mb-6">
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="总供应商数"
              value={statistics.totalSuppliers}
              prefix={<ShopOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="认证供应商"
              value={statistics.verifiedSuppliers}
              prefix={<SafetyCertificateOutlined />}
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
              title="产品类目"
              value={statistics.topCategories?.length || 0}
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
              placeholder="搜索供应商、产品..."
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
              <Option value="CN">中国</Option>
              <Option value="IN">印度</Option>
              <Option value="TR">土耳其</Option>
              <Option value="VN">越南</Option>
              <Option value="TH">泰国</Option>
              <Option value="ID">印尼</Option>
            </Select>
          </Col>
          <Col xs={12} md={4}>
            <Select
              placeholder="产品类目"
              allowClear
              className="w-full"
              onChange={(value) => handleFilter('industry', value)}
            >
              <Option value="Electronics">电子产品</Option>
              <Option value="Machinery">机械设备</Option>
              <Option value="Textiles">纺织服装</Option>
              <Option value="Chemicals">化工原料</Option>
              <Option value="Home&Garden">家居园艺</Option>
            </Select>
          </Col>
          <Col xs={12} md={4}>
            <Select
              placeholder="认证类型"
              allowClear
              className="w-full"
              onChange={(value) => handleFilter('certification', value)}
            >
              <Option value="ISO9001">ISO9001</Option>
              <Option value="CE">CE认证</Option>
              <Option value="ROHS">ROHS认证</Option>
              <Option value="FCC">FCC认证</Option>
              <Option value="FDA">FDA认证</Option>
            </Select>
          </Col>
          <Col xs={12} md={4}>
            <Button
              type="primary"
              icon={<ExportOutlined />}
              onClick={exportSuppliers}
              className="w-full"
            >
              导出列表
            </Button>
          </Col>
        </Row>
      </Card>

      {/* 供应商列表 */}
      <Card>
        <div className="flex justify-between items-center mb-4">
          <div>
            <Text strong>找到 {total} 个匹配的供应商</Text>
            {searchParams.keyword && (
              <Text type="secondary" className="ml-2">
                关键词: "{searchParams.keyword}"
              </Text>
            )}
          </div>
        </div>

        <Table
          columns={columns}
          dataSource={suppliers}
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
                image={<ShopOutlined className="text-4xl text-gray-400" />}
                description="暂无供应商数据"
              />
            ),
          }}
        />
      </Card>
    </Content>
  );
};

export default SuppliersPage;