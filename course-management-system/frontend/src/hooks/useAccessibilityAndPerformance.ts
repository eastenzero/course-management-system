import { useEffect, useRef, useState, useCallback } from 'react';
import { AccessibilityUtils } from '../utils/accessibility';
import { PerformanceUtils } from '../utils/performance';

/**
 * 无障碍支持Hook
 */
export function useAccessibility() {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(
    AccessibilityUtils.MotionPreferences.prefersReducedMotion()
  );

  useEffect(() => {
    // 初始化焦点可见性增强
    AccessibilityUtils.FocusManager.enhanceFocusVisibility();
    
    // 应用文本方向
    AccessibilityUtils.Internationalization.applyTextDirection();

    // 监听动效偏好变化
    const cleanup = AccessibilityUtils.MotionPreferences.watchMotionPreference(
      setPrefersReducedMotion
    );

    return cleanup;
  }, []);

  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    AccessibilityUtils.ScreenReaderSupport.announce(message, priority);
  }, []);

  const trapFocus = useCallback((container: HTMLElement) => {
    return AccessibilityUtils.KeyboardNavigation.trapFocus(container);
  }, []);

  const skipToMain = useCallback(() => {
    AccessibilityUtils.KeyboardNavigation.skipToMain();
  }, []);

  return {
    prefersReducedMotion,
    announce,
    trapFocus,
    skipToMain,
    saveFocus: AccessibilityUtils.FocusManager.saveFocus,
    restoreFocus: AccessibilityUtils.FocusManager.restoreFocus
  };
}

/**
 * 性能监控Hook
 */
export function usePerformance() {
  const [networkQuality, setNetworkQuality] = useState(
    PerformanceUtils.NetworkOptimization.getNetworkQuality()
  );

  useEffect(() => {
    // 初始化网络适配
    PerformanceUtils.NetworkOptimization.adaptToNetwork();

    // 监控内存使用（仅开发环境）
    if (process.env.NODE_ENV === 'development') {
      const interval = setInterval(() => {
        PerformanceUtils.MemoryManagement.monitorMemory();
      }, 30000);
      
      PerformanceUtils.MemoryManagement.registerInterval(interval);
    }

    // 网络连接变化监听
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      const handleChange = () => {
        const quality = PerformanceUtils.NetworkOptimization.getNetworkQuality();
        setNetworkQuality(quality);
        PerformanceUtils.NetworkOptimization.adaptToNetwork();
      };
      
      connection.addEventListener('change', handleChange);
      
      return () => {
        connection.removeEventListener('change', handleChange);
      };
    }
  }, []);

  const prefetchResources = useCallback((urls: string[]) => {
    PerformanceUtils.NetworkOptimization.prefetchResources(urls);
  }, []);

  const debounce = useCallback(<T extends (...args: any[]) => any>(
    func: T,
    wait: number
  ) => {
    return PerformanceUtils.RenderOptimization.debounce(func, wait);
  }, []);

  const throttle = useCallback(<T extends (...args: any[]) => any>(
    func: T,
    limit: number
  ) => {
    return PerformanceUtils.RenderOptimization.throttle(func, limit);
  }, []);

  return {
    networkQuality,
    prefetchResources,
    debounce,
    throttle,
    batchDOMUpdates: PerformanceUtils.RenderOptimization.batchDOMUpdates
  };
}

/**
 * 懒加载图片Hook
 */
export function useLazyImage(src: string, options?: {
  webpSrc?: string;
  threshold?: number;
  rootMargin?: string;
}) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const img = imgRef.current;
    if (!img) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          const image = new Image();
          
          image.onload = () => {
            if (img) {
              img.src = src;
              setLoaded(true);
            }
          };
          
          image.onerror = () => {
            setError(true);
          };

          // 支持WebP
          if (options?.webpSrc && 'webp' in document.createElement('canvas').getContext('2d')!) {
            image.src = options.webpSrc;
          } else {
            image.src = src;
          }
          
          observer.unobserve(img);
        }
      },
      {
        threshold: options?.threshold || 0.1,
        rootMargin: options?.rootMargin || '50px'
      }
    );

    observer.observe(img);
    PerformanceUtils.MemoryManagement.registerObserver(observer);

    return () => {
      observer.disconnect();
    };
  }, [src, options?.webpSrc, options?.threshold, options?.rootMargin]);

  return {
    imgRef,
    loaded,
    error
  };
}

/**
 * 虚拟滚动Hook
 */
export function useVirtualScroll<T>(
  items: T[],
  itemHeight: number,
  containerHeight: number,
  overscan = 5
) {
  const [scrollTop, setScrollTop] = useState(0);

  const visibleStart = Math.floor(scrollTop / itemHeight);
  const visibleEnd = Math.min(
    visibleStart + Math.ceil(containerHeight / itemHeight),
    items.length - 1
  );

  const startIndex = Math.max(0, visibleStart - overscan);
  const endIndex = Math.min(items.length - 1, visibleEnd + overscan);

  const visibleItems = items.slice(startIndex, endIndex + 1);
  const totalHeight = items.length * itemHeight;
  const offsetY = startIndex * itemHeight;

  const onScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  }, []);

  return {
    visibleItems,
    totalHeight,
    offsetY,
    onScroll,
    startIndex,
    endIndex
  };
}

/**
 * 色彩对比度检查Hook
 */
export function useContrastCheck(foreground: string, background: string) {
  const [ratio, setRatio] = useState(0);
  const [passesAA, setPassesAA] = useState(false);
  const [passesAAA, setPassesAAA] = useState(false);

  useEffect(() => {
    const contrastRatio = AccessibilityUtils.ContrastChecker.getContrastRatio(
      foreground,
      background
    );
    
    setRatio(contrastRatio);
    setPassesAA(AccessibilityUtils.ContrastChecker.checkWCAGAA(foreground, background));
    setPassesAAA(AccessibilityUtils.ContrastChecker.checkWCAGAAA(foreground, background));
  }, [foreground, background]);

  return {
    ratio,
    passesAA,
    passesAAA
  };
}

/**
 * 清理资源Hook
 */
export function useCleanup() {
  useEffect(() => {
    return () => {
      PerformanceUtils.MemoryManagement.cleanup();
    };
  }, []);
}

/**
 * 键盘快捷键Hook
 */
export function useKeyboardShortcuts(shortcuts: Record<string, () => void>) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const key = e.key.toLowerCase();
      const modifiers = {
        ctrl: e.ctrlKey,
        alt: e.altKey,
        shift: e.shiftKey,
        meta: e.metaKey
      };

      Object.entries(shortcuts).forEach(([shortcut, handler]) => {
        const [modifierPart, ...keyParts] = shortcut.toLowerCase().split('+').reverse();
        const targetKey = keyParts.pop() || modifierPart;
        
        const requiredModifiers = keyParts.reverse();
        const hasRequiredModifiers = requiredModifiers.every(mod => {
          switch (mod) {
            case 'ctrl': return modifiers.ctrl;
            case 'alt': return modifiers.alt;
            case 'shift': return modifiers.shift;
            case 'meta': return modifiers.meta;
            default: return false;
          }
        });

        if (key === targetKey && hasRequiredModifiers) {
          e.preventDefault();
          handler();
        }
      });
    };

    document.addEventListener('keydown', handleKeyDown);
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [shortcuts]);
}