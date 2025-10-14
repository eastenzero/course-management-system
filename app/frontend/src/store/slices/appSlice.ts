import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { AppState, Notification, ThemeConfig } from '../../types/index';

// 初始状态
const initialState: AppState = {
  theme: {
    primaryColor: '#1890ff',
    mode: 'light',
    compact: false,
  },
  sidebarCollapsed: false,
  loading: false,
  notifications: [],
};

// 创建slice
const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    // 主题设置
    setTheme: (state, action: PayloadAction<Partial<ThemeConfig>>) => {
      state.theme = { ...state.theme, ...action.payload };
    },
    toggleThemeMode: state => {
      state.theme.mode = state.theme.mode === 'light' ? 'dark' : 'light';
    },
    setPrimaryColor: (state, action: PayloadAction<string>) => {
      state.theme.primaryColor = action.payload;
    },
    toggleCompactMode: state => {
      state.theme.compact = !state.theme.compact;
    },

    // 侧边栏控制
    toggleSidebar: state => {
      state.sidebarCollapsed = !state.sidebarCollapsed;
    },
    setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
      state.sidebarCollapsed = action.payload;
    },

    // 全局加载状态
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },

    // 通知管理
    addNotification: (
      state,
      action: PayloadAction<Omit<Notification, 'id' | 'timestamp'>>
    ) => {
      const notification: Notification = {
        ...action.payload,
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        read: false,
      };
      state.notifications.unshift(notification);

      // 限制通知数量，最多保留50条
      if (state.notifications.length > 50) {
        state.notifications = state.notifications.slice(0, 50);
      }
    },

    markNotificationAsRead: (state, action: PayloadAction<string>) => {
      const notification = state.notifications.find(
        n => n.id === action.payload
      );
      if (notification) {
        notification.read = true;
      }
    },

    markAllNotificationsAsRead: state => {
      state.notifications.forEach(notification => {
        notification.read = true;
      });
    },

    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(
        n => n.id !== action.payload
      );
    },

    clearNotifications: state => {
      state.notifications = [];
    },

    // 批量操作
    clearReadNotifications: state => {
      state.notifications = state.notifications.filter(n => !n.read);
    },
  },
});

export const {
  setTheme,
  toggleThemeMode,
  setPrimaryColor,
  toggleCompactMode,
  toggleSidebar,
  setSidebarCollapsed,
  setLoading,
  addNotification,
  markNotificationAsRead,
  markAllNotificationsAsRead,
  removeNotification,
  clearNotifications,
  clearReadNotifications,
} = appSlice.actions;

export default appSlice.reducer;

// 选择器
export const selectTheme = (state: { app: AppState }) => state.app.theme;
export const selectSidebarCollapsed = (state: { app: AppState }) =>
  state.app.sidebarCollapsed;
export const selectLoading = (state: { app: AppState }) => state.app.loading;
export const selectNotifications = (state: { app: AppState }) =>
  state.app.notifications;
export const selectUnreadNotifications = (state: { app: AppState }) =>
  state.app.notifications.filter(n => !n.read);
export const selectUnreadNotificationCount = (state: { app: AppState }) =>
  state.app.notifications.filter(n => !n.read).length;
