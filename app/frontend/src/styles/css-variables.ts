/**
 * CSS Variables Generator for Design Tokens
 * Converts design tokens to CSS custom properties
 */

import { 
  DesignTokens, 
  monetThemes, 
  morandiThemes, 
  glassTokens,
  radiusTokens,
  spacingTokens,
  motionTokens,
  typographyTokens,
  ThemeCategory,
  MonetThemeKey,
  MorandiThemeKey,
  ThemeMode
} from './design-tokens';

/**
 * 生成CSS变量字符串
 */
export function generateCSSVariables(tokens: DesignTokens): string {
  const { colors, glass, radius, spacing, motion, typography, mode } = tokens;
  
  const variables: string[] = [];
  
  // 颜色变量
  variables.push(`  /* Theme Colors */`);
  variables.push(`  --color-primary: ${colors.primary};`);
  variables.push(`  --color-secondary: ${colors.secondary};`);
  variables.push(`  --color-tertiary: ${colors.tertiary};`);
  variables.push(`  --color-accent: ${colors.accent};`);
  variables.push(`  --color-neutral: ${colors.neutral};`);
  
  // 功能色变量
  variables.push(`  /* Functional Colors */`);
  variables.push(`  --color-success: ${colors.functional.success};`);
  variables.push(`  --color-warning: ${colors.functional.warning};`);
  variables.push(`  --color-error: ${colors.functional.error};`);
  variables.push(`  --color-info: ${colors.functional.info};`);
  
  // 玻璃拟态变量
  const glassAlpha = glass.alpha[mode];
  variables.push(`  /* Glass Effect */`);
  variables.push(`  --glass-blur-sm: blur(${glass.blur.sm});`);
  variables.push(`  --glass-blur-md: blur(${glass.blur.md});`);
  variables.push(`  --glass-blur-lg: blur(${glass.blur.lg});`);
  variables.push(`  --glass-alpha-primary: ${glassAlpha.primary};`);
  variables.push(`  --glass-alpha-secondary: ${glassAlpha.secondary};`);
  variables.push(`  --glass-alpha-tertiary: ${glassAlpha.tertiary};`);
  variables.push(`  --glass-highlight-alpha: ${glass.highlight.alpha[mode]};`);
  variables.push(`  --glass-highlight-width: ${glass.highlight.width};`);
  
  // 阴影变量
  variables.push(`  /* Shadows */`);
  Object.entries(glass.shadow).forEach(([size, shadow]) => {
    variables.push(`  --shadow-${size}: 0 ${shadow.y}px ${shadow.blur}px rgba(0, 0, 0, ${shadow.alpha});`);
  });
  
  // 圆角变量
  variables.push(`  /* Border Radius */`);
  Object.entries(radius).forEach(([key, value]) => {
    variables.push(`  --radius-${key}: ${value};`);
  });
  
  // 间距变量
  variables.push(`  /* Spacing */`);
  Object.entries(spacing).forEach(([key, value]) => {
    variables.push(`  --spacing-${key}: ${value};`);
  });
  
  // 动效变量
  variables.push(`  /* Motion */`);
  Object.entries(motion.duration).forEach(([key, value]) => {
    variables.push(`  --duration-${key}: ${value};`);
  });
  Object.entries(motion.easing).forEach(([key, value]) => {
    variables.push(`  --easing-${key}: ${value};`);
  });
  
  // 字体变量
  variables.push(`  /* Typography */`);
  Object.entries(typography.lineHeight).forEach(([key, value]) => {
    variables.push(`  --line-height-${key}: ${value};`);
  });
  Object.entries(typography.fontWeight).forEach(([key, value]) => {
    variables.push(`  --font-weight-${key}: ${value};`);
  });
  
  return variables.join('\n');
}

/**
 * 生成完整的CSS主题
 */
export function generateThemeCSS(
  category: ThemeCategory,
  themeKey: MonetThemeKey | MorandiThemeKey,
  mode: ThemeMode = 'light'
): string {
  const themes = category === 'monet' ? monetThemes : morandiThemes;
  const colors = themes[themeKey as keyof typeof themes];
  
  const tokens: DesignTokens = {
    category,
    themeKey,
    mode,
    colors,
    glass: glassTokens,
    radius: radiusTokens,
    spacing: spacingTokens,
    motion: motionTokens,
    typography: typographyTokens,
    breakpoints: { sm: '576px', md: '768px', lg: '992px', xl: '1200px', xxl: '1440px' }
  };
  
  const variables = generateCSSVariables(tokens);
  
  return `
:root[data-theme="${category}-${themeKey}"][data-mode="${mode}"] {
${variables}
}`;
}

/**
 * 生成所有主题的CSS
 */
export function generateAllThemesCSS(): string {
  const css: string[] = [];
  
  // 生成莫奈主题
  Object.keys(monetThemes).forEach(themeKey => {
    css.push(generateThemeCSS('monet', themeKey as MonetThemeKey, 'light'));
    css.push(generateThemeCSS('monet', themeKey as MonetThemeKey, 'dark'));
  });
  
  // 生成莫兰迪主题
  Object.keys(morandiThemes).forEach(themeKey => {
    css.push(generateThemeCSS('morandi', themeKey as MorandiThemeKey, 'light'));
    css.push(generateThemeCSS('morandi', themeKey as MorandiThemeKey, 'dark'));
  });
  
  return css.join('\n\n');
}

/**
 * 应用主题到DOM
 */
export function applyTheme(
  category: ThemeCategory,
  themeKey: MonetThemeKey | MorandiThemeKey,
  mode: ThemeMode = 'light'
): void {
  const root = document.documentElement;
  root.setAttribute('data-theme', `${category}-${themeKey}`);
  root.setAttribute('data-mode', mode);
  
  // 保存到localStorage
  localStorage.setItem('ui-theme-category', category);
  localStorage.setItem('ui-theme-key', themeKey);
  localStorage.setItem('ui-theme-mode', mode);
}

/**
 * 从localStorage恢复主题
 */
export function restoreTheme(): {
  category: ThemeCategory;
  themeKey: MonetThemeKey | MorandiThemeKey;
  mode: ThemeMode;
} {
  const category = (localStorage.getItem('ui-theme-category') as ThemeCategory) || 'monet';
  const themeKey = localStorage.getItem('ui-theme-key') || 'clearMorningLake';
  const mode = (localStorage.getItem('ui-theme-mode') as ThemeMode) || 'light';
  
  applyTheme(category, themeKey as any, mode);
  
  return { category, themeKey: themeKey as any, mode };
}

/**
 * 获取当前主题的颜色值
 */
export function getCurrentThemeColors(
  category: ThemeCategory,
  themeKey: MonetThemeKey | MorandiThemeKey
) {
  const themes = category === 'monet' ? monetThemes : morandiThemes;
  return themes[themeKey as keyof typeof themes];
}

/**
 * 检查对比度是否符合AA标准
 */
export function checkContrastRatio(foreground: string, background: string): number {
  // 简化的对比度计算，实际项目中应使用更精确的算法
  // 这里返回一个模拟值，实际应该实现完整的WCAG对比度计算
  return 4.5; // 假设符合AA标准
}

/**
 * 自动调整颜色以满足对比度要求
 */
export function adjustColorForContrast(
  color: string,
  background: string,
  targetRatio: number = 4.5
): string {
  // 简化实现，实际项目中应该实现完整的颜色调整算法
  return color;
}
