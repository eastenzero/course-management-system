import { useState, useEffect, useCallback, useRef } from 'react';
import { message } from 'antd';
import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
});

// 请求拦截器 - 添加认证token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理通用错误
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token过期，清除本地存储并跳转到登录页
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface UseApiOptions<T> {
  /** 初始数据 */
  initialData?: T;
  /** 是否立即执行 */
  immediate?: boolean;
  /** 成功回调 */
  onSuccess?: (data: T) => void;
  /** 错误回调 */
  onError?: (error: any) => void;
  /** 完成回调（无论成功失败） */
  onFinally?: () => void;
  /** 是否显示错误消息 */
  showError?: boolean;
  /** 是否显示成功消息 */
  showSuccess?: boolean;
  /** 成功消息文本 */
  successMessage?: string;
  /** 错误消息文本 */
  errorMessage?: string;
  /** 依赖项数组，当依赖项变化时重新执行 */
  deps?: any[];
}

export interface UseApiResult<T> {
  /** 数据 */
  data: T | undefined;
  /** 加载状态 */
  loading: boolean;
  /** 错误信息 */
  error: any;
  /** 执行API调用 */
  run: (...args: any[]) => Promise<T>;
  /** 刷新（使用上次的参数重新执行） */
  refresh: () => Promise<T>;
  /** 取消请求 */
  cancel: () => void;
  /** 重置状态 */
  reset: () => void;
}

/**
 * API调用Hook
 * @param apiFunction API函数
 * @param options 配置选项
 */
export function useApi<T = any>(
  apiFunction: (...args: any[]) => Promise<any>,
  options: UseApiOptions<T> = {}
): UseApiResult<T> {
  const {
    initialData,
    immediate = false,
    onSuccess,
    onError,
    onFinally,
    showError = true,
    showSuccess = false,
    successMessage,
    errorMessage,
    deps = [],
  } = options;

  const [data, setData] = useState<T | undefined>(initialData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);
  
  const lastArgsRef = useRef<any[]>([]);
  const cancelRef = useRef<boolean>(false);

  const run = useCallback(async (...args: any[]): Promise<T> => {
    lastArgsRef.current = args;
    cancelRef.current = false;
    
    setLoading(true);
    setError(null);

    try {
      const response = await apiFunction(...args);
      
      if (cancelRef.current) {
        return response;
      }

      const result = response?.data || response;
      setData(result);

      if (onSuccess) {
        onSuccess(result);
      }

      if (showSuccess && successMessage) {
        message.success(successMessage);
      }

      return result;
    } catch (err: any) {
      if (cancelRef.current) {
        throw err;
      }

      setError(err);

      if (onError) {
        onError(err);
      }

      if (showError) {
        const msg = errorMessage || err?.response?.data?.message || err?.message || '操作失败';
        message.error(msg);
      }

      throw err;
    } finally {
      if (!cancelRef.current) {
        setLoading(false);
        if (onFinally) {
          onFinally();
        }
      }
    }
  }, [apiFunction, onSuccess, onError, onFinally, showError, showSuccess, successMessage, errorMessage]);

  const refresh = useCallback(async (): Promise<T> => {
    return run(...lastArgsRef.current);
  }, [run]);

  const cancel = useCallback(() => {
    cancelRef.current = true;
    setLoading(false);
  }, []);

  const reset = useCallback(() => {
    setData(initialData);
    setLoading(false);
    setError(null);
    lastArgsRef.current = [];
  }, [initialData]);

  // 依赖项变化时自动执行
  useEffect(() => {
    if (immediate) {
      run();
    }
  }, [immediate, ...deps]);

  // 组件卸载时取消请求
  useEffect(() => {
    return () => {
      cancel();
    };
  }, [cancel]);

  return {
    data,
    loading,
    error,
    run,
    refresh,
    cancel,
    reset,
  };
}

/**
 * 分页API调用Hook
 */
export function usePaginatedApi<T = any>(
  apiFunction: (params: any) => Promise<any>,
  options: UseApiOptions<T> & {
    defaultPageSize?: number;
    defaultCurrent?: number;
  } = {}
) {
  const { defaultPageSize = 20, defaultCurrent = 1, ...apiOptions } = options;
  
  const [pagination, setPagination] = useState({
    current: defaultCurrent,
    pageSize: defaultPageSize,
    total: 0,
  });

  const { data, loading, error, run: originalRun, ...rest } = useApi(apiFunction, {
    ...apiOptions,
    onSuccess: (result) => {
      if (result && typeof result === 'object') {
        setPagination(prev => ({
          ...prev,
          total: result.total || result.count || 0,
        }));
      }
      if (apiOptions.onSuccess) {
        apiOptions.onSuccess(result);
      }
    },
  });

  const run = useCallback(async (params: any = {}) => {
    const paginationParams = {
      page: pagination.current,
      page_size: pagination.pageSize,
      ...params,
    };
    return originalRun(paginationParams);
  }, [originalRun, pagination.current, pagination.pageSize]);

  const changePage = useCallback((page: number, pageSize?: number) => {
    setPagination(prev => ({
      ...prev,
      current: page,
      pageSize: pageSize || prev.pageSize,
    }));
  }, []);

  const refresh = useCallback(() => {
    return run();
  }, [run]);

  return {
    data,
    loading,
    error,
    run,
    refresh,
    pagination,
    changePage,
    ...rest,
  };
}

/**
 * 通用API请求Hook
 * 提供request方法用于直接API调用
 */
export function useRequest() {
  const request = useCallback(async (url: string, options: any = {}) => {
    try {
      const response = await api({
        url,
        method: options.method || 'GET',
        data: options.data,
        params: options.params,
        ...options,
      });
      return response;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }, []);

  return { request };
}

export default useRequest;
