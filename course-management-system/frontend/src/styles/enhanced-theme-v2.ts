import { ThemeConfig } from 'antd';
import { getThemeColors, getFunctionalColor, type ThemeCategory, type UIThemeKey } from './design-tokens-v2';

/**
 * 创建基于新Design Tokens的Ant Design主题配置
 */
export function createEnhancedTheme(
  category: ThemeCategory = 'monet',
  themeKey: UIThemeKey = 'a'
): ThemeConfig {
  const colors = getThemeColors(category, themeKey);
  
  if (!colors) {
    console.warn(`Theme not found: ${category}-${themeKey}, using fallback`);
    // 使用莫奈A作为回退
    const fallbackColors = getThemeColors('monet', 'a')!;
    return createThemeConfig(fallbackColors, 'monet');
  }

  return createThemeConfig(colors, category);
}

function createThemeConfig(colors: any, category: ThemeCategory): ThemeConfig {
  return {
    token: {
      // 主题色彩
      colorPrimary: colors.primary,
      colorSuccess: getFunctionalColor('success', category),
      colorWarning: getFunctionalColor('warning', category),
      colorError: getFunctionalColor('error', category),
      colorInfo: getFunctionalColor('info', category),

      // 文字颜色 - 根据主题类别调整
      colorText: category === 'morandi' ? '#1f1f1f' : '#262626',
      colorTextSecondary: category === 'morandi' ? '#4a4a4a' : '#595959',
      colorTextTertiary: '#8c8c8c',
      colorTextQuaternary: '#bfbfbf',

      // 背景颜色 - 使用CSS变量
      colorBgContainer: 'var(--neutral-bg-primary)',
      colorBgElevated: 'var(--neutral-bg-secondary)',
      colorBgLayout: 'var(--neutral-bg-tertiary)',
      colorBgSpotlight: colors.neutral,

      // 边框颜色
      colorBorder: 'var(--neutral-border)',
      colorBorderSecondary: 'rgba(0, 0, 0, 0.06)',

      // 字体配置 - 中文优化
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif',
      fontSize: 14,
      fontSizeLG: 16,
      fontSizeSM: 12,
      fontSizeXL: 20,
      fontSizeHeading1: 32,
      fontSizeHeading2: 24,
      fontSizeHeading3: 20,
      fontSizeHeading4: 16,
      fontSizeHeading5: 14,

      // 行高配置 - 基于Design Tokens
      lineHeight: 1.6,
      lineHeightLG: 1.5,
      lineHeightSM: 1.8,

      // 圆角配置 - 使用数值
      borderRadius: 8,
      borderRadiusLG: 16,
      borderRadiusSM: 6,
      borderRadiusXS: 4,

      // 阴影配置 - 基于Design Tokens
      boxShadow: 'var(--shadow-md)',
      boxShadowSecondary: 'var(--shadow-sm)',
      boxShadowTertiary: 'var(--shadow-lg)',

      // 间距配置 - 基于8pt网格
      padding: 16,
      paddingLG: 24,
      paddingSM: 12,
      paddingXS: 8,
      paddingXXS: 4,

      margin: 16,
      marginLG: 24,
      marginSM: 12,
      marginXS: 8,
      marginXXS: 4,

      // 控件高度
      controlHeight: 36,
      controlHeightLG: 44,
      controlHeightSM: 28,

      // 动画配置 - 基于Design Tokens
      motionDurationFast: 'var(--duration-fast)',
      motionDurationMid: 'var(--duration-normal)',
      motionDurationSlow: 'var(--duration-slow)',
      motionEaseInOut: 'var(--easing-standard)',
      motionEaseOut: 'var(--easing-decelerate)',
    },
    components: {
      Layout: {
        headerBg: 'rgba(255, 255, 255, var(--glass-alpha-secondary))',
        headerHeight: 64,
        headerPadding: '0 24px',
        siderBg: `linear-gradient(180deg, ${colors.primary}15, ${colors.secondary}10)`,
        triggerBg: 'rgba(255, 255, 255, var(--glass-alpha-primary))',
        triggerColor: colors.primary,
      },
      Menu: {
        darkItemBg: 'transparent',
        darkItemSelectedBg: `rgba(255, 255, 255, var(--glass-alpha-secondary))`,
        darkItemHoverBg: `rgba(255, 255, 255, var(--glass-alpha-primary))`,
        itemHeight: 48,
        itemMarginInline: 8,
        borderRadius: 10,
      },
      Card: {
        headerBg: 'transparent',
        headerHeight: 56,
        paddingLG: 24,
        boxShadow: 'var(--shadow-md)',
        borderRadiusLG: 16,
      },
      Button: {
        borderRadius: 10,
        controlHeight: 36,
        controlHeightLG: 44,
        controlHeightSM: 28,
        paddingInline: 16,
        paddingInlineLG: 20,
        paddingInlineSM: 12,
      },
      Input: {
        borderRadius: 8,
        controlHeight: 36,
        controlHeightLG: 44,
        controlHeightSM: 28,
        paddingInline: 12,
      },
      Select: {
        borderRadius: 8,
        controlHeight: 36,
        controlHeightLG: 44,
        controlHeightSM: 28,
      },
      Table: {
        borderRadiusLG: 12,
        headerBg: 'rgba(255, 255, 255, var(--glass-alpha-tertiary))',
        headerSplitColor: 'var(--neutral-border)',
        rowHoverBg: `${colors.primary}08`,
      },
      Modal: {
        borderRadiusLG: 20,
        paddingLG: 24,
      },
      Drawer: {
        borderRadiusLG: 16,
        paddingLG: 24,
      },
      Tooltip: {
        borderRadius: 8,
      },
      Popover: {
        borderRadiusLG: 12,
      },
      Notification: {
        borderRadiusLG: 12,
      },
      Message: {
        borderRadiusLG: 12,
      },
    },
  };
}

// 预设主题配置 - 使用新的主题键
export const monetThemeA = createEnhancedTheme('monet', 'a');
export const monetThemeB = createEnhancedTheme('monet', 'b');
export const monetThemeC = createEnhancedTheme('monet', 'c');

export const morandiThemeA = createEnhancedTheme('morandi', 'a');
export const morandiThemeB = createEnhancedTheme('morandi', 'b');
export const morandiThemeC = createEnhancedTheme('morandi', 'c');

// 默认主题
export const defaultEnhancedTheme = monetThemeA;

// 根据用户角色推荐的主题
export const teacherRecommendedTheme = morandiThemeA;
export const studentRecommendedTheme = monetThemeA;

// 主题映射 - 新结构
export const enhancedThemeMap = {
  monet: {
    a: monetThemeA,
    b: monetThemeB,
    c: monetThemeC,
  },
  morandi: {
    a: morandiThemeA,
    b: morandiThemeB,
    c: morandiThemeC,
  },
} as const;

/**
 * 根据主题类别和键获取主题配置
 */
export function getEnhancedThemeConfig(category: ThemeCategory, themeKey: UIThemeKey): ThemeConfig {
  const theme = enhancedThemeMap[category]?.[themeKey];
  return theme || defaultEnhancedTheme;
}

/**
 * 创建自适应主题 - 根据用户角色自动选择
 */
export function createAdaptiveTheme(userRole?: string): ThemeConfig {
  if (userRole === 'teacher') {
    return teacherRecommendedTheme;
  } else if (userRole === 'student') {
    return studentRecommendedTheme;
  }
  return defaultEnhancedTheme;
}