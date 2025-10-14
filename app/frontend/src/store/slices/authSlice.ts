import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import type { User, LoginForm, AuthState } from '../../types/index';
import { authAPI } from '../../api/auth';
import { cacheWarmer } from '../../utils/apiCache';

// 异步thunk
export const login = createAsyncThunk(
  'auth/login',
  async (credentials: LoginForm, { rejectWithValue }) => {
    try {
      const response = await authAPI.login(credentials);
      // 后端返回格式: {code, message, data: {access, refresh, user}}
      if (response.data.code === 200) {
        const { data } = response.data;
        // 保存token到localStorage
        localStorage.setItem('token', data.access);
        localStorage.setItem('refreshToken', data.refresh);

        // 登录成功后在后台异步预热缓存，不阻塞登录响应
        setTimeout(async () => {
          try {
            await cacheWarmer.warmUpCourseData();
            console.log('[Cache] Post-login cache warming completed');
          } catch (error) {
            console.warn('[Cache] Post-login cache warming failed:', error);
          }
        }, 100);

        return data;
      } else {
        return rejectWithValue(response.data.message || '登录失败');
      }
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || '登录失败');
    }
  }
);

export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      await authAPI.logout();
      // 清除本地存储
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      return null;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || '退出失败');
    }
  }
);

export const getCurrentUser = createAsyncThunk(
  'auth/getCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authAPI.getCurrentUser();
      // 后端返回格式: {code, message, data: user}
      // 统一处理响应格式
      if (response.data.code === 200) {
        return response.data.data;
      } else {
        return rejectWithValue(response.data.message || '获取用户信息失败');
      }
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || '获取用户信息失败'
      );
    }
  }
);

export const refreshToken = createAsyncThunk(
  'auth/refreshToken',
  async (_, { rejectWithValue }) => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) {
        throw new Error('No refresh token');
      }
      const response = await authAPI.refreshToken(refreshToken);
      // 处理刷新token的响应格式
      const newToken = response.data?.access || response.data;
      localStorage.setItem('token', newToken as string);
      return { access: newToken as string };
    } catch (error: any) {
      // 刷新失败，清除所有token
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      return rejectWithValue(error.response?.data?.message || '刷新token失败');
    }
  }
);

// 初始状态
const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'), // 如果有token就认为已认证
  loading: false,
};

// 创建slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: () => {
      // 清除错误状态
    },
    setCredentials: (
      state,
      action: PayloadAction<{ user: User; token: string }>
    ) => {
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.isAuthenticated = true;
    },
    clearCredentials: state => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
    },
    initializeAuth: state => {
      // 应用启动时初始化认证状态
      const token = localStorage.getItem('token');
      const userStr = localStorage.getItem('user');
      
      if (token) {
        state.token = token;
        state.isAuthenticated = true;
        
        // 移除模拟token特殊处理，统一处理所有token
        if (userStr) {
          try {
            state.user = JSON.parse(userStr);
            state.loading = false;
          } catch (error) {
            console.warn('解析用户数据失败:', error);
            // 解析失败时需要重新获取用户信息
            state.loading = true;
          }
        } else {
          // 没有用户数据时需要获取
          state.loading = true;
        }
      } else {
        state.isAuthenticated = false;
        state.loading = false;
      }
    },
  },
  extraReducers: builder => {
    builder
      // 登录
      .addCase(login.pending, state => {
        state.loading = true;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.token = action.payload.access as string;
        state.isAuthenticated = true;
      })
      .addCase(login.rejected, state => {
        state.loading = false;
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
      })
      // 退出
      .addCase(logout.pending, state => {
        state.loading = true;
      })
      .addCase(logout.fulfilled, state => {
        state.loading = false;
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
      })
      .addCase(logout.rejected, state => {
        state.loading = false;
        // 即使退出失败，也清除本地状态
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
      })
      // 获取当前用户
      .addCase(getCurrentUser.pending, state => {
        state.loading = true;
      })
      .addCase(getCurrentUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
      })
      .addCase(getCurrentUser.rejected, state => {
        state.loading = false;
        // 获取用户信息失败时，清除认证状态
        state.user = null;
        state.isAuthenticated = false;
        // 清除无效的token
        state.token = null;
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
      })
      // 刷新token
      .addCase(refreshToken.fulfilled, (state, action) => {
        state.token = action.payload.access as string;
      })
      .addCase(refreshToken.rejected, state => {
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
      });
  },
});

export const { clearError, setCredentials, clearCredentials, initializeAuth } =
  authSlice.actions;
export default authSlice.reducer;
