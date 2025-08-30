// 性能优化工具集合

// 1. 防抖函数优化版
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  options: {
    leading?: boolean;
    trailing?: boolean;
    maxWait?: number;
  } = {}
): T & { cancel: () => void; flush: () => ReturnType<T> } {
  const { leading = false, trailing = true, maxWait } = options;
  
  let lastArgs: Parameters<T> | undefined;
  let lastThis: any;
  let maxTimeoutId: NodeJS.Timeout | undefined;
  let result: ReturnType<T>;
  let timerId: NodeJS.Timeout | undefined;
  let lastCallTime: number | undefined;
  let lastInvokeTime = 0;

  function invokeFunc(time: number): ReturnType<T> {
    const args = lastArgs!;
    const thisArg = lastThis;

    lastArgs = lastThis = undefined;
    lastInvokeTime = time;
    result = func.apply(thisArg, args);
    return result;
  }

  function leadingEdge(time: number): ReturnType<T> {
    lastInvokeTime = time;
    timerId = setTimeout(timerExpired, wait);
    return leading ? invokeFunc(time) : result;
  }

  function remainingWait(time: number): number {
    const timeSinceLastCall = time - lastCallTime!;
    const timeSinceLastInvoke = time - lastInvokeTime;
    const timeWaiting = wait - timeSinceLastCall;

    return maxWait !== undefined
      ? Math.min(timeWaiting, maxWait - timeSinceLastInvoke)
      : timeWaiting;
  }

  function shouldInvoke(time: number): boolean {
    const timeSinceLastCall = time - lastCallTime!;
    const timeSinceLastInvoke = time - lastInvokeTime;

    return (
      lastCallTime === undefined ||
      timeSinceLastCall >= wait ||
      timeSinceLastCall < 0 ||
      (maxWait !== undefined && timeSinceLastInvoke >= maxWait)
    );
  }

  function timerExpired(): ReturnType<T> | undefined {
    const time = Date.now();
    if (shouldInvoke(time)) {
      return trailingEdge(time);
    }
    timerId = setTimeout(timerExpired, remainingWait(time));
  }

  function trailingEdge(time: number): ReturnType<T> {
    timerId = undefined;

    if (trailing && lastArgs) {
      return invokeFunc(time);
    }
    lastArgs = lastThis = undefined;
    return result;
  }

  function cancel(): void {
    if (timerId !== undefined) {
      clearTimeout(timerId);
    }
    if (maxTimeoutId !== undefined) {
      clearTimeout(maxTimeoutId);
    }
    lastInvokeTime = 0;
    lastArgs = lastCallTime = lastThis = timerId = undefined;
  }

  function flush(): ReturnType<T> {
    return timerId === undefined ? result : trailingEdge(Date.now());
  }

  function debounced(...args: Parameters<T>): ReturnType<T> {
    const time = Date.now();
    const isInvoking = shouldInvoke(time);

    lastArgs = args;
    lastThis = this;
    lastCallTime = time;

    if (isInvoking) {
      if (timerId === undefined) {
        return leadingEdge(lastCallTime);
      }
      if (maxWait !== undefined) {
        timerId = setTimeout(timerExpired, wait);
        return invokeFunc(lastCallTime);
      }
    }
    if (timerId === undefined) {
      timerId = setTimeout(timerExpired, wait);
    }
    return result;
  }

  debounced.cancel = cancel;
  debounced.flush = flush;
  return debounced as T & { cancel: () => void; flush: () => ReturnType<T> };
}

// 2. 节流函数优化版
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  options: {
    leading?: boolean;
    trailing?: boolean;
  } = {}
): T & { cancel: () => void; flush: () => ReturnType<T> } {
  const { leading = true, trailing = true } = options;
  return debounce(func, wait, {
    leading,
    trailing,
    maxWait: wait,
  });
}

// 3. 内存优化的对象池
export class ObjectPool<T> {
  private pool: T[] = [];
  private createFn: () => T;
  private resetFn?: (obj: T) => void;
  private maxSize: number;

  constructor(
    createFn: () => T,
    resetFn?: (obj: T) => void,
    maxSize: number = 100
  ) {
    this.createFn = createFn;
    this.resetFn = resetFn;
    this.maxSize = maxSize;
  }

  acquire(): T {
    if (this.pool.length > 0) {
      return this.pool.pop()!;
    }
    return this.createFn();
  }

  release(obj: T): void {
    if (this.pool.length < this.maxSize) {
      if (this.resetFn) {
        this.resetFn(obj);
      }
      this.pool.push(obj);
    }
  }

  clear(): void {
    this.pool.length = 0;
  }

  size(): number {
    return this.pool.length;
  }
}

// 4. 批处理执行器
export class BatchProcessor<T> {
  private batch: T[] = [];
  private processFn: (items: T[]) => void;
  private batchSize: number;
  private delay: number;
  private timeoutId?: NodeJS.Timeout;

  constructor(
    processFn: (items: T[]) => void,
    batchSize: number = 10,
    delay: number = 100
  ) {
    this.processFn = processFn;
    this.batchSize = batchSize;
    this.delay = delay;
  }

  add(item: T): void {
    this.batch.push(item);

    if (this.batch.length >= this.batchSize) {
      this.flush();
    } else if (!this.timeoutId) {
      this.timeoutId = setTimeout(() => this.flush(), this.delay);
    }
  }

  flush(): void {
    if (this.batch.length > 0) {
      const items = this.batch.splice(0);
      this.processFn(items);
    }

    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = undefined;
    }
  }

  clear(): void {
    this.batch.length = 0;
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = undefined;
    }
  }
}

// 5. 智能重试机制
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number;
    baseDelay?: number;
    maxDelay?: number;
    backoffFactor?: number;
    shouldRetry?: (error: any) => boolean;
  } = {}
): Promise<T> {
  const {
    maxRetries = 3,
    baseDelay = 1000,
    maxDelay = 10000,
    backoffFactor = 2,
    shouldRetry = () => true,
  } = options;

  let lastError: any;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      if (attempt === maxRetries || !shouldRetry(error)) {
        throw error;
      }

      const delay = Math.min(
        baseDelay * Math.pow(backoffFactor, attempt),
        maxDelay
      );

      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError;
}

// 6. 资源预加载管理器
export class ResourcePreloader {
  private static cache = new Map<string, Promise<any>>();
  private static loaded = new Set<string>();

  static async preloadImage(src: string): Promise<HTMLImageElement> {
    if (this.loaded.has(src)) {
      const img = new Image();
      img.src = src;
      return img;
    }

    if (this.cache.has(src)) {
      return this.cache.get(src)!;
    }

    const promise = new Promise<HTMLImageElement>((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        this.loaded.add(src);
        resolve(img);
      };
      img.onerror = reject;
      img.src = src;
    });

    this.cache.set(src, promise);
    return promise;
  }

  static async preloadScript(src: string): Promise<void> {
    if (this.loaded.has(src)) {
      return;
    }

    if (this.cache.has(src)) {
      return this.cache.get(src)!;
    }

    const promise = new Promise<void>((resolve, reject) => {
      const script = document.createElement('script');
      script.onload = () => {
        this.loaded.add(src);
        resolve();
      };
      script.onerror = reject;
      script.src = src;
      document.head.appendChild(script);
    });

    this.cache.set(src, promise);
    return promise;
  }

  static async preloadCSS(href: string): Promise<void> {
    if (this.loaded.has(href)) {
      return;
    }

    if (this.cache.has(href)) {
      return this.cache.get(href)!;
    }

    const promise = new Promise<void>((resolve, reject) => {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.onload = () => {
        this.loaded.add(href);
        resolve();
      };
      link.onerror = reject;
      link.href = href;
      document.head.appendChild(link);
    });

    this.cache.set(href, promise);
    return promise;
  }

  static isLoaded(url: string): boolean {
    return this.loaded.has(url);
  }

  static clearCache(): void {
    this.cache.clear();
    this.loaded.clear();
  }
}

// 7. 性能监控工具
export class PerformanceTracker {
  private static marks = new Map<string, number>();
  private static measures = new Map<string, number>();

  static mark(name: string): void {
    this.marks.set(name, performance.now());
    if ('performance' in window && 'mark' in performance) {
      performance.mark(name);
    }
  }

  static measure(name: string, startMark: string, endMark?: string): number {
    const startTime = this.marks.get(startMark);
    if (!startTime) {
      console.warn(`Start mark "${startMark}" not found`);
      return 0;
    }

    const endTime = endMark ? this.marks.get(endMark) : performance.now();
    if (endMark && !endTime) {
      console.warn(`End mark "${endMark}" not found`);
      return 0;
    }

    const duration = (endTime || performance.now()) - startTime;
    this.measures.set(name, duration);

    if ('performance' in window && 'measure' in performance) {
      try {
        performance.measure(name, startMark, endMark);
      } catch (e) {
        // Fallback for browsers that don't support measure
      }
    }

    return duration;
  }

  static getMeasure(name: string): number | undefined {
    return this.measures.get(name);
  }

  static getAllMeasures(): Record<string, number> {
    return Object.fromEntries(this.measures);
  }

  static clear(): void {
    this.marks.clear();
    this.measures.clear();
    if ('performance' in window && 'clearMarks' in performance) {
      performance.clearMarks();
      performance.clearMeasures();
    }
  }
}

// 8. 导出所有优化工具
export {
  debounce as optimizedDebounce,
  throttle as optimizedThrottle,
  ObjectPool,
  BatchProcessor,
  retryWithBackoff,
  ResourcePreloader,
  PerformanceTracker,
};
