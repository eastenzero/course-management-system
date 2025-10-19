import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { message } from 'antd';

// API基础配置
// 通过Vite代理连接到后端服务器
const API_BASE_URL = '/api/v1';

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    // 添加认证token
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 添加请求时间戳（用于缓存控制）
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now(),
      };
    }

    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // 成功响应处理
    return response;
  },
  async error => {
    const { response, config } = error;

    if (response) {
      switch (response.status) {
        case 401:
          // 未授权，尝试刷新token
          const refreshToken = localStorage.getItem('refreshToken');
          if (refreshToken && !config._retry) {
            config._retry = true;

            try {
              const refreshResponse = await axios.post(
                `${API_BASE_URL}/auth/refresh/`,
                {
                  refresh: refreshToken,
                }
              );

              // 处理刷新token的响应格式
              const newToken = refreshResponse.data.access || refreshResponse.data.data?.access;
              localStorage.setItem('token', newToken);

              // 重试原始请求
              config.headers.Authorization = `Bearer ${newToken}`;
              return apiClient(config);
            } catch (refreshError) {
              // 刷新失败，清除token并跳转到登录页
              localStorage.removeItem('token');
              localStorage.removeItem('refreshToken');
              window.location.href = '/login';
              return Promise.reject(refreshError);
            }
          } else {
            // 没有刷新token或刷新失败
            localStorage.removeItem('token');
            localStorage.removeItem('refreshToken');
            window.location.href = '/login';
          }
          break;

        case 403:
          message.error('权限不足，无法访问该资源');
          break;

        case 404:
          message.error('请求的资源不存在');
          break;

        case 422:
          // 表单验证错误
          const errors = response.data?.errors;
          if (errors) {
            Object.values(errors).forEach((errorMessages: any) => {
              if (Array.isArray(errorMessages)) {
                errorMessages.forEach((msg: string) => message.error(msg));
              }
            });
          } else {
            message.error(response.data?.message || '请求参数错误');
          }
          break;

        case 500:
          message.error('服务器内部错误，请稍后重试');
          break;

        default:
          message.error(response.data?.message || '请求失败，请稍后重试');
      }
    } else if (error.code === 'ECONNABORTED') {
      message.error('请求超时，请检查网络连接');
    } else {
      message.error('网络错误，请检查网络连接');
    }

    return Promise.reject(error);
  }
);

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message?: string;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T = any> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// 通用API方法
export const api = {
  // GET请求
  get: <T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> => {
    return apiClient.get(url, config);
  },

  // POST请求
  post: <T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> => {
    return apiClient.post(url, data, config);
  },

  // PUT请求
  put: <T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> => {
    return apiClient.put(url, data, config);
  },

  // PATCH请求
  patch: <T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> => {
    return apiClient.patch(url, data, config);
  },

  // DELETE请求
  delete: <T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> => {
    return apiClient.delete(url, config);
  },

  // 文件上传
  upload: <T = any>(
    url: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<AxiosResponse<T>> => {
    const formData = new FormData();
    formData.append('file', file);

    return apiClient.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: progressEvent => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(progress);
        }
      },
    });
  },

  // 文件下载
  download: (url: string, filename?: string): Promise<void> => {
    return apiClient
      .get(url, {
        responseType: 'blob',
      })
      .then(response => {
        const blob = new Blob([response.data]);
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename || 'download';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);
      });
  },
};

// 导出apiClient实例供其他模块使用
export { apiClient };
export default apiClient;
