import { Layout } from 'antd';
import { Outlet } from 'react-router-dom';
import { useAppSelector } from '../store/hooks';
import Sidebar from '../components/layout/Sidebar';
import Header from '../components/layout/Header';
import FilePreviewPanel from '../components/layout/FilePreviewPanel';

const { Content } = Layout;

const AppLayout: React.FC = () => {
  const { sidebarCollapsed, filePreviewPanelOpen } = useAppSelector(state => state.ui);

  return (
    <Layout className="h-screen">
      {/* 左侧导航栏 */}
      <Sidebar collapsed={sidebarCollapsed} />
      
      {/* 右侧主要内容区域 */}
      <Layout 
        className="flex-1 min-w-0"
        style={{
          marginLeft: sidebarCollapsed ? 0 : 280,
          transition: 'margin-left 0.3s cubic-bezier(0.2, 0, 0.2, 1)',
        }}
      >
        {/* 顶部Header */}
        <Header />
        
        {/* 中间内容区域和右侧文件预览区域 */}
        <Layout className="flex-1 min-h-0 flex-row">
          {/* 中间内容区 */}
          <Content 
            className="bg-white flex flex-col min-h-0"
            style={{ 
              width: filePreviewPanelOpen ? '60%' : '100%',
              transition: 'width 0.3s cubic-bezier(0.2, 0, 0.2, 1)',
            }}
          >
            <div className="flex-1 h-full overflow-hidden">
              <Outlet />
            </div>
          </Content>
          
          {/* 右侧文件预览面板 */}
          <FilePreviewPanel 
            visible={filePreviewPanelOpen}
            width="40%"
          />
        </Layout>
      </Layout>
    </Layout>
  );
};

export default AppLayout;