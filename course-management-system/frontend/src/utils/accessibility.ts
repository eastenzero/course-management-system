/**
 * 无障碍支持工具集
 * Accessibility utilities for enhanced user experience
 */

// 键盘导航支持
export class KeyboardNavigation {
  private static focusableSelectors = [
    'button',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    'a[href]',
    '[tabindex]:not([tabindex="-1"])'
  ].join(',');

  /**
   * 获取可聚焦元素
   */
  static getFocusableElements(container: HTMLElement): HTMLElement[] {
    return Array.from(container.querySelectorAll(this.focusableSelectors));
  }

  /**
   * 实现键盘陷阱（模态框内键盘导航）
   */
  static trapFocus(container: HTMLElement): () => void {
    const focusableElements = this.getFocusableElements(container);
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleKeydown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          // Shift + Tab: 向前导航
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement?.focus();
          }
        } else {
          // Tab: 向后导航
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement?.focus();
          }
        }
      }
      
      // ESC键关闭模态框
      if (e.key === 'Escape') {
        const closeButton = container.querySelector('[aria-label="关闭"], [aria-label="Close"]') as HTMLElement;
        closeButton?.click();
      }
    };

    container.addEventListener('keydown', handleKeydown);
    
    // 自动聚焦到第一个元素
    firstElement?.focus();

    // 返回清理函数
    return () => {
      container.removeEventListener('keydown', handleKeydown);
    };
  }

  /**
   * 跳转到主内容区域
   */
  static skipToMain(): void {
    const mainContent = document.querySelector('main, [role="main"], #main-content') as HTMLElement;
    if (mainContent) {
      mainContent.focus();
      mainContent.scrollIntoView({ behavior: 'smooth' });
    }
  }
}

// 屏幕阅读器支持
export class ScreenReaderSupport {
  /**
   * 动态宣布消息给屏幕阅读器
   */
  static announce(message: string, priority: 'polite' | 'assertive' = 'polite'): void {
    const announcer = document.createElement('div');
    announcer.setAttribute('aria-live', priority);
    announcer.setAttribute('aria-atomic', 'true');
    announcer.style.position = 'absolute';
    announcer.style.left = '-10000px';
    announcer.style.width = '1px';
    announcer.style.height = '1px';
    announcer.style.overflow = 'hidden';
    
    document.body.appendChild(announcer);
    announcer.textContent = message;
    
    // 清理
    setTimeout(() => {
      document.body.removeChild(announcer);
    }, 1000);
  }

  /**
   * 创建进度更新播报器
   */
  static createProgressAnnouncer(): (progress: number, total?: number) => void {
    let lastAnnounced = 0;
    
    return (progress: number, total: number = 100) => {
      const percentage = Math.round((progress / total) * 100);
      
      // 每增加25%播报一次
      if (percentage >= lastAnnounced + 25) {
        this.announce(`进度 ${percentage}%`, 'polite');
        lastAnnounced = percentage;
      }
      
      // 完成时特别播报
      if (percentage === 100) {
        this.announce('任务完成', 'assertive');
      }
    };
  }
}

// 色彩对比度检查器
export class ContrastChecker {
  /**
   * 计算两个颜色之间的对比度
   */
  static getContrastRatio(color1: string, color2: string): number {
    const rgb1 = this.hexToRgb(color1);
    const rgb2 = this.hexToRgb(color2);
    
    if (!rgb1 || !rgb2) return 0;
    
    const l1 = this.getLuminance(rgb1);
    const l2 = this.getLuminance(rgb2);
    
    const lighter = Math.max(l1, l2);
    const darker = Math.min(l1, l2);
    
    return (lighter + 0.05) / (darker + 0.05);
  }

  /**
   * 检查对比度是否符合WCAG AA标准
   */
  static checkWCAGAA(foreground: string, background: string, isLargeText = false): boolean {
    const ratio = this.getContrastRatio(foreground, background);
    return isLargeText ? ratio >= 3 : ratio >= 4.5;
  }

  /**
   * 检查对比度是否符合WCAG AAA标准
   */
  static checkWCAGAAA(foreground: string, background: string, isLargeText = false): boolean {
    const ratio = this.getContrastRatio(foreground, background);
    return isLargeText ? ratio >= 4.5 : ratio >= 7;
  }

  private static hexToRgb(hex: string): { r: number; g: number; b: number } | null {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  }

  private static getLuminance(rgb: { r: number; g: number; b: number }): number {
    const [r, g, b] = [rgb.r, rgb.g, rgb.b].map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }
}

// 减少动效偏好检测
export class MotionPreferences {
  /**
   * 检查用户是否偏好减少动效
   */
  static prefersReducedMotion(): boolean {
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  /**
   * 根据用户偏好应用动效类
   */
  static applyMotionClass(element: HTMLElement, animationClass: string): void {
    if (!this.prefersReducedMotion()) {
      element.classList.add(animationClass);
    }
  }

  /**
   * 监听动效偏好变化
   */
  static watchMotionPreference(callback: (prefersReduced: boolean) => void): () => void {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    const handler = (e: MediaQueryListEvent) => {
      callback(e.matches);
    };
    
    mediaQuery.addEventListener('change', handler);
    
    // 初始调用
    callback(mediaQuery.matches);
    
    // 返回清理函数
    return () => {
      mediaQuery.removeEventListener('change', handler);
    };
  }
}

// 焦点管理器
export class FocusManager {
  private static focusHistory: HTMLElement[] = [];

  /**
   * 保存当前焦点
   */
  static saveFocus(): void {
    const activeElement = document.activeElement as HTMLElement;
    if (activeElement) {
      this.focusHistory.push(activeElement);
    }
  }

  /**
   * 恢复之前的焦点
   */
  static restoreFocus(): void {
    const previousElement = this.focusHistory.pop();
    if (previousElement && document.contains(previousElement)) {
      previousElement.focus();
    }
  }

  /**
   * 创建可见的焦点指示器
   */
  static enhanceFocusVisibility(): void {
    const style = document.createElement('style');
    style.textContent = `
      *:focus {
        outline: 2px solid var(--color-primary, #1890ff) !important;
        outline-offset: 2px !important;
        border-radius: 4px !important;
      }
      
      *:focus:not(:focus-visible) {
        outline: none !important;
      }
      
      .enhanced-glass-button:focus,
      .enhanced-glass-input:focus,
      .enhanced-glass-card:focus {
        box-shadow: 0 0 0 2px var(--color-primary, #1890ff) !important;
      }
    `;
    document.head.appendChild(style);
  }
}

// 语言和区域设置支持
export class Internationalization {
  /**
   * 获取用户首选语言
   */
  static getPreferredLanguage(): string {
    return navigator.language || 'zh-CN';
  }

  /**
   * 检查是否为RTL语言
   */
  static isRTL(language?: string): boolean {
    const rtlLanguages = ['ar', 'he', 'fa', 'ur'];
    const lang = language || this.getPreferredLanguage();
    return rtlLanguages.some(rtl => lang.startsWith(rtl));
  }

  /**
   * 应用文本方向
   */
  static applyTextDirection(): void {
    const isRTL = this.isRTL();
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
    document.documentElement.setAttribute('data-text-direction', isRTL ? 'rtl' : 'ltr');
  }
}

// 导出统一的无障碍工具
export const AccessibilityUtils = {
  KeyboardNavigation,
  ScreenReaderSupport,
  ContrastChecker,
  MotionPreferences,
  FocusManager,
  Internationalization
};

export default AccessibilityUtils;