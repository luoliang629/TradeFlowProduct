import React, { useState, useRef, useCallback } from 'react';
import { Input, Button, Upload, message, Tooltip, Popover } from 'antd';
import {
  SendOutlined,
  PaperClipOutlined,
  SmileOutlined,
  LoadingOutlined,
  PlusOutlined,
} from '@ant-design/icons';
import { useDropzone } from 'react-dropzone';

const { TextArea } = Input;

interface MessageInputProps {
  onSendMessage: (content: string, files?: File[]) => Promise<void>;
  loading?: boolean;
  placeholder?: string;
  disabled?: boolean;
  maxLength?: number;
  showFileUpload?: boolean;
  showEmoji?: boolean;
  acceptedFileTypes?: string[];
  maxFileSize?: number;
}

const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  loading = false,
  placeholder = "输入您的消息...",
  disabled = false,
  maxLength = 2000,
  showFileUpload = true,
  showEmoji = true,
  acceptedFileTypes = ['image/*', 'text/*', '.pdf', '.doc', '.docx', '.xls', '.xlsx'],
  maxFileSize = 10 * 1024 * 1024, // 10MB
}) => {
  const [inputValue, setInputValue] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const textAreaRef = useRef<any>(null);

  // 处理文件拖拽
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const validFiles = acceptedFiles.filter(file => {
      if (file.size > maxFileSize) {
        message.error(`文件 ${file.name} 超过最大大小限制`);
        return false;
      }
      return true;
    });
    
    setFiles(prev => [...prev, ...validFiles]);
  }, [maxFileSize]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    noClick: true,
    multiple: true,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif'],
      'text/*': ['.txt', '.md'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
  });

  // 发送消息
  const handleSend = async () => {
    if (!inputValue.trim() && files.length === 0) {
      return;
    }

    try {
      await onSendMessage(inputValue, files);
      setInputValue('');
      setFiles([]);
      
      // 重新聚焦到输入框
      if (textAreaRef.current) {
        textAreaRef.current.focus();
      }
    } catch (error) {
      message.error('发送失败，请重试');
    }
  };

  // 处理键盘事件
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // 移除文件
  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  // 文件上传组件
  const fileUploadProps = {
    beforeUpload: (file: File) => {
      if (file.size > maxFileSize) {
        message.error('文件大小超过限制');
        return false;
      }
      setFiles(prev => [...prev, file]);
      return false;
    },
    showUploadList: false,
    multiple: true,
    accept: acceptedFileTypes.join(','),
  };

  // 表情选择器（简单实现）
  const emojiList = ['😊', '😂', '🤔', '👍', '❤️', '😢', '😮', '🎉', '🔥', '💡'];
  const EmojiPicker = (
    <div className="grid grid-cols-5 gap-2 p-2 w-40">
      {emojiList.map(emoji => (
        <button
          key={emoji}
          className="text-lg p-1 hover:bg-gray-100 rounded"
          onClick={() => {
            setInputValue(prev => prev + emoji);
            textAreaRef.current?.focus();
          }}
        >
          {emoji}
        </button>
      ))}
    </div>
  );

  return (
    <div
      {...getRootProps()}
      className={`relative bg-white border rounded-lg shadow-sm ${
        isDragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-200'
      } ${disabled ? 'opacity-50 pointer-events-none' : ''}`}
    >
      <input {...getInputProps()} />
      
      {/* 拖拽提示 */}
      {isDragActive && (
        <div className="absolute inset-0 bg-blue-50 bg-opacity-90 flex items-center justify-center z-10 rounded-lg border-2 border-dashed border-blue-400">
          <div className="text-blue-600 text-center">
            <PlusOutlined className="text-3xl mb-2" />
            <div>拖拽文件到此处上传</div>
          </div>
        </div>
      )}

      {/* 文件预览 */}
      {files.length > 0 && (
        <div className="p-3 border-b border-gray-200">
          <div className="flex flex-wrap gap-2">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center bg-gray-100 rounded px-2 py-1 text-sm"
              >
                <PaperClipOutlined className="mr-1 text-gray-500" />
                <span className="max-w-32 truncate">{file.name}</span>
                <Button
                  type="text"
                  size="small"
                  className="ml-1 p-0 h-auto"
                  onClick={() => removeFile(index)}
                >
                  ×
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 输入区域 */}
      <div className="flex items-end p-3">
        <div className="flex-1 mr-3">
          <TextArea
            ref={textAreaRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            maxLength={maxLength}
            showCount
            autoSize={{ minRows: 1, maxRows: 6 }}
            className="resize-none border-0 p-0 shadow-none"
            disabled={disabled || loading}
          />
        </div>

        {/* 工具栏 */}
        <div className="flex items-center gap-2">
          {/* 文件上传 */}
          {showFileUpload && (
            <Upload {...fileUploadProps}>
              <Tooltip title="上传文件">
                <Button
                  type="text"
                  icon={<PaperClipOutlined />}
                  className="text-gray-500 hover:text-gray-700"
                  disabled={disabled || loading}
                />
              </Tooltip>
            </Upload>
          )}

          {/* 表情选择 */}
          {showEmoji && (
            <Popover
              content={EmojiPicker}
              trigger="click"
              placement="topRight"
            >
              <Tooltip title="添加表情">
                <Button
                  type="text"
                  icon={<SmileOutlined />}
                  className="text-gray-500 hover:text-gray-700"
                  disabled={disabled || loading}
                />
              </Tooltip>
            </Popover>
          )}

          {/* 发送按钮 */}
          <Button
            type="primary"
            shape="circle"
            icon={loading ? <LoadingOutlined /> : <SendOutlined />}
            onClick={handleSend}
            disabled={disabled || loading || (!inputValue.trim() && files.length === 0)}
            className="shrink-0"
            size="small"
          />
        </div>
      </div>

      {/* 快捷键提示 */}
      <div className="px-3 pb-2 text-xs text-gray-400">
        按 Enter 发送，Shift + Enter 换行
      </div>
    </div>
  );
};

export default MessageInput;