import { Layout, Card, Button, Space, Typography, Spin, Empty, List, Tag } from 'antd';
import { 
  CloseOutlined,
  DownloadOutlined,
  EyeOutlined,
  FileTextOutlined,
  FilePdfOutlined,
  FileExcelOutlined,
  FileImageOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import { useState, useEffect } from 'react';
import { useAppSelector, useAppDispatch } from '../../store/hooks';
import { toggleFilePreviewPanel } from '../../store/uiSlice';
import { apiService } from '../../services';
import type { FileInfo } from '../../types';

const { Sider } = Layout;
const { Title, Text } = Typography;

interface FilePreviewPanelProps {
  visible: boolean;
  width: string;
}

const FilePreviewPanel: React.FC<FilePreviewPanelProps> = ({ visible, width }) => {
  const dispatch = useAppDispatch();
  const { theme } = useAppSelector(state => state.ui);
  const { currentSession } = useAppSelector(state => state.chat);
  
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [previewContent, setPreviewContent] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<FileInfo | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  // 预览文件
  const previewFile = async (file: FileInfo) => {
    try {
      setPreviewLoading(true);
      setSelectedFile(file);
      const response = await apiService.files.getPreview(file.id);
      if (response.success) {
        setPreviewContent(response.data.content);
      }
    } catch (error) {
      console.error('预览文件失败:', error);
      setPreviewContent('无法预览此文件');
    } finally {
      setPreviewLoading(false);
    }
  };

  // 下载文件
  const downloadFile = (file: FileInfo) => {
    window.open(file.url, '_blank');
  };

  // 删除文件
  const deleteFile = async (file: FileInfo) => {
    try {
      const response = await apiService.files.delete(file.id);
      if (response.success) {
        setFiles(prev => prev.filter(f => f.id !== file.id));
        if (selectedFile?.id === file.id) {
          setSelectedFile(null);
          setPreviewContent('');
        }
      }
    } catch (error) {
      console.error('删除文件失败:', error);
    }
  };

  // 获取文件图标
  const getFileIcon = (type: string) => {
    if (type.includes('pdf')) return <FilePdfOutlined className="text-red-500" />;
    if (type.includes('excel') || type.includes('spreadsheet')) return <FileExcelOutlined className="text-green-500" />;
    if (type.includes('image')) return <FileImageOutlined className="text-blue-500" />;
    return <FileTextOutlined className="text-gray-500" />;
  };

  // 格式化文件大小
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        setLoading(true);
        const response = await apiService.files.getList(currentSession?.id);
        if (response.success) {
          setFiles(response.data);
        }
      } catch (error) {
        console.error('获取文件列表失败:', error);
      } finally {
        setLoading(false);
      }
    };

    if (visible && currentSession) {
      fetchFiles();
    }
  }, [visible, currentSession]);

  if (!visible) return null;

  return (
    <Sider
      width={width}
      theme={theme}
      className="border-l border-gray-200 bg-gray-50"
      style={{
        backgroundColor: theme === 'dark' ? '#1f1f1f' : '#f9fafb',
        borderLeftColor: theme === 'dark' ? '#404040' : '#e5e7eb',
        height: 'calc(100vh - 64px)',
        overflow: 'hidden',
      }}
    >
      <div className="h-full flex flex-col">
        {/* 头部 */}
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <Title level={5} className="mb-0">
            文件预览
          </Title>
          <Button
            type="text"
            size="small"
            icon={<CloseOutlined />}
            onClick={() => dispatch(toggleFilePreviewPanel())}
          />
        </div>

        <div className="flex-1 flex overflow-hidden">
          {/* 文件列表 */}
          <div className="w-1/3 border-r border-gray-200 overflow-hidden">
            <div className="p-3">
              <Text className="text-xs text-gray-500 font-medium">
                会话文件 ({files.length})
              </Text>
            </div>
            
            <div className="flex-1 overflow-y-auto">
              {loading ? (
                <div className="flex justify-center items-center h-32">
                  <Spin />
                </div>
              ) : files.length === 0 ? (
                <Empty 
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                  description="暂无文件"
                  className="mt-8"
                />
              ) : (
                <List
                  size="small"
                  dataSource={files}
                  renderItem={(file) => (
                    <List.Item
                      className={`cursor-pointer px-3 py-2 hover:bg-gray-100 ${
                        selectedFile?.id === file.id ? 'bg-blue-50 border-r-2 border-blue-500' : ''
                      }`}
                      onClick={() => previewFile(file)}
                    >
                      <div className="w-full">
                        <div className="flex items-center gap-2 mb-1">
                          {getFileIcon(file.type)}
                          <Text 
                            className="text-sm font-medium truncate flex-1"
                            title={file.name}
                          >
                            {file.name}
                          </Text>
                        </div>
                        <div className="flex justify-between items-center">
                          <Text className="text-xs text-gray-500">
                            {formatFileSize(file.size)}
                          </Text>
                          <Space size={4}>
                            <Button
                              type="text"
                              size="small"
                              icon={<EyeOutlined />}
                              onClick={(e) => {
                                e.stopPropagation();
                                previewFile(file);
                              }}
                            />
                            <Button
                              type="text"
                              size="small"
                              icon={<DownloadOutlined />}
                              onClick={(e) => {
                                e.stopPropagation();
                                downloadFile(file);
                              }}
                            />
                            <Button
                              type="text"
                              size="small"
                              danger
                              icon={<DeleteOutlined />}
                              onClick={(e) => {
                                e.stopPropagation();
                                deleteFile(file);
                              }}
                            />
                          </Space>
                        </div>
                      </div>
                    </List.Item>
                  )}
                />
              )}
            </div>
          </div>

          {/* 预览区域 */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {selectedFile ? (
              <>
                {/* 预览头部 */}
                <div className="p-3 border-b border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      {getFileIcon(selectedFile.type)}
                      <Text 
                        className="font-medium truncate"
                        title={selectedFile.name}
                      >
                        {selectedFile.name}
                      </Text>
                    </div>
                    <Space>
                      <Button
                        type="text"
                        size="small"
                        icon={<DownloadOutlined />}
                        onClick={() => downloadFile(selectedFile)}
                      />
                    </Space>
                  </div>
                  <div className="flex items-center gap-4">
                    <Tag size="small">
                      {formatFileSize(selectedFile.size)}
                    </Tag>
                    <Text className="text-xs text-gray-500">
                      {new Date(selectedFile.created_at).toLocaleDateString()}
                    </Text>
                  </div>
                </div>

                {/* 预览内容 */}
                <div className="flex-1 p-3 overflow-y-auto">
                  {previewLoading ? (
                    <div className="flex justify-center items-center h-32">
                      <Spin />
                    </div>
                  ) : selectedFile.type.includes('image') ? (
                    <div className="text-center">
                      <img
                        src={selectedFile.preview_url || selectedFile.url}
                        alt={selectedFile.name}
                        className="max-w-full max-h-96 object-contain mx-auto rounded-lg shadow-sm"
                      />
                    </div>
                  ) : (
                    <Card size="small" className="h-full">
                      <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono">
                        {previewContent || '正在加载预览内容...'}
                      </pre>
                    </Card>
                  )}
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center">
                <Empty
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                  description="选择文件以预览"
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </Sider>
  );
};

export default FilePreviewPanel;