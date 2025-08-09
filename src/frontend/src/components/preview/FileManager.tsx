import React, { useState } from 'react';
import { Layout, Tree, Card, Button, Input, Space, Tag, Tooltip, Empty } from 'antd';
import {
  FolderOutlined,
  FolderOpenOutlined,
  FileTextOutlined,
  PictureOutlined,
  FilePdfOutlined,
  FileWordOutlined,
  FileExcelOutlined,
  CodeOutlined,
  SearchOutlined,
  FilterOutlined,
  UploadOutlined,
} from '@ant-design/icons';
import FilePreviewPanel from './FilePreviewPanel';
import type { FileAttachment } from '../../types';
import type { DataNode } from 'antd/es/tree';

const { Sider, Content } = Layout;
const { Search } = Input;

interface FileNode extends DataNode {
  type: 'folder' | 'file';
  file?: FileAttachment;
  children?: FileNode[];
}

interface FileManagerProps {
  files: FileAttachment[];
  onFileUpload?: (files: File[]) => void;
  onFileDelete?: (file: FileAttachment) => void;
  className?: string;
}

const FileManager: React.FC<FileManagerProps> = ({
  files,
  onFileUpload,
  onFileDelete,
  className,
}) => {
  const [selectedKeys, setSelectedKeys] = useState<string[]>([]);
  const [selectedFile, setSelectedFile] = useState<FileAttachment | null>(null);
  const [searchValue, setSearchValue] = useState('');
  const [filterType, setFilterType] = useState<string>('all');

  // 获取文件图标
  const getFileIcon = (file: FileAttachment) => {
    const { type, name } = file;
    const ext = name.split('.').pop()?.toLowerCase();

    if (type?.startsWith('image/')) {
      return <PictureOutlined className="text-green-500" />;
    }
    if (type === 'application/pdf') {
      return <FilePdfOutlined className="text-red-500" />;
    }
    if (type?.includes('word') || ext === 'doc' || ext === 'docx') {
      return <FileWordOutlined className="text-blue-500" />;
    }
    if (type?.includes('sheet') || ext === 'xls' || ext === 'xlsx' || ext === 'csv') {
      return <FileExcelOutlined className="text-green-600" />;
    }
    if (['js', 'ts', 'tsx', 'jsx', 'json', 'html', 'css', 'py', 'java'].includes(ext || '')) {
      return <CodeOutlined className="text-purple-500" />;
    }
    return <FileTextOutlined className="text-gray-500" />;
  };

  // 获取文件类型标签
  const getFileTypeTag = (file: FileAttachment) => {
    const ext = file.name.split('.').pop()?.toLowerCase();
    const typeColors: { [key: string]: string } = {
      'pdf': 'red',
      'doc': 'blue',
      'docx': 'blue',
      'xls': 'green',
      'xlsx': 'green',
      'csv': 'green',
      'jpg': 'orange',
      'jpeg': 'orange',
      'png': 'orange',
      'gif': 'orange',
      'js': 'gold',
      'ts': 'blue',
      'tsx': 'blue',
      'jsx': 'gold',
      'json': 'purple',
      'html': 'red',
      'css': 'blue',
      'py': 'green',
      'java': 'red',
      'md': 'cyan',
    };
    
    return (
      <Tag color={typeColors[ext || ''] || 'default'} size="small">
        {ext?.toUpperCase() || 'FILE'}
      </Tag>
    );
  };

  // 构建文件树结构
  const buildFileTree = (files: FileAttachment[]): FileNode[] => {
    const filteredFiles = files.filter(file => {
      // 搜索过滤
      if (searchValue && !file.name.toLowerCase().includes(searchValue.toLowerCase())) {
        return false;
      }
      
      // 类型过滤
      if (filterType !== 'all') {
        const ext = file.name.split('.').pop()?.toLowerCase();
        switch (filterType) {
          case 'image':
            return file.type?.startsWith('image/');
          case 'document':
            return ['pdf', 'doc', 'docx', 'txt', 'md'].includes(ext || '');
          case 'spreadsheet':
            return ['xls', 'xlsx', 'csv'].includes(ext || '');
          case 'code':
            return ['js', 'ts', 'tsx', 'jsx', 'json', 'html', 'css', 'py', 'java'].includes(ext || '');
          default:
            return true;
        }
      }
      
      return true;
    });

    // 按文件类型和名称分组
    const grouped: { [key: string]: FileAttachment[] } = {};
    
    filteredFiles.forEach(file => {
      const ext = file.name.split('.').pop()?.toLowerCase() || 'other';
      if (!grouped[ext]) {
        grouped[ext] = [];
      }
      grouped[ext].push(file);
    });

    // 构建树节点
    const treeNodes: FileNode[] = Object.entries(grouped).map(([ext, files]) => {
      const folderNode: FileNode = {
        title: `${ext.toUpperCase()} 文件 (${files.length})`,
        key: `folder-${ext}`,
        type: 'folder',
        icon: <FolderOutlined />,
        children: files.map((file, index) => ({
          title: (
            <div className="flex items-center justify-between w-full">
              <span className="flex-1 truncate">{file.name}</span>
              <div className="flex items-center gap-1">
                {getFileTypeTag(file)}
                {file.size && (
                  <Tag size="small" color="default">
                    {(file.size / 1024).toFixed(1)}KB
                  </Tag>
                )}
              </div>
            </div>
          ),
          key: `file-${ext}-${index}`,
          type: 'file',
          file,
          icon: getFileIcon(file),
          isLeaf: true,
        })),
      };
      return folderNode;
    });

    return treeNodes;
  };

  // 处理树节点选择
  const handleSelect = (selectedKeys: string[], info: any) => {
    setSelectedKeys(selectedKeys);
    
    if (selectedKeys.length > 0 && info.node.type === 'file') {
      setSelectedFile(info.node.file);
    } else {
      setSelectedFile(null);
    }
  };

  // 处理文件上传
  const handleUpload = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = '*/*';
    input.onchange = (e) => {
      const files = Array.from((e.target as HTMLInputElement).files || []);
      if (files.length > 0 && onFileUpload) {
        onFileUpload(files);
      }
    };
    input.click();
  };

  const treeData = buildFileTree(files);

  return (
    <Layout className={`${className} h-full`}>
      {/* 文件列表侧边栏 */}
      <Sider width={350} className="bg-white border-r">
        <div className="p-4 border-b">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-800">文件管理器</h3>
            <Button
              type="primary"
              size="small"
              icon={<UploadOutlined />}
              onClick={handleUpload}
            >
              上传
            </Button>
          </div>
          
          {/* 搜索框 */}
          <Search
            placeholder="搜索文件..."
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className="mb-3"
            size="small"
          />
          
          {/* 类型过滤 */}
          <div className="flex flex-wrap gap-1">
            {[
              { key: 'all', label: '全部', icon: <FilterOutlined /> },
              { key: 'image', label: '图片', icon: <PictureOutlined /> },
              { key: 'document', label: '文档', icon: <FileTextOutlined /> },
              { key: 'spreadsheet', label: '表格', icon: <FileExcelOutlined /> },
              { key: 'code', label: '代码', icon: <CodeOutlined /> },
            ].map(({ key, label, icon }) => (
              <Button
                key={key}
                size="small"
                type={filterType === key ? 'primary' : 'default'}
                icon={icon}
                onClick={() => setFilterType(key)}
                className="text-xs"
              >
                {label}
              </Button>
            ))}
          </div>
        </div>

        {/* 文件树 */}
        <div className="flex-1 overflow-auto p-2">
          {treeData.length === 0 ? (
            <Empty
              image={<FolderOutlined className="text-4xl text-gray-400" />}
              description="没有找到文件"
              className="mt-8"
            />
          ) : (
            <Tree
              treeData={treeData}
              selectedKeys={selectedKeys}
              onSelect={handleSelect}
              showIcon
              switcherIcon={({ expanded }) => 
                expanded ? <FolderOpenOutlined /> : <FolderOutlined />
              }
              className="file-tree"
            />
          )}
        </div>

        {/* 统计信息 */}
        <div className="p-3 border-t bg-gray-50 text-xs text-gray-600">
          <div className="flex justify-between">
            <span>共 {files.length} 个文件</span>
            <span>
              总大小: {(files.reduce((sum, f) => sum + (f.size || 0), 0) / 1024 / 1024).toFixed(1)} MB
            </span>
          </div>
        </div>
      </Sider>

      {/* 文件预览区域 */}
      <Content className="bg-gray-50">
        {selectedFile ? (
          <FilePreviewPanel
            files={[selectedFile]}
            className="h-full"
          />
        ) : (
          <div className="h-full flex items-center justify-center">
            <Empty
              image={<FileTextOutlined className="text-6xl text-gray-400" />}
              description="请从左侧选择文件进行预览"
            />
          </div>
        )}
      </Content>
    </Layout>
  );
};

export default FileManager;