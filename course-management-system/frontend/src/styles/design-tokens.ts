/**
 * Design Tokens for UI Redesign
 * Based on Monet/Morandi aesthetic with Glassmorphism effects
 */

// 莫奈主题色板 - 水彩柔光、空气感、淡高光
export const monetThemes = {
  clearMorningLake: {
    name: '清晨湖畔',
    primary: '#A9D6E5',
    secondary: '#89C2D9',
    tertiary: '#B8E0D2',
    accent: '#CDB4DB',
    neutral: '#E6E8EB',
    functional: {
      success: '#6BAF92',
      warning: '#D8A657',
      error: '#B55A5A',
      info: '#6F90B6'
    }
  },
  morningGarden: {
    name: '晨光花园',
    primary: '#FFF1B6',
    secondary: '#BEE1D9',
    tertiary: '#F6C7C7',
    accent: '#D9C2E9',
    neutral: '#F2F4F6',
    functional: {
      success: '#77B39A',
      warning: '#D3A24E',
      error: '#B76A6A',
      info: '#7C98BE'
    }
  },
  seaBreezeLavender: {
    name: '海风与薰衣',
    primary: '#B6D0E2',
    secondary: '#F5E7A1',
    tertiary: '#D8CBE6',
    accent: '#BFD8CC',
    neutral: '#E9ECEF',
    functional: {
      success: '#73A890',
      warning: '#D1A14C',
      error: '#B16464',
      info: '#6E8FB1'
    }
  }
} as const;

// 莫兰迪主题色板 - 低饱和灰调、静谧克制
export const morandiThemes = {
  rockAndMoss: {
    name: '岩石与苔',
    primary: '#A3B18A',
    secondary: '#CFC9C2',
    tertiary: '#CDB4BD',
    accent: '#A7A9C9',
    neutral: '#D8C3A5',
    functional: {
      success: '#6E9B7F',
      warning: '#C7934B',
      error: '#A35555',
      info: '#6E86A8'
    }
  },
  oatAndGraphite: {
    name: '燕麦与石墨',
    primary: '#D9CEC1',
    secondary: '#8A8FA3',
    tertiary: '#B08A8A',
    accent: '#9C93A7',
    neutral: '#8FA08C',
    functional: {
      success: '#6C927A',
      warning: '#C28D47',
      error: '#A05C5C',
      info: '#6D85A2'
    }
  },
  ceramicAndAsh: {
    name: '陶瓷与烟灰',
    primary: '#C9C3BB',
    secondary: '#A0A7B5',
    tertiary: '#C6A6A6',
    accent: '#AEB8A3',
    neutral: '#EFEEEA',
    functional: {
      success: '#6A927A',
      warning: '#C0924A',
      error: '#A05A5A',
      info: '#6D86A5'
    }
  }
} as const;

// 玻璃拟态效果参数
export const glassTokens = {
  blur: {
    sm: '8px',
    md: '16px',
    lg: '24px'
  },
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
  highlight: {
    alpha: {
      light: 0.35,
      dark: 0.30
    },
    width: '1px'
  },
  shadow: {
    sm: {
      y: 8,
      blur: 24,
      alpha: 0.08
    },
    md: {
      y: 16,
      blur: 32,
      alpha: 0.10
    },
    lg: {
      y: 24,
      blur: 48,
      alpha: 0.12
    }
  }
} as const;

// 圆角系统
export const radiusTokens = {
  sm: '8px',
  md: '12px',
  lg: '16px',
  xl: '20px',
  xxl: '24px',
  button: '10px',
  card: '16px',
  modal: '20px',
  pill: '9999px'
} as const;

// 间距系统 (8pt grid)
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
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.6,
    loose: 1.8
  },
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700
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
export type ThemeCategory = 'monet' | 'morandi';
export type ThemeMode = 'light' | 'dark';

// 完整主题配置接口
export interface DesignTokens {
  category: ThemeCategory;
  themeKey: MonetThemeKey | MorandiThemeKey;
  mode: ThemeMode;
  colors: typeof monetThemes[MonetThemeKey] | typeof morandiThemes[MorandiThemeKey];
  glass: typeof glassTokens;
  radius: typeof radiusTokens;
  spacing: typeof spacingTokens;
  motion: typeof motionTokens;
  typography: typeof typographyTokens;
  breakpoints: typeof breakpointTokens;
}

// 默认主题配置
export const defaultTokens: DesignTokens = {
  category: 'monet',
  themeKey: 'clearMorningLake',
  mode: 'light',
  colors: monetThemes.clearMorningLake,
  glass: glassTokens,
  radius: radiusTokens,
  spacing: spacingTokens,
  motion: motionTokens,
  typography: typographyTokens,
  breakpoints: breakpointTokens
};
