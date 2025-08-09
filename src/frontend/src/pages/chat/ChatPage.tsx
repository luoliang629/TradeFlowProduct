const ChatPage: React.FC = () => {
  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            AI对话助手
          </h2>
          <p className="text-gray-600 mb-8">
            欢迎使用TradeFlow AI助手，我可以帮您找到买家和供应商
          </p>
          <div className="space-y-2 text-sm text-gray-500">
            <p>• 买家开发和推荐</p>
            <p>• 供应商搜索和匹配</p>
            <p>• 贸易数据分析</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;