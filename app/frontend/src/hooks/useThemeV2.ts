import React, { useState, useEffect, useContext, createContext, useMemo, useCallback } from 'react';
import { ThemeConfig } from 'antd';
import { modernTheme, teacherTheme, studentTheme } from '../styles/theme';
import { 
  applyThemeTokens, 
  getThemeColors, 
  generateCSSVariables,
  designTokens,
  monetThemes,
  morandiThemes,
  type ThemeCategory, 
  type ThemeMode,
  type MonetThemeKey,
  type MorandiThemeKey
} from '../styles/design-tokens-v2';
import { createEnhancedTheme, getEnhancedThemeConfig } from '../styles/enhanced-theme-v2';

// 主题类型定义
export type ThemeType = 'modern' | 'teacher' | 'student';
export type UserRole = 'teacher' | 'student' | 'admin' | 'academic_admin';
export type UIThemeCategory = ThemeCategory;
export type UIThemeKey = MonetThemeKey | MorandiThemeKey;
export type UIThemeMode = ThemeMode;

interface ThemeContextType {
  // 原有主题系统
  currentTheme: string;
  antdTheme: ThemeConfig;
  setTheme: (themeKey: string) => void;
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
  applyCurrentTheme: () => void;
  designTokens: typeof designTokens;
  
  // 主题数据导出
  monetThemes: typeof monetThemes;
  morandiThemes: typeof morandiThemes;
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
  // 生成默认主题（固定为浅色）
  const generateDefaultTheme = (): { category: UIThemeCategory; themeKey: UIThemeKey; mode: UIThemeMode } => {
    return {
      category: 'monet',
      themeKey: 'a',
      mode: 'light' // 固定为浅色主题
    };
  };

  // 从localStorage加载主题，如果没有则生成随机主题
  const loadThemeFromStorage = useMemo((): { category: UIThemeCategory; themeKey: UIThemeKey; mode: UIThemeMode } => {
    try {
      const savedTheme = localStorage.getItem('ui-theme-v2');
      if (savedTheme) {
        const parsed = JSON.parse(savedTheme);
        // 验证主题数据的有效性
        if (parsed.category && parsed.themeKey && parsed.mode) {
          if (process.env.NODE_ENV === 'development') {
            console.log('从localStorage加载主题:', parsed);
          }
          return parsed;
        }
      }
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.warn('加载主题失败:', error);
      }
    }

    // 如果没有保存的主题或加载失败，使用默认浅色主题
    const defaultTheme = generateDefaultTheme();
    if (process.env.NODE_ENV === 'development') {
      console.log('使用默认浅色主题:', defaultTheme);
    }
    return defaultTheme;
  }, []); // 空依赖数组，只在组件初始化时计算一次

  const [uiTheme, setUIThemeState] = useState<{
    category: UIThemeCategory;
    themeKey: UIThemeKey;
    mode: UIThemeMode;
  }>(() => loadThemeFromStorage); // 使用函数初始化避免每次渲染都调用

  // 合并localStorage操作，减少多个useEffect
  useEffect(() => {
    // 从 localStorage 恢复主题
    const savedTheme = localStorage.getItem('theme') as ThemeType;
    const savedRole = localStorage.getItem('userRole') as UserRole;
    
    if (savedTheme) {
      setCurrentTheme(savedTheme);
    }
    if (savedRole) {
      setUserRole(savedRole);
    }
    
    // 初始化时应用主题
    applyThemeTokens(uiTheme.category, uiTheme.themeKey, uiTheme.mode);
  }, []); // 只在组件挂载时执行一次

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
    } else if (userRole === 'admin' || userRole === 'academic_admin') {
      setCurrentTheme('modern');
    }
  }, [userRole]);

  // 保存主题设置到localStorage
  useEffect(() => {
    localStorage.setItem('theme', currentTheme);
  }, [currentTheme]);

  useEffect(() => {
    if (userRole) {
      localStorage.setItem('userRole', userRole);
    }
  }, [userRole]);

  const getAntdTheme = (): ThemeConfig => {
    // 使用新的增强主题系统
    try {
      return getEnhancedThemeConfig(uiTheme.category, uiTheme.themeKey);
    } catch (error) {
      console.warn('Failed to get enhanced theme, falling back to default:', error);
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

  const setTheme = (themeKey: string) => {
    // 解析主题键，支持 'monet-a', 'morandi-b' 格式
    if (themeKey.includes('-')) {
      const [category, key] = themeKey.split('-');
      const validMonetKeys = ['a', 'b', 'c'];
      const validMorandiKeys = ['a', 'b', 'c'];

      if (category === 'monet' && validMonetKeys.includes(key)) {
        setUITheme(category as UIThemeCategory, key as UIThemeKey);
        return;
      }
      if (category === 'morandi' && validMorandiKeys.includes(key)) {
        setUITheme(category as UIThemeCategory, key as UIThemeKey);
        return;
      }
    }

    // 原有主题系统
    if (['modern', 'teacher', 'student'].includes(themeKey)) {
      setCurrentTheme(themeKey as ThemeType);
    }
  };

  const setRole = (role: UserRole) => {
    setUserRole(role);
  };

  // 新的UI主题方法
  const setUITheme = (category: UIThemeCategory, themeKey: UIThemeKey, mode?: UIThemeMode) => {
    const newTheme = {
      category,
      themeKey,
      mode: mode || uiTheme.mode
    };

    setUIThemeState(newTheme);

    // 立即应用主题
    applyThemeTokens(category, themeKey, newTheme.mode);

    // 保存主题到localStorage
    try {
      localStorage.setItem('ui-theme-v2', JSON.stringify(newTheme));
      if (process.env.NODE_ENV === 'development') {
        console.log('主题已保存到localStorage:', newTheme);
      }
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.warn('保存主题失败:', error);
      }
    }
  };

  const toggleMode = () => {
    const newMode: UIThemeMode = uiTheme.mode === 'light' ? 'dark' : 'light';
    setUITheme(uiTheme.category, uiTheme.themeKey, newMode);
  };

  const getCurrentThemeColors = useMemo(() => {
    return getThemeColors(uiTheme.category, uiTheme.themeKey);
  }, [uiTheme.category, uiTheme.themeKey]); // 仅在主题变化时重新计算

  // 应用主题到DOM
  const applyCurrentTheme = () => {
    applyThemeTokens(uiTheme.category, uiTheme.themeKey, uiTheme.mode);
  };

  return {
    currentTheme: `${uiTheme.category}-${uiTheme.themeKey}`,
    antdTheme: getAntdTheme(),
    setTheme,
    setUserRole: setRole,
    userRole,
    uiTheme,
    setUITheme,
    toggleMode,
    getThemeColors: () => getCurrentThemeColors,
    applyCurrentTheme,
    designTokens,
    monetThemes,
    morandiThemes
  };
};

export const ThemeProvider = ({ children }: { children: React.ReactNode }) => {
  const themeValue = useThemeProvider();

  return React.createElement(ThemeContext.Provider, { value: themeValue }, children);
};