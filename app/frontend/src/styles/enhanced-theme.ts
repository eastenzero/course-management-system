import { ThemeConfig } from 'antd';
import { monetThemes, morandiThemes } from './design-tokens';
import type { UIThemeCategory, UIThemeKey } from '../hooks/useThemeV2';

/**
 * 创建基于设计规范的Ant Design主题配置
 */
export function createEnhancedTheme(
  category: UIThemeCategory = 'monet',
  themeKey: UIThemeKey = 'clearMorningLake'
): ThemeConfig {
  const themes = category === 'monet' ? monetThemes : morandiThemes;
  const colors = themes[themeKey as keyof typeof themes];

  return {
    token: {
      // 主题色彩
      colorPrimary: colors.primary,
      colorSuccess: colors.functional.success,
      colorWarning: colors.functional.warning,
      colorError: colors.functional.error,
      colorInfo: colors.functional.info,

      // 文字颜色
      colorText: '#262626',
      colorTextSecondary: '#595959',
      colorTextTertiary: '#8c8c8c',
      colorTextQuaternary: '#bfbfbf',

      // 背景颜色
      colorBgContainer: '#ffffff',
      colorBgElevated: '#ffffff',
      colorBgLayout: '#fafafa',
      colorBgSpotlight: '#f5f5f5',

      // 边框颜色
      colorBorder: '#e8e8e8',
      colorBorderSecondary: '#f0f0f0',

      // 字体配置
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif',
      fontSize: 14,
      fontSizeLG: 16,
      fontSizeSM: 12,
      fontSizeXL: 20,
      fontSizeHeading1: 32,
      fontSizeHeading2: 24,
      fontSizeHeading3: 20,
      fontSizeHeading4: 16,
      fontSizeHeading5: 14,

      // 行高配置 - 中文优化
      lineHeight: 1.6,
      lineHeightLG: 1.5,
      lineHeightSM: 1.8,

      // 圆角配置 - 基于设计规范
      borderRadius: 8,
      borderRadiusLG: 16,
      borderRadiusSM: 6,
      borderRadiusXS: 4,

      // 阴影配置 - 柔和无硬边
      boxShadow: '0 8px 24px rgba(0, 0, 0, 0.08)',
      boxShadowSecondary: '0 16px 32px rgba(0, 0, 0, 0.10)',
      boxShadowTertiary: '0 24px 48px rgba(0, 0, 0, 0.12)',

      // 间距配置 - 8pt基准
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

      // 动画配置 - 基于设计规范
      motionDurationFast: '0.15s',
      motionDurationMid: '0.2s',
      motionDurationSlow: '0.25s',
      motionEaseInOut: 'cubic-bezier(0.22, 1, 0.36, 1)',
      motionEaseOut: 'cubic-bezier(0.0, 0.0, 0.2, 1)',
      motionEaseIn: 'cubic-bezier(0.4, 0.0, 1, 1)',
    },
    components: {
      Layout: {
        headerBg: 'rgba(255, 255, 255, 0.8)',
        headerHeight: 64,
        headerPadding: '0 24px',
        siderBg: `linear-gradient(180deg, ${colors.primary} 0%, ${colors.secondary} 100%)`,
        triggerBg: 'rgba(255, 255, 255, 0.15)',
        triggerColor: '#ffffff',
      },
      Menu: {
        darkItemBg: 'transparent',
        darkItemSelectedBg: 'rgba(255, 255, 255, 0.2)',
        darkItemHoverBg: 'rgba(255, 255, 255, 0.1)',
        itemHeight: 48,
        itemMarginInline: 8,
        borderRadius: 8,
      },
      Card: {
        headerBg: 'transparent',
        headerHeight: 56,
        paddingLG: 24,
        boxShadow: '0 8px 24px rgba(0, 0, 0, 0.08)',
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
        headerBg: 'rgba(255, 255, 255, 0.8)',
        headerSplitColor: 'rgba(0, 0, 0, 0.06)',
        rowHoverBg: 'rgba(0, 0, 0, 0.02)',
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

// 预设主题配置
export const monetClearMorningLakeTheme = createEnhancedTheme('monet', 'clearMorningLake');
export const monetMorningGardenTheme = createEnhancedTheme('monet', 'morningGarden');
export const monetSeaBreezeLavenderTheme = createEnhancedTheme('monet', 'seaBreezeLavender');

export const morandiRockAndMossTheme = createEnhancedTheme('morandi', 'rockAndMoss');
export const morandiOatAndGraphiteTheme = createEnhancedTheme('morandi', 'oatAndGraphite');
export const morandiCeramicAndAshTheme = createEnhancedTheme('morandi', 'ceramicAndAsh');

// 默认主题
export const defaultEnhancedTheme = monetClearMorningLakeTheme;

// 根据用户角色推荐的主题
export const teacherRecommendedTheme = morandiRockAndMossTheme;
export const studentRecommendedTheme = monetClearMorningLakeTheme;

// 主题映射
export const themeMap = {
  monet: {
    clearMorningLake: monetClearMorningLakeTheme,
    morningGarden: monetMorningGardenTheme,
    seaBreezeLavender: monetSeaBreezeLavenderTheme,
  },
  morandi: {
    rockAndMoss: morandiRockAndMossTheme,
    oatAndGraphite: morandiOatAndGraphiteTheme,
    ceramicAndAsh: morandiCeramicAndAshTheme,
  },
};

/**
 * 获取主题配置
 */
export function getThemeConfig(category: UIThemeCategory, themeKey: UIThemeKey): ThemeConfig {
  return themeMap[category][themeKey as keyof typeof themeMap[typeof category]] || defaultEnhancedTheme;
}
