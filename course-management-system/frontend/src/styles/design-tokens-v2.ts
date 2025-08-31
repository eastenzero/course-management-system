/**
 * Design Tokens V2 - Based on UI Redesign Specification
 * 基于设计规范的完整Design Tokens系统
 */

// 莫奈主题色板 - 水彩柔光、空气感、淡高光
export const monetThemes = {
  a: {
    name: '清晨湖畔',
    primary: '#A9D6E5',
    secondary: '#89C2D9', 
    tertiary: '#B8E0D2',
    accent: '#CDB4DB',
    neutral: '#E6E8EB'
  },
  b: {
    name: '晨光花园',
    primary: '#FFF1B6',
    secondary: '#BEE1D9',
    tertiary: '#F6C7C7', 
    accent: '#D9C2E9',
    neutral: '#F2F4F6'
  },
  c: {
    name: '海风与薰衣',
    primary: '#B6D0E2',
    secondary: '#F5E7A1',
    tertiary: '#D8CBE6',
    accent: '#BFD8CC', 
    neutral: '#E9ECEF'
  }
} as const;

// 莫兰迪主题色板 - 低饱和灰调、静谧克制
export const morandiThemes = {
  a: {
    name: '岩石与苔',
    primary: '#A3B18A',
    secondary: '#CFC9C2',
    tertiary: '#CDB4BD',
    accent: '#A7A9C9',
    neutral: '#D8C3A5'
  },
  b: {
    name: '燕麦与石墨',
    primary: '#D9CEC1', 
    secondary: '#8A8FA3',
    tertiary: '#B08A8A',
    accent: '#9C93A7',
    neutral: '#8FA08C'
  },
  c: {
    name: '陶瓷与烟灰',
    primary: '#C9C3BB',
    secondary: '#A0A7B5', 
    tertiary: '#C6A6A6',
    accent: '#AEB8A3',
    neutral: '#EFEEEA'
  }
} as const;

// 功能色
export const functionalColors = {
  success: {
    monet: '#6BAF92',
    morandi: '#6E9B7F'
  },
  warning: {
    monet: '#D8A657', 
    morandi: '#C7934B'
  },
  error: {
    monet: '#B55A5A',
    morandi: '#A35555'
  },
  info: {
    monet: '#6F90B6',
    morandi: '#6E86A8'
  }
} as const;

// 中性色系统
export const neutralColors = {
  bg: {
    0: 'var(--neutral-bg-primary)',
    1: 'var(--neutral-bg-secondary)', 
    2: 'var(--neutral-bg-tertiary)'
  },
  text: {
    1: 'var(--neutral-text-primary)',
    2: 'var(--neutral-text-secondary)',
    3: 'var(--neutral-text-tertiary)'
  },
  border: 'var(--neutral-border)'
} as const;

// 玻璃拟态效果参数 - 符合设计规范
export const glassTokens = {
  alpha: {
    light: {
      primary: 0.60,
      secondary: 0.55,
      tertiary: 0.68
    },
    dark: {
      primary: 0.35,
      secondary: 0.28,
      tertiary: 0.40
    }
  },
  // 纹理与颗粒
  noise: {
    opacity: 0.03, // 2-4% 低频细颗粒噪点
    size: '100px'
  }
} as const;

// 效果系统
export const effectTokens = {
  blur: {
    sm: '8px',
    md: '16px', 
    lg: '24px'
  },
  shadow: {
    sm: {
      y: '8px',
      blur: '24px',
      alpha: '0.08'
    },
    md: {
      y: '16px', 
      blur: '32px',
      alpha: '0.10'
    },
    lg: {
      y: '24px',
      blur: '48px', 
      alpha: '0.12'
    }
  },
  highlight: {
    alpha: {
      light: '0.35',
      dark: '0.30'
    },
    width: '1px'
  }
} as const;

// 圆角系统 - 符合设计规范
export const radiusTokens = {
  sm: '8px',
  md: '12px',
  lg: '16px',
  xl: '20px',
  xxl: '24px',
  button: '10px',    // 按钮 10-12
  card: '16px',      // 卡片 16
  modal: '20px',     // 弹窗/抽屉 20-24
  drawer: '24px',    // 抽屉
  pill: '9999px'     // 胶囊控件全圆角
} as const;

// 间距系统 - 基于8pt网格
export const spacingTokens = {
  xs: '4px',
  sm: '8px', 
  md: '16px',
  lg: '24px',
  xl: '32px',
  xxl: '48px'
} as const;

// 动效系统
export const motionTokens = {
  duration: {
    fast: '150ms',
    normal: '200ms',
    slow: '250ms',
    enter: '200ms',
    exit: '150ms'
  },
  easing: {
    standard: 'cubic-bezier(0.22, 1, 0.36, 1)',
    decelerate: 'cubic-bezier(0.0, 0.0, 0.2, 1)',
    accelerate: 'cubic-bezier(0.4, 0.0, 1, 1)'
  }
} as const;

// 字体系统
export const typographyTokens = {
  lineHeight: {
    tight: '1.2',
    normal: '1.5', 
    relaxed: '1.6',
    loose: '1.8'
  },
  fontWeight: {
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700'
  }
} as const;

// 响应式断点
export const breakpointTokens = {
  sm: '576px',
  md: '768px',
  lg: '992px', 
  xl: '1200px',
  xxl: '1440px'
} as const;

// 主题类型定义
export type MonetThemeKey = keyof typeof monetThemes;
export type MorandiThemeKey = keyof typeof morandiThemes;
export type UIThemeKey = MonetThemeKey | MorandiThemeKey;
export type ThemeCategory = 'monet' | 'morandi';
export type ThemeMode = 'light' | 'dark';

// 完整的Design Tokens对象 - 符合规范结构
export const designTokens = {
  color: {
    monet: monetThemes,
    morandi: morandiThemes,
    functional: functionalColors,
    neutral: neutralColors
  },
  surface: {
    glass: glassTokens
  },
  effect: effectTokens,
  radius: radiusTokens,
  spacing: spacingTokens,
  motion: motionTokens,
  typography: typographyTokens,
  breakpoints: breakpointTokens
} as const;

// 工具函数：获取主题颜色 - 添加缓存优化
const themeCache = new Map<string, any>();

export function getThemeColors(category: UIThemeCategory, themeKey: UIThemeKey) {
  // 创建缓存键
  const cacheKey = `${category}-${themeKey}`;
  
  // 检查缓存
  if (themeCache.has(cacheKey)) {
    return themeCache.get(cacheKey);
  }

  const themes = category === 'monet' ? monetThemes : morandiThemes;
  
  // 确保 themeKey 是有效的
  const validKeys = Object.keys(themes);
  if (!validKeys.includes(themeKey)) {
    // 仅在开发环境输出警告
    if (process.env.NODE_ENV === 'development') {
      console.warn('无效的主题键:', { themeKey, validKeys });
    }
    const fallbackResult = themes[validKeys[0] as keyof typeof themes];
    themeCache.set(cacheKey, fallbackResult);
    return fallbackResult;
  }

  const result = themes[themeKey as keyof typeof themes];
  
  // 存储到缓存
  themeCache.set(cacheKey, result);
  
  return result;
}

// 工具函数：获取功能色
export function getFunctionalColor(type: keyof typeof functionalColors, category: UIThemeCategory) {
  return functionalColors[type][category];
}

// 工具函数：生成CSS变量
export function generateCSSVariables(
  category: UIThemeCategory,
  themeKey: UIThemeKey,
  mode: UIThemeMode = 'light'
) {
  const theme = getThemeColors(category, themeKey);
  if (!theme) {
    console.warn('无法获取主题颜色:', { category, themeKey });
    return {};
  }

  const variables: Record<string, string> = {
    // 主题颜色
    '--color-primary': theme.primary,
    '--color-secondary': theme.secondary,
    '--color-tertiary': theme.tertiary,
    '--color-accent': theme.accent,
    '--color-neutral': theme.neutral,

    // 功能色
    '--color-success': getFunctionalColor('success', category),
    '--color-warning': getFunctionalColor('warning', category),
    '--color-error': getFunctionalColor('error', category),
    '--color-info': getFunctionalColor('info', category),

    // 玻璃效果
    '--glass-alpha-primary': glassTokens.alpha[mode].primary.toString(),
    '--glass-alpha-secondary': glassTokens.alpha[mode].secondary.toString(),
    '--glass-alpha-tertiary': glassTokens.alpha[mode].tertiary.toString(),

    // 模糊效果
    '--blur-sm': effectTokens.blur.sm,
    '--blur-md': effectTokens.blur.md,
    '--blur-lg': effectTokens.blur.lg,

    // 阴影
    '--shadow-sm': `0 ${effectTokens.shadow.sm.y} ${effectTokens.shadow.sm.blur} rgba(0, 0, 0, ${effectTokens.shadow.sm.alpha})`,
    '--shadow-md': `0 ${effectTokens.shadow.md.y} ${effectTokens.shadow.md.blur} rgba(0, 0, 0, ${effectTokens.shadow.md.alpha})`,
    '--shadow-lg': `0 ${effectTokens.shadow.lg.y} ${effectTokens.shadow.lg.blur} rgba(0, 0, 0, ${effectTokens.shadow.lg.alpha})`,

    // 高光
    '--highlight-alpha': effectTokens.highlight.alpha[mode],
    '--highlight-width': effectTokens.highlight.width,

    // 圆角
    '--radius-sm': radiusTokens.sm,
    '--radius-md': radiusTokens.md,
    '--radius-lg': radiusTokens.lg,
    '--radius-xl': radiusTokens.xl,
    '--radius-xxl': radiusTokens.xxl,
    '--radius-button': radiusTokens.button,
    '--radius-card': radiusTokens.card,
    '--radius-modal': radiusTokens.modal,
    '--radius-pill': radiusTokens.pill,

    // 间距
    '--spacing-xs': spacingTokens.xs,
    '--spacing-sm': spacingTokens.sm,
    '--spacing-md': spacingTokens.md,
    '--spacing-lg': spacingTokens.lg,
    '--spacing-xl': spacingTokens.xl,
    '--spacing-xxl': spacingTokens.xxl,

    // 动效
    '--duration-fast': motionTokens.duration.fast,
    '--duration-normal': motionTokens.duration.normal,
    '--duration-slow': motionTokens.duration.slow,
    '--duration-enter': motionTokens.duration.enter,
    '--duration-exit': motionTokens.duration.exit,
    '--easing-standard': motionTokens.easing.standard,
    '--easing-decelerate': motionTokens.easing.decelerate,
    '--easing-accelerate': motionTokens.easing.accelerate,

    // 字体
    '--line-height-tight': typographyTokens.lineHeight.tight,
    '--line-height-normal': typographyTokens.lineHeight.normal,
    '--line-height-relaxed': typographyTokens.lineHeight.relaxed,
    '--line-height-loose': typographyTokens.lineHeight.loose,
    '--font-weight-normal': typographyTokens.fontWeight.normal,
    '--font-weight-medium': typographyTokens.fontWeight.medium,
    '--font-weight-semibold': typographyTokens.fontWeight.semibold,
    '--font-weight-bold': typographyTokens.fontWeight.bold
  };

  // 根据模式设置中性色
  if (mode === 'light') {
    variables['--neutral-bg-primary'] = '#ffffff';
    variables['--neutral-bg-secondary'] = '#fafafa';
    variables['--neutral-bg-tertiary'] = '#f5f5f5';
    variables['--neutral-text-primary'] = '#262626';
    variables['--neutral-text-secondary'] = '#595959';
    variables['--neutral-text-tertiary'] = '#8c8c8c';
    variables['--neutral-border'] = '#e8e8e8';
  } else {
    variables['--neutral-bg-primary'] = '#141414';
    variables['--neutral-bg-secondary'] = '#1f1f1f';
    variables['--neutral-bg-tertiary'] = '#262626';
    variables['--neutral-text-primary'] = '#ffffff';
    variables['--neutral-text-secondary'] = '#d9d9d9';
    variables['--neutral-text-tertiary'] = '#8c8c8c';
    variables['--neutral-border'] = '#424242';
  }

  return variables;
}

// 应用主题到DOM - 添加防抖优化
let applyThemeTimeout: NodeJS.Timeout | null = null;

export function applyThemeTokens(
  category: UIThemeCategory,
  themeKey: UIThemeKey,
  mode: UIThemeMode = 'light'
) {
  // 防抖处理，避免频繁应用主题
  if (applyThemeTimeout) {
    clearTimeout(applyThemeTimeout);
  }
  
  applyThemeTimeout = setTimeout(() => {
    const variables = generateCSSVariables(category, themeKey, mode);
    const root = document.documentElement;

    // 设置data属性
    root.setAttribute('data-theme-category', category);
    root.setAttribute('data-theme-key', themeKey);
    root.setAttribute('data-theme-mode', mode);

    // 应用CSS变量
    Object.entries(variables).forEach(([key, value]) => {
      root.style.setProperty(key, value);
    });

    // 仅在开发环境输出日志
    if (process.env.NODE_ENV === 'development') {
      console.log('应用主题:', { category, themeKey, mode });
    }
  }, 16); // 16ms防抖
}

// 默认导出
export default designTokens;