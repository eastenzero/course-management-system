import React, { memo, useMemo, useCallback, useRef, useEffect } from 'react';
import { optimizedDebounce as debounce, optimizedThrottle as throttle } from '../../utils/performanceOptimizations';

// 性能优化的高阶组件
export function withPerformanceOptimization<T extends Record<string, any>>(
  Component: React.ComponentType<T>,
  options: {
    memoize?: boolean;
    debounceProps?: string[];
    throttleProps?: string[];
    debounceDelay?: number;
    throttleDelay?: number;
  } = {}
) {
  const {
    memoize = true,
    debounceProps = [],
    throttleProps = [],
    debounceDelay = 300,
    throttleDelay = 100,
  } = options;

  const OptimizedComponent: React.FC<T> = (props) => {
    const debouncedPropsRef = useRef<Record<string, any>>({});
    const throttledPropsRef = useRef<Record<string, any>>({});

    // 创建防抖函数
    const debouncedFunctions = useMemo(() => {
      const functions: Record<string, any> = {};
      debounceProps.forEach(propName => {
        if (typeof props[propName] === 'function') {
          functions[propName] = debounce(props[propName], debounceDelay);
        }
      });
      return functions;
    }, [props, debounceDelay]);

    // 创建节流函数
    const throttledFunctions = useMemo(() => {
      const functions: Record<string, any> = {};
      throttleProps.forEach(propName => {
        if (typeof props[propName] === 'function') {
          functions[propName] = throttle(props[propName], throttleDelay);
        }
      });
      return functions;
    }, [props, throttleDelay]);

    // 合并优化后的props
    const optimizedProps = useMemo(() => {
      return {
        ...props,
        ...debouncedFunctions,
        ...throttledFunctions,
      };
    }, [props, debouncedFunctions, throttledFunctions]);

    return <Component {...optimizedProps} />;
  };

  OptimizedComponent.displayName = `withPerformanceOptimization(${Component.displayName || Component.name})`;

  return memoize ? memo(OptimizedComponent) : OptimizedComponent;
}

// 虚拟滚动优化组件
interface VirtualScrollProps {
  items: any[];
  itemHeight: number;
  containerHeight: number;
  renderItem: (item: any, index: number) => React.ReactNode;
  overscan?: number;
  className?: string;
  style?: React.CSSProperties;
}

export const VirtualScroll: React.FC<VirtualScrollProps> = memo(({
  items,
  itemHeight,
  containerHeight,
  renderItem,
  overscan = 5,
  className,
  style,
}) => {
  const [scrollTop, setScrollTop] = React.useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleScroll = useCallback(
    throttle((e: React.UIEvent<HTMLDivElement>) => {
      setScrollTop(e.currentTarget.scrollTop);
    }, 16), // 60fps
    []
  );

  const visibleRange = useMemo(() => {
    const start = Math.floor(scrollTop / itemHeight);
    const end = Math.min(
      start + Math.ceil(containerHeight / itemHeight),
      items.length - 1
    );

    return {
      start: Math.max(0, start - overscan),
      end: Math.min(items.length - 1, end + overscan),
    };
  }, [scrollTop, itemHeight, containerHeight, items.length, overscan]);

  const visibleItems = useMemo(() => {
    return items.slice(visibleRange.start, visibleRange.end + 1);
  }, [items, visibleRange]);

  const totalHeight = items.length * itemHeight;
  const offsetY = visibleRange.start * itemHeight;

  return (
    <div
      ref={containerRef}
      className={className}
      style={{
        height: containerHeight,
        overflow: 'auto',
        ...style,
      }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div
          style={{
            transform: `translateY(${offsetY}px)`,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
          }}
        >
          {visibleItems.map((item, index) =>
            renderItem(item, visibleRange.start + index)
          )}
        </div>
      </div>
    </div>
  );
});

VirtualScroll.displayName = 'VirtualScroll';

// 图片预加载组件
interface ImagePreloaderProps {
  src: string;
  fallback?: string;
  placeholder?: React.ReactNode;
  onLoad?: () => void;
  onError?: () => void;
  className?: string;
  style?: React.CSSProperties;
  alt?: string;
}

export const ImagePreloader: React.FC<ImagePreloaderProps> = memo(({
  src,
  fallback,
  placeholder,
  onLoad,
  onError,
  className,
  style,
  alt = '',
}) => {
  const [imageState, setImageState] = React.useState<'loading' | 'loaded' | 'error'>('loading');
  const [imageSrc, setImageSrc] = React.useState<string>('');

  useEffect(() => {
    const img = new Image();
    
    img.onload = () => {
      setImageState('loaded');
      setImageSrc(src);
      onLoad?.();
    };

    img.onerror = () => {
      setImageState('error');
      if (fallback) {
        setImageSrc(fallback);
      }
      onError?.();
    };

    img.src = src;

    return () => {
      img.onload = null;
      img.onerror = null;
    };
  }, [src, fallback, onLoad, onError]);

  if (imageState === 'loading') {
    return placeholder ? <>{placeholder}</> : null;
  }

  if (imageState === 'error' && !fallback) {
    return null;
  }

  return (
    <img
      src={imageSrc}
      alt={alt}
      className={className}
      style={style}
    />
  );
});

ImagePreloader.displayName = 'ImagePreloader';

// 延迟渲染组件
interface DeferredRenderProps {
  children: React.ReactNode;
  delay?: number;
  fallback?: React.ReactNode;
}

export const DeferredRender: React.FC<DeferredRenderProps> = memo(({
  children,
  delay = 0,
  fallback = null,
}) => {
  const [shouldRender, setShouldRender] = React.useState(delay === 0);

  useEffect(() => {
    if (delay > 0) {
      const timer = setTimeout(() => {
        setShouldRender(true);
      }, delay);

      return () => clearTimeout(timer);
    }
  }, [delay]);

  if (!shouldRender) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
});

DeferredRender.displayName = 'DeferredRender';

// 批量更新组件
interface BatchUpdateProps<T> {
  items: T[];
  batchSize?: number;
  delay?: number;
  renderItem: (item: T, index: number) => React.ReactNode;
  renderBatch?: (items: T[], startIndex: number) => React.ReactNode;
  onBatchComplete?: (batchIndex: number, totalBatches: number) => void;
}

export function BatchUpdate<T>({
  items,
  batchSize = 10,
  delay = 16,
  renderItem,
  renderBatch,
  onBatchComplete,
}: BatchUpdateProps<T>) {
  const [renderedCount, setRenderedCount] = React.useState(batchSize);

  useEffect(() => {
    if (renderedCount >= items.length) return;

    const timer = setTimeout(() => {
      const newCount = Math.min(renderedCount + batchSize, items.length);
      setRenderedCount(newCount);
      
      const batchIndex = Math.ceil(newCount / batchSize);
      const totalBatches = Math.ceil(items.length / batchSize);
      onBatchComplete?.(batchIndex, totalBatches);
    }, delay);

    return () => clearTimeout(timer);
  }, [renderedCount, items.length, batchSize, delay, onBatchComplete]);

  const visibleItems = items.slice(0, renderedCount);

  if (renderBatch) {
    const batches: T[][] = [];
    for (let i = 0; i < visibleItems.length; i += batchSize) {
      batches.push(visibleItems.slice(i, i + batchSize));
    }
    
    return (
      <>
        {batches.map((batch, batchIndex) =>
          renderBatch(batch, batchIndex * batchSize)
        )}
      </>
    );
  }

  return (
    <>
      {visibleItems.map((item, index) => renderItem(item, index))}
    </>
  );
}

// 性能监控Hook
export function usePerformanceMonitor(componentName: string) {
  const renderCountRef = useRef(0);
  const mountTimeRef = useRef(Date.now());
  const lastRenderTimeRef = useRef(Date.now());

  useEffect(() => {
    renderCountRef.current += 1;
    const now = Date.now();
    const renderTime = now - lastRenderTimeRef.current;
    lastRenderTimeRef.current = now;

    if (process.env.NODE_ENV === 'development') {
      console.log(`[Performance] ${componentName}:`, {
        renderCount: renderCountRef.current,
        renderTime,
        totalTime: now - mountTimeRef.current,
      });
    }
  });

  return {
    renderCount: renderCountRef.current,
    totalTime: Date.now() - mountTimeRef.current,
  };
}

// 内存泄漏检测Hook
export function useMemoryLeakDetection(componentName: string) {
  const timersRef = useRef<Set<NodeJS.Timeout>>(new Set());
  const intervalsRef = useRef<Set<NodeJS.Timeout>>(new Set());
  const listenersRef = useRef<Array<{ element: EventTarget; event: string; handler: EventListener }>>(
    []
  );

  const addTimer = useCallback((timer: NodeJS.Timeout) => {
    timersRef.current.add(timer);
    return timer;
  }, []);

  const addInterval = useCallback((interval: NodeJS.Timeout) => {
    intervalsRef.current.add(interval);
    return interval;
  }, []);

  const addEventListener = useCallback((
    element: EventTarget,
    event: string,
    handler: EventListener,
    options?: boolean | AddEventListenerOptions
  ) => {
    element.addEventListener(event, handler, options);
    listenersRef.current.push({ element, event, handler });
  }, []);

  useEffect(() => {
    return () => {
      // 清理定时器
      timersRef.current.forEach(timer => clearTimeout(timer));
      timersRef.current.clear();

      // 清理间隔器
      intervalsRef.current.forEach(interval => clearInterval(interval));
      intervalsRef.current.clear();

      // 清理事件监听器
      listenersRef.current.forEach(({ element, event, handler }) => {
        element.removeEventListener(event, handler);
      });
      listenersRef.current.length = 0;

      if (process.env.NODE_ENV === 'development') {
        console.log(`[Memory] ${componentName} cleaned up`);
      }
    };
  }, [componentName]);

  return {
    addTimer,
    addInterval,
    addEventListener,
  };
}
