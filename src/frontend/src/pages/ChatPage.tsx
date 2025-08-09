import { Typography } from 'antd';

const { Title, Text } = Typography;

const ChatPage: React.FC = () => {
  return (
    <div className="p-6 bg-gray-50 min-h-full">
      <div className="max-w-4xl mx-auto">
        <Title level={2} className="mb-4">
          AI助手
        </Title>
        <Text className="text-gray-600">
          这里将是AI对话界面。您可以与TradeFlow AI助手进行对话，获取买家推荐、供应商分析等服务。
        </Text>
        
        {/* TODO: 这里将集成聊天界面组件 */}
        <div className="mt-8 p-8 bg-white rounded-lg border border-gray-200 text-center">
          <Text className="text-gray-500">
            聊天界面组件将在后续任务中实现...
          </Text>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;