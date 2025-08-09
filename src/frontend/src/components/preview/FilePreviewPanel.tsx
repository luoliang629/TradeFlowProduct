import React, { useState, useEffect } from 'react';
import { Card, Spin, Empty, Button, message, Tabs, Typography } from 'antd';
import {
  FileTextOutlined,
  PictureOutlined,
  FilePdfOutlined,
  FileWordOutlined,
  FileExcelOutlined,
  CodeOutlined,
  DownloadOutlined,
  CopyOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import ReactMarkdown from 'react-markdown';
import type { FileAttachment } from '../../types';

const { Text, Title } = Typography;
const { TabPane } = Tabs;

interface FilePreviewPanelProps {
  files: FileAttachment[];
  selectedFileIndex?: number;
  onFileSelect?: (index: number) => void;
  className?: string;
}

const FilePreviewPanel: React.FC<FilePreviewPanelProps> = ({
  files,
  selectedFileIndex = 0,
  onFileSelect,
  className,
}) => {
  const [fileContents, setFileContents] = useState<{ [key: string]: string }>({});
  const [loading, setLoading] = useState<{ [key: string]: boolean }>({});

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

  // 获取代码语言
  const getCodeLanguage = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    const languageMap: { [key: string]: string } = {
      'js': 'javascript',
      'jsx': 'jsx',
      'ts': 'typescript',
      'tsx': 'tsx',
      'py': 'python',
      'java': 'java',
      'html': 'html',
      'css': 'css',
      'json': 'json',
      'md': 'markdown',
      'yaml': 'yaml',
      'yml': 'yaml',
      'xml': 'xml',
      'sql': 'sql',
      'sh': 'bash',
    };
    return languageMap[ext || ''] || 'text';
  };

  // 判断是否为文本文件
  const isTextFile = (file: FileAttachment) => {
    const textTypes = [
      'text/',
      'application/json',
      'application/javascript',
      'application/xml',
    ];
    const textExts = ['txt', 'md', 'js', 'ts', 'jsx', 'tsx', 'json', 'html', 'css', 'py', 'java'];
    const ext = file.name.split('.').pop()?.toLowerCase();
    
    return textTypes.some(type => file.type?.startsWith(type)) || 
           textExts.includes(ext || '');
  };

  // 判断是否为图片文件
  const isImageFile = (file: FileAttachment) => {
    return file.type?.startsWith('image/');
  };

  // 判断是否为Markdown文件
  const isMarkdownFile = (file: FileAttachment) => {
    const ext = file.name.split('.').pop()?.toLowerCase();
    return ext === 'md' || ext === 'markdown';
  };

  // 加载文件内容
  const loadFileContent = async (file: FileAttachment) => {
    if (!file.url || fileContents[file.url]) return;

    setLoading(prev => ({ ...prev, [file.url!]: true }));
    
    try {
      const response = await fetch(file.url);
      const content = await response.text();
      setFileContents(prev => ({ ...prev, [file.url!]: content }));
    } catch (error) {
      console.error('加载文件失败:', error);
      message.error(`加载文件失败: ${file.name}`);
    } finally {
      setLoading(prev => ({ ...prev, [file.url!]: false }));
    }
  };

  // 复制文件内容
  const copyContent = (content: string) => {
    navigator.clipboard.writeText(content);
    message.success('内容已复制到剪贴板');
  };

  // 下载文件
  const downloadFile = (file: FileAttachment) => {
    if (file.url) {
      const link = document.createElement('a');
      link.href = file.url;
      link.download = file.name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  // 渲染文件预览
  const renderFilePreview = (file: FileAttachment) => {
    if (!file.url) {
      return (
        <Empty 
          image={getFileIcon(file)}
          description={`文件 "${file.name}" 暂不支持预览`}
        />
      );
    }

    // 图片预览
    if (isImageFile(file)) {
      return (
        <div className="flex justify-center p-4">
          <img
            src={file.url}
            alt={file.name}
            className="max-w-full max-h-96 object-contain rounded shadow-lg"
            onError={() => message.error('图片加载失败')}
          />
        </div>
      );
    }

    // 文本文件预览
    if (isTextFile(file)) {
      const content = fileContents[file.url];
      const isLoading = loading[file.url];

      if (isLoading) {
        return (
          <div className="flex justify-center items-center h-64">
            <Spin size="large" tip="加载中..." />
          </div>
        );
      }

      if (!content) {
        loadFileContent(file);
        return null;
      }

      // Markdown渲染
      if (isMarkdownFile(file)) {
        return (
          <Tabs defaultActiveKey="preview">
            <TabPane tab="预览" key="preview">
              <div className="markdown-body p-4 bg-white rounded">
                <ReactMarkdown>{content}</ReactMarkdown>
              </div>
            </TabPane>
            <TabPane tab="源码" key="source">
              <SyntaxHighlighter
                language="markdown"
                style={tomorrow}
                showLineNumbers
                className="rounded"
              >
                {content}
              </SyntaxHighlighter>
            </TabPane>
          </Tabs>
        );
      }

      // 代码文件高亮
      const language = getCodeLanguage(file.name);
      if (['js', 'ts', 'tsx', 'jsx', 'json', 'html', 'css', 'py', 'java'].includes(language)) {
        return (
          <div className="relative">
            <SyntaxHighlighter
              language={language}
              style={tomorrow}
              showLineNumbers
              className="rounded"
            >
              {content}
            </SyntaxHighlighter>
            <Button
              icon={<CopyOutlined />}
              className="absolute top-2 right-2 opacity-70 hover:opacity-100"
              onClick={() => copyContent(content)}
            >
              复制
            </Button>
          </div>
        );
      }

      // 普通文本文件
      return (
        <div className="relative">
          <pre className="bg-gray-50 p-4 rounded border overflow-auto max-h-96 whitespace-pre-wrap">
            {content}
          </pre>
          <Button
            icon={<CopyOutlined />}
            className="absolute top-2 right-2 opacity-70 hover:opacity-100"
            onClick={() => copyContent(content)}
          >
            复制
          </Button>
        </div>
      );
    }

    // 其他文件类型
    return (
      <Empty
        image={getFileIcon(file)}
        description={
          <div className="space-y-2">
            <Text>该文件类型不支持在线预览</Text>
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={() => downloadFile(file)}
            >
              下载查看
            </Button>
          </div>
        }
      />
    );
  };

  if (!files || files.length === 0) {
    return (
      <Card className={className}>
        <Empty
          image={<EyeOutlined className="text-4xl text-gray-400" />}
          description="没有文件可预览"
        />
      </Card>
    );
  }

  const currentFile = files[selectedFileIndex];

  return (
    <Card 
      className={className}
      title={
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getFileIcon(currentFile)}
            <span className="font-medium">{currentFile.name}</span>
            {currentFile.size && (
              <Text type="secondary" className="text-xs">
                ({(currentFile.size / 1024).toFixed(1)} KB)
              </Text>
            )}
          </div>
          <div className="flex items-center gap-2">
            {currentFile.url && (
              <Button
                type="text"
                icon={<DownloadOutlined />}
                onClick={() => downloadFile(currentFile)}
              >
                下载
              </Button>
            )}
            {files.length > 1 && onFileSelect && (
              <Text type="secondary" className="text-sm">
                {selectedFileIndex + 1} / {files.length}
              </Text>
            )}
          </div>
        </div>
      }
      extra={
        files.length > 1 && onFileSelect && (
          <div className="flex items-center gap-2">
            <Button
              size="small"
              disabled={selectedFileIndex === 0}
              onClick={() => onFileSelect(selectedFileIndex - 1)}
            >
              上一个
            </Button>
            <Button
              size="small"
              disabled={selectedFileIndex === files.length - 1}
              onClick={() => onFileSelect(selectedFileIndex + 1)}
            >
              下一个
            </Button>
          </div>
        )
      }
    >
      {renderFilePreview(currentFile)}
    </Card>
  );
};

export default FilePreviewPanel;