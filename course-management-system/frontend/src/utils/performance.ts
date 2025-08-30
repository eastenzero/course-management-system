/**
 * 性能优化工具集
 * Performance optimization utilities
 */

// 图片懒加载和优化
export class ImageOptimization {
  /**
   * 创建支持WebP的图片元素
   */
  static createOptimizedImage(src: string, alt: string, options?: {
    webpSrc?: string;
    loading?: 'lazy' | 'eager';
    sizes?: string;
  }): HTMLPictureElement {
    const picture = document.createElement('picture');
    
    // WebP支持
    if (options?.webpSrc) {
      const webpSource = document.createElement('source');
      webpSource.srcset = options.webpSrc;
      webpSource.type = 'image/webp';
      picture.appendChild(webpSource);
    }
    
    // 回退图片
    const img = document.createElement('img');
    img.src = src;
    img.alt = alt;
    img.loading = options?.loading || 'lazy';
    
    if (options?.sizes) {
      img.sizes = options.sizes;
    }
    
    picture.appendChild(img);
    return picture;
  }

  /**
   * 批量懒加载图片
   */
  static lazyLoadImages(selector = 'img[data-src]'): IntersectionObserver {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target as HTMLImageElement;
          const src = img.getAttribute('data-src');
          
          if (src) {
            img.src = src;
            img.removeAttribute('data-src');
            img.classList.add('loaded');
            observer.unobserve(img);
          }
        }
      });
    }, {
      rootMargin: '50px 0px',
      threshold: 0.1
    });

    const images = document.querySelectorAll(selector);
    images.forEach(img => imageObserver.observe(img));
    
    return imageObserver;
  }
}

// 代码分割和组件懒加载
export class ComponentLazyLoading {
  /**
   * 创建带加载状态的懒加载组件
   */
  static createLazyComponent<T = any>(
    importFn: () => Promise<{ default: React.ComponentType<T> }>,
    fallback?: React.ComponentType
  ) {
    const LazyComponent = React.lazy(importFn);
    
    return function LazyWrapper(props: T) {
      return React.createElement(
        React.Suspense,
        { 
          fallback: fallback 
            ? React.createElement(fallback) 
            : React.createElement('div', null, '加载中...')
        },
        React.createElement(LazyComponent, props)
      );
    };
  }

  /**
   * 预加载组件
   */
  static preloadComponent(importFn: () => Promise<any>): void {
    // 在空闲时间预加载
    if ('requestIdleCallback' in window) {
      requestIdleCallback(() => {
        importFn();
      });
    } else {
      // 回退到setTimeout
      setTimeout(() => {
        importFn();
      }, 100);
    }
  }
}

// 虚拟滚动优化
export class VirtualScrolling {
  /**
   * 创建虚拟滚动实例
   */
  static create(options: {
    container: HTMLElement;
    itemHeight: number;
    items: any[];
    renderItem: (item: any, index: number) => HTMLElement;
    overscan?: number;
  }) {
    const { container, itemHeight, items, renderItem, overscan = 5 } = options;
    
    let scrollTop = 0;
    let containerHeight = container.clientHeight;
    
    const totalHeight = items.length * itemHeight;
    const visibleStart = Math.floor(scrollTop / itemHeight);
    const visibleEnd = Math.min(
      visibleStart + Math.ceil(containerHeight / itemHeight),
      items.length - 1
    );
    
    const startIndex = Math.max(0, visibleStart - overscan);
    const endIndex = Math.min(items.length - 1, visibleEnd + overscan);
    
    // 渲染可见项目
    const fragment = document.createDocumentFragment();
    
    for (let i = startIndex; i <= endIndex; i++) {
      const item = renderItem(items[i], i);
      item.style.position = 'absolute';
      item.style.top = `${i * itemHeight}px`;
      item.style.width = '100%';
      item.style.height = `${itemHeight}px`;
      fragment.appendChild(item);
    }
    
    container.style.height = `${totalHeight}px`;
    container.style.position = 'relative';
    container.innerHTML = '';
    container.appendChild(fragment);
    
    // 滚动监听
    const handleScroll = () => {
      scrollTop = container.scrollTop;
      // 重新计算和渲染可见项目
    };
    
    container.addEventListener('scroll', handleScroll, { passive: true });
    
    return {
      destroy: () => {
        container.removeEventListener('scroll', handleScroll);
      },
      updateItems: (newItems: any[]) => {
        // 更新项目列表
      }
    };
  }
}

// 内存管理
export class MemoryManagement {
  private static observers: Set<IntersectionObserver | MutationObserver> = new Set();
  private static timeouts: Set<number> = new Set();
  private static intervals: Set<number> = new Set();

  /**
   * 注册观察器以便清理
   */
  static registerObserver(observer: IntersectionObserver | MutationObserver): void {
    this.observers.add(observer);
  }

  /**
   * 注册定时器以便清理
   */
  static registerTimeout(id: number): void {
    this.timeouts.add(id);
  }

  /**
   * 注册间隔器以便清理
   */
  static registerInterval(id: number): void {
    this.intervals.add(id);
  }

  /**
   * 清理所有注册的资源
   */
  static cleanup(): void {
    // 清理观察器
    this.observers.forEach(observer => {
      observer.disconnect();
    });
    this.observers.clear();

    // 清理定时器
    this.timeouts.forEach(id => {
      clearTimeout(id);
    });
    this.timeouts.clear();

    // 清理间隔器
    this.intervals.forEach(id => {
      clearInterval(id);
    });
    this.intervals.clear();
  }

  /**
   * 监控内存使用情况
   */
  static monitorMemory(): void {
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      console.log('Memory usage:', {
        used: `${Math.round(memory.usedJSHeapSize / 1048576)} MB`,
        total: `${Math.round(memory.totalJSHeapSize / 1048576)} MB`,
        limit: `${Math.round(memory.jsHeapSizeLimit / 1048576)} MB`
      });
    }
  }
}

// 网络优化
export class NetworkOptimization {
  /**
   * 检测网络连接质量
   */
  static getNetworkQuality(): 'slow' | 'fast' | 'unknown' {
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      const effectiveType = connection.effectiveType;
      
      if (effectiveType === 'slow-2g' || effectiveType === '2g') {
        return 'slow';
      } else if (effectiveType === '3g' || effectiveType === '4g') {
        return 'fast';
      }
    }
    return 'unknown';
  }

  /**
   * 根据网络质量调整资源加载
   */
  static adaptToNetwork(): void {
    const quality = this.getNetworkQuality();
    
    if (quality === 'slow') {
      // 慢网络：减少预加载，降低图片质量
      document.documentElement.setAttribute('data-network-quality', 'slow');
      
      // 禁用非关键动画
      const style = document.createElement('style');
      style.textContent = `
        .transition-standard,
        .transition-fast,
        .transition-slow {
          transition: none !important;
        }
        
        .glass-surface {
          backdrop-filter: none !important;
          -webkit-backdrop-filter: none !important;
        }
      `;
      document.head.appendChild(style);
    } else {
      document.documentElement.setAttribute('data-network-quality', 'fast');
    }
  }

  /**
   * 预取关键资源
   */
  static prefetchResources(urls: string[]): void {
    const quality = this.getNetworkQuality();
    
    if (quality !== 'slow') {
      urls.forEach(url => {
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = url;
        document.head.appendChild(link);
      });
    }
  }
}

// 渲染优化
export class RenderOptimization {
  /**
   * 防抖函数
   */
  static debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number
  ): (...args: Parameters<T>) => void {
    let timeout: number;
    
    return (...args: Parameters<T>) => {
      clearTimeout(timeout);
      timeout = window.setTimeout(() => func(...args), wait);
      MemoryManagement.registerTimeout(timeout);
    };
  }

  /**
   * 节流函数
   */
  static throttle<T extends (...args: any[]) => any>(
    func: T,
    limit: number
  ): (...args: Parameters<T>) => void {
    let inThrottle: boolean;
    
    return (...args: Parameters<T>) => {
      if (!inThrottle) {
        func(...args);
        inThrottle = true;
        const timeout = window.setTimeout(() => inThrottle = false, limit);
        MemoryManagement.registerTimeout(timeout);
      }
    };
  }

  /**
   * 使用requestAnimationFrame优化DOM操作
   */
  static rafBatch(callback: () => void): void {
    requestAnimationFrame(callback);
  }

  /**
   * 批量DOM更新
   */
  static batchDOMUpdates(updates: (() => void)[]): void {
    this.rafBatch(() => {
      updates.forEach(update => update());
    });
  }
}

// 导出性能优化工具
export const PerformanceUtils = {
  ImageOptimization,
  ComponentLazyLoading,
  VirtualScrolling,
  MemoryManagement,
  NetworkOptimization,
  RenderOptimization
};

export default PerformanceUtils;