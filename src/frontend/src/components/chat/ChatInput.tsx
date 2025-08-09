import React, { useState, useRef, KeyboardEvent } from 'react';
import { Input, Button, Upload, Space, Tooltip, Popover, message } from 'antd';
import {
  SendOutlined,
  PaperClipOutlined,
  SmileOutlined,
  PictureOutlined,
  FileTextOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import type { UploadFile, RcFile } from 'antd/es/upload';

const { TextArea } = Input;

// 表情符号列表
const EMOJIS = [
  '😀', '😃', '😄', '😁', '😅', '😂', '🤣', '😊',
  '😇', '🙂', '😉', '😌', '😍', '🥰', '😘', '😗',
  '🤔', '🤗', '🤭', '🤫', '🤨', '😐', '😑', '😶',
  '🙄', '😏', '😣', '😥', '😮', '🤐', '😯', '😪',
  '😫', '😴', '😌', '😛', '😜', '😝', '🤤', '😒',
  '👍', '👎', '👌', '✌️', '🤞', '🤟', '🤘', '🤙',
  '💪', '🙏', '👏', '🤝', '❤️', '💔', '💯', '✨',
];

interface ChatInputProps {
  onSendMessage: (content: string, files?: File[]) => void;
  onFileUpload?: (files: File[]) => Promise<File[] | void>;
  disabled?: boolean;
  placeholder?: string;
}

const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  onFileUpload,
  disabled = false,
  placeholder = '输入消息...',
}) => {
  const [message, setMessage] = useState('');
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [isComposing, setIsComposing] = useState(false);
  const textAreaRef = useRef<any>(null);

  // 发送消息
  const handleSend = async () => {
    const trimmedMessage = message.trim();
    if (!trimmedMessage && files.length === 0) return;

    // 准备文件列表
    const fileList = files.map(f => f.originFileObj as File).filter(Boolean);
    
    // 调用发送回调
    onSendMessage(trimmedMessage, fileList.length > 0 ? fileList : undefined);
    
    // 清空输入
    setMessage('');
    setFiles([]);
    
    // 重新聚焦输入框
    textAreaRef.current?.focus();
  };

  // 处理键盘事件
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // 中文输入法时不处理
    if (isComposing) return;
    
    // Enter发送，Shift+Enter换行
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // 处理文件选择
  const handleFileChange = async (info: any) => {
    const { fileList } = info;
    
    // 限制文件数量
    if (fileList.length > 5) {
      message.warning('最多只能上传5个文件');
      return;
    }

    // 如果有文件上传处理函数，调用它
    if (onFileUpload && fileList.length > 0) {
      const files = fileList.map((f: UploadFile) => f.originFileObj as File).filter(Boolean);
      const processedFiles = await onFileUpload(files);
      
      if (processedFiles) {
        setFiles(fileList.filter((f: UploadFile) => 
          processedFiles.includes(f.originFileObj as File)
        ));
      } else {
        setFiles(fileList);
      }
    } else {
      setFiles(fileList);
    }
  };

  // 移除文件
  const handleRemoveFile = (file: UploadFile) => {
    setFiles(files.filter(f => f.uid !== file.uid));
  };

  // 插入表情
  const handleEmojiSelect = (emoji: string) => {
    const textarea = textAreaRef.current?.resizableTextArea?.textArea;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const newMessage = message.substring(0, start) + emoji + message.substring(end);
    
    setMessage(newMessage);
    
    // 设置光标位置
    setTimeout(() => {
      textarea.selectionStart = start + emoji.length;
      textarea.selectionEnd = start + emoji.length;
      textarea.focus();
    }, 0);
  };

  // 表情选择器
  const emojiPicker = (
    <div className="grid grid-cols-8 gap-1 p-2 max-w-xs">
      {EMOJIS.map((emoji, index) => (
        <button
          key={index}
          className="p-1 hover:bg-gray-100 rounded text-xl"
          onClick={() => handleEmojiSelect(emoji)}
        >
          {emoji}
        </button>
      ))}
    </div>
  );

  return (
    <div className="relative">
      {/* 已选择的文件 */}
      {files.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-2">
          {files.map(file => (
            <div
              key={file.uid}
              className="flex items-center gap-1 px-2 py-1 bg-gray-100 rounded"
            >
              {file.type?.startsWith('image/') ? (
                <PictureOutlined />
              ) : (
                <FileTextOutlined />
              )}
              <span className="text-sm max-w-[150px] truncate">
                {file.name}
              </span>
              <Button
                type="text"
                size="small"
                icon={<DeleteOutlined />}
                onClick={() => handleRemoveFile(file)}
              />
            </div>
          ))}
        </div>
      )}

      {/* 输入区域 */}
      <div className="flex items-end gap-2">
        {/* 文本输入框 */}
        <TextArea
          ref={textAreaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          onCompositionStart={() => setIsComposing(true)}
          onCompositionEnd={() => setIsComposing(false)}
          placeholder={placeholder}
          disabled={disabled}
          autoSize={{ minRows: 1, maxRows: 6 }}
          className="flex-1"
          style={{
            resize: 'none',
            paddingRight: '120px', // 为按钮留出空间
          }}
        />

        {/* 操作按钮 */}
        <Space className="absolute right-2 bottom-2">
          {/* 表情 */}
          <Popover
            content={emojiPicker}
            trigger="click"
            placement="topRight"
          >
            <Tooltip title="添加表情">
              <Button
                type="text"
                icon={<SmileOutlined />}
                disabled={disabled}
              />
            </Tooltip>
          </Popover>

          {/* 文件上传 */}
          <Upload
            multiple
            showUploadList={false}
            beforeUpload={() => false}
            onChange={handleFileChange}
            accept="image/*,.pdf,.doc,.docx,.xls,.xlsx,.txt,.csv"
            disabled={disabled}
          >
            <Tooltip title="添加附件">
              <Button
                type="text"
                icon={<PaperClipOutlined />}
                disabled={disabled}
              />
            </Tooltip>
          </Upload>

          {/* 发送按钮 */}
          <Tooltip title="发送 (Enter)">
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSend}
              disabled={disabled || (!message.trim() && files.length === 0)}
            />
          </Tooltip>
        </Space>
      </div>

      {/* 提示文字 */}
      <div className="mt-1 text-xs text-gray-400">
        按 Enter 发送，Shift + Enter 换行
      </div>
    </div>
  );
};

export default ChatInput;