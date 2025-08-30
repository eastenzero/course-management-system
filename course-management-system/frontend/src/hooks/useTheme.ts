import React, { useState, useEffect, useContext, createContext } from 'react';
import { ThemeConfig } from 'antd';
import { modernTheme, teacherTheme, studentTheme } from '../styles/theme';
import {
  ThemeCategory,
  MonetThemeKey,
  MorandiThemeKey,
  ThemeMode,
  monetThemes,
  morandiThemes
} from '../styles/design-tokens';
import { applyTheme, restoreTheme } from '../styles/css-variables';
import { getThemeConfig } from '../styles/enhanced-theme';

export type ThemeType = 'modern' | 'teacher' | 'student';
export type UserRole = 'admin' | 'teacher' | 'student';

// 新的主题类型
export type UIThemeCategory = ThemeCategory;
export type UIThemeKey = MonetThemeKey | MorandiThemeKey;
export type UIThemeMode = ThemeMode;

interface ThemeContextType {
  // 原有主题系统
  currentTheme: ThemeType;
  antdTheme: ThemeConfig;
  setTheme: (theme: ThemeType) => void;
  setUserRole: (role: UserRole) => void;
  userRole: UserRole | null;

  // 新的UI主题系统
  uiTheme: {
    category: UIThemeCategory;
    themeKey: UIThemeKey;
    mode: UIThemeMode;
  };
  setUITheme: (category: UIThemeCategory, themeKey: UIThemeKey, mode?: UIThemeMode) => void;
  toggleMode: () => void;
  getThemeColors: () => any;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const useThemeProvider = () => {
  const [currentTheme, setCurrentTheme] = useState<ThemeType>('modern');
  const [userRole, setUserRole] = useState<UserRole | null>(null);

  // 新的UI主题状态
  const [uiTheme, setUIThemeState] = useState<{
    category: UIThemeCategory;
    themeKey: UIThemeKey;
    mode: UIThemeMode;
  }>({
    category: 'monet',
    themeKey: 'a',
    mode: 'light'
  });

  // 根据用户角色自动设置主题
  useEffect(() => {
    if (userRole === 'teacher') {
      setCurrentTheme('teacher');
      // 教师端推荐莫兰迪主题
      setUIThemeState(prev => ({ ...prev, category: 'morandi', themeKey: 'a' }));
    } else if (userRole === 'student') {
      setCurrentTheme('student');
      // 学生端推荐莫奈主题
      setUIThemeState(prev => ({ ...prev, category: 'monet', themeKey: 'a' }));
    } else {
      setCurrentTheme('modern');
    }
  }, [userRole]);

  // 从localStorage加载主题设置
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as ThemeType;
    const savedRole = localStorage.getItem('userRole') as UserRole;

    if (savedTheme) {
      setCurrentTheme(savedTheme);
    }
    if (savedRole) {
      setUserRole(savedRole);
    }

    // 恢复UI主题设置
    const restoredUITheme = restoreTheme();
    setUIThemeState(restoredUITheme);
  }, []);

  // 保存主题设置到localStorage
  useEffect(() => {
    localStorage.setItem('theme', currentTheme);
  }, [currentTheme]);

  useEffect(() => {
    if (userRole) {
      localStorage.setItem('userRole', userRole);
    }
  }, [userRole]);

  // 应用UI主题变化
  useEffect(() => {
    applyTheme(uiTheme.category, uiTheme.themeKey, uiTheme.mode);
  }, [uiTheme]);

  const getAntdTheme = (): ThemeConfig => {
    // 优先使用新的增强主题
    const enhancedTheme = getThemeConfig(uiTheme.category, uiTheme.themeKey);
    if (enhancedTheme) {
      return enhancedTheme;
    }

    // 回退到原有主题
    switch (currentTheme) {
      case 'teacher':
        return teacherTheme;
      case 'student':
        return studentTheme;
      default:
        return modernTheme;
    }
  };

  const setTheme = (theme: ThemeType) => {
    setCurrentTheme(theme);
  };

  const setRole = (role: UserRole) => {
    setUserRole(role);
  };

  // 新的UI主题方法
  const setUITheme = (category: UIThemeCategory, themeKey: UIThemeKey, mode?: UIThemeMode) => {
    setUIThemeState(prev => ({
      category,
      themeKey,
      mode: mode || prev.mode
    }));
  };

  const toggleMode = () => {
    setUIThemeState(prev => ({
      ...prev,
      mode: prev.mode === 'light' ? 'dark' : 'light'
    }));
  };

  const getThemeColors = () => {
    return getThemeColors(uiTheme.category, uiTheme.themeKey);
  };

  // 应用主题到DOM
  const applyCurrentTheme = () => {
    applyThemeTokens(uiTheme.category, uiTheme.themeKey, uiTheme.mode);
  };

  // 监听主题变化并应用
  useEffect(() => {
    applyCurrentTheme();
    // 保存到localStorage
    localStorage.setItem('ui-theme-category', uiTheme.category);
    localStorage.setItem('ui-theme-key', uiTheme.themeKey);
    localStorage.setItem('ui-theme-mode', uiTheme.mode);
  }, [uiTheme]);

  // 从localStorage恢复主题
  useEffect(() => {
    const savedCategory = localStorage.getItem('ui-theme-category') as UIThemeCategory;
    const savedThemeKey = localStorage.getItem('ui-theme-key') as UIThemeKey;
    const savedMode = localStorage.getItem('ui-theme-mode') as UIThemeMode;

    if (savedCategory && savedThemeKey && savedMode) {
      setUIThemeState({
        category: savedCategory,
        themeKey: savedThemeKey,
        mode: savedMode
      });
    }
  }, []);

  return {
    currentTheme,
    antdTheme: getAntdTheme(),
    setTheme,
    setUserRole: setRole,
    userRole,
    uiTheme,
    setUITheme,
    toggleMode,
    getThemeColors,
    applyCurrentTheme,
    designTokens
  };
};

export const ThemeProvider = ({ children }: { children: React.ReactNode }) => {
  const themeValue = useThemeProvider();

  return React.createElement(ThemeContext.Provider, { value: themeValue }, children);
};
