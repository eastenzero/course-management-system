import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';

import App from './App';
import { store } from './store/index';
import { RoutePreloader } from './utils/lazyRoutes';
import { modernTheme } from './styles/theme';
import { ThemeProvider, useTheme } from './hooks/useThemeV2';
import './styles/enhanced-css-variables.css';
import './styles/glass-variables.css';
import { AccessibilityUtils } from './utils/accessibility';
import { PerformanceUtils } from './utils/performance';
import { glassOptimizer } from './utils/glassEffectOptimizer';

// 设置dayjs中文
dayjs.locale('zh-cn');

// 性能监控（仅在必要时开启）
if ((import.meta as any).env?.VITE_VERBOSE_LOGS === 'true' && false) { // 默认禁用详细性能监控
  // 监控性能指标
  if ('PerformanceObserver' in window) {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        // 只记录重要的性能指标
        if (entry.duration > 1000) { // 只记录超过1秒的操作
          console.log('[Performance]', entry.name, entry.duration);
        }
      }
    });
    observer.observe({ entryTypes: ['measure', 'navigation'] });
  }
}

// 初始化缓存预热（仅预热不需要认证的数据）
const initializeCache = async () => {
  try {
    // 只预热不需要认证的数据，认证相关的数据在用户登录后预热
    if ((import.meta as any).env?.VITE_VERBOSE_LOGS === 'true') {
      console.log('[Cache] Initial cache warming completed');
    }
  } catch (error) {
    if ((import.meta as any).env?.VITE_VERBOSE_LOGS === 'true') {
      console.warn('[Cache] Cache warming failed:', error);
    }
  }
};

// 根据用户角色预加载路由
const initializeRoutePreloading = async () => {
  try {
    // 获取用户信息（如果已登录）
    const userInfo = localStorage.getItem('user');
    if (userInfo) {
      const user = JSON.parse(userInfo);
      await RoutePreloader.preloadByUserRole(user.user_type);
      if ((import.meta as any).env?.VITE_VERBOSE_LOGS === 'true') {
        console.log('[Routes] Route preloading completed for role:', user.user_type);
      }
    }
  } catch (error) {
    if ((import.meta as any).env?.VITE_VERBOSE_LOGS === 'true') {
      console.warn('[Routes] Route preloading failed:', error);
    }
  }
};

// 导入样式
import './styles/global.css';
import './styles/variables.css';
import './styles/modern.css';
import './styles/enhanced-css-variables.css';
import './styles/glass-fallback.css';
import './styles/accessibility.css';
import './styles/forced-colors-polyfill.css'; // 现代强制颜色模式支持

// 应用启动时初始化
const initializeApp = async () => {
  // 初始化无障碍功能
  AccessibilityUtils.FocusManager.enhanceFocusVisibility();
  AccessibilityUtils.Internationalization.applyTextDirection();

  // 初始化性能优化
  PerformanceUtils.NetworkOptimization.adaptToNetwork();
  PerformanceUtils.ImageOptimization.lazyLoadImages();

  // 初始化玻璃效果优化器
  glassOptimizer.setOptimizationLevel('auto');

  // 并行执行初始化任务
  await Promise.allSettled([
    initializeCache(),
    initializeRoutePreloading(),
  ]);
};

// 主题包装组件
const ThemedApp = () => {
  const { antdTheme } = useTheme();

  return (
    <ConfigProvider locale={zhCN} theme={antdTheme}>
      <App />
    </ConfigProvider>
  );
};

// 启动应用
const startApp = () => {
  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <Provider store={store}>
        <BrowserRouter>
          <ThemeProvider>
            <ThemedApp />
          </ThemeProvider>
        </BrowserRouter>
      </Provider>
    </React.StrictMode>
  );

  // 应用启动后执行初始化
  initializeApp();
};

// 启动应用
startApp();
