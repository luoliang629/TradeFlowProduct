import { Typography } from 'antd';
import { Outlet, useLocation } from 'react-router-dom';

const { Title, Text } = Typography;

const TradePage: React.FC = () => {
  const location = useLocation();
  
  // 如果在子路由，显示子路由内容
  if (location.pathname !== '/trade') {
    return <Outlet />;
  }

  return (
    <div className="p-6 bg-gray-50 min-h-full">
      <div className="max-w-4xl mx-auto">
        <Title level={2} className="mb-4">
          贸易业务
        </Title>
        <Text className="text-gray-600">
          管理您的贸易业务，包括买家开发、供应商管理、产品管理和订单跟踪。
        </Text>
        
        {/* 业务模块导航 */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 bg-white rounded-lg border border-gray-200">
            <Title level={4}>买家开发</Title>
            <Text className="text-gray-600">
              使用AI助手找到匹配的买家，生成联系方案。
            </Text>
          </div>
          
          <div className="p-6 bg-white rounded-lg border border-gray-200">
            <Title level={4}>供应商管理</Title>
            <Text className="text-gray-600">
              搜索和评估供应商，进行供应商对比分析。
            </Text>
          </div>
          
          <div className="p-6 bg-white rounded-lg border border-gray-200">
            <Title level={4}>产品管理</Title>
            <Text className="text-gray-600">
              管理产品目录，维护产品信息和规格。
            </Text>
          </div>
          
          <div className="p-6 bg-white rounded-lg border border-gray-200">
            <Title level={4}>订单跟踪</Title>
            <Text className="text-gray-600">
              跟踪订单状态，管理交易流程。
            </Text>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradePage;