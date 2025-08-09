import { useState, useCallback } from 'react';
import { useAppDispatch } from '../store/hooks';
import { addNotification } from '../store/uiSlice';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiOptions {
  showErrorNotification?: boolean;
  showSuccessNotification?: boolean;
  successMessage?: string;
}

/**
 * 通用API调用Hook
 * 提供loading、error状态管理和通知功能
 */
export function useApi<T = unknown>(
  apiCall: (...args: unknown[]) => Promise<{ success: boolean; data: T }>,
  options: UseApiOptions = {}
) {
  const {
    showErrorNotification = true,
    showSuccessNotification = false,
    successMessage,
  } = options;

  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const dispatch = useAppDispatch();

  const execute = useCallback(
    async (...args: unknown[]) => {
      setState(prev => ({ ...prev, loading: true, error: null }));

      try {
        const response = await apiCall(...args);
        
        if (response.success) {
          setState({
            data: response.data,
            loading: false,
            error: null,
          });

          if (showSuccessNotification && successMessage) {
            dispatch(addNotification({
              type: 'success',
              title: '操作成功',
              message: successMessage,
            }));
          }

          return response.data;
        } else {
          throw new Error('API调用失败');
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : '未知错误';
        
        setState({
          data: null,
          loading: false,
          error: errorMessage,
        });

        if (showErrorNotification) {
          dispatch(addNotification({
            type: 'error',
            title: '操作失败',
            message: errorMessage,
          }));
        }

        throw error;
      }
    },
    [apiCall, dispatch, showErrorNotification, showSuccessNotification, successMessage]
  );

  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
    });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}

/**
 * 文件上传Hook
 */
export function useFileUpload() {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  
  const dispatch = useAppDispatch();

  const uploadFile = useCallback(async (
    file: File,
    uploadFn: (file: File, onProgress: (progress: number) => void) => Promise<unknown>
  ) => {
    setUploading(true);
    setUploadProgress(0);

    try {
      const result = await uploadFn(file, setUploadProgress);
      
      dispatch(addNotification({
        type: 'success',
        title: '上传成功',
        message: `文件 ${file.name} 上传完成`,
      }));

      return result;
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '上传失败',
        message: error instanceof Error ? error.message : '文件上传失败',
      }));
      throw error;
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, [dispatch]);

  return {
    uploading,
    uploadProgress,
    uploadFile,
  };
}

/**
 * SSE连接Hook
 */
export function useSSE(url: string | null) {
  const [connected, setConnected] = useState(false);
  const [eventSource, setEventSource] = useState<EventSource | null>(null);

  const connect = useCallback(() => {
    if (!url) return;

    const es = new EventSource(url);
    
    es.onopen = () => {
      setConnected(true);
    };

    es.onerror = () => {
      setConnected(false);
    };

    setEventSource(es);

    return () => {
      es.close();
      setConnected(false);
    };
  }, [url]);

  const disconnect = useCallback(() => {
    if (eventSource) {
      eventSource.close();
      setEventSource(null);
      setConnected(false);
    }
  }, [eventSource]);

  const addEventListener = useCallback((
    event: string, 
    handler: (event: MessageEvent) => void
  ) => {
    if (eventSource) {
      eventSource.addEventListener(event, handler);
    }
  }, [eventSource]);

  return {
    connected,
    connect,
    disconnect,
    addEventListener,
  };
}