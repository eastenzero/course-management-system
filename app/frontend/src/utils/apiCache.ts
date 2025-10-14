import { apiClient } from '../api/index';

// 简单的LRU缓存实现
class SimpleLRUCache<K, V> {
  private cache = new Map<K, V>();
  private maxSize: number;

  constructor(options: { max: number; ttl?: number }) {
    this.maxSize = options.max;
  }

  set(key: K, value: V): void {
    if (this.cache.has(key)) {
      this.cache.delete(key);
    } else if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(key, value);
  }

  get(key: K): V | undefined {
    if (this.cache.has(key)) {
      const value = this.cache.get(key);
      this.cache.delete(key);
      this.cache.set(key, value!);
      return value;
    }
    return undefined;
  }

  has(key: K): boolean {
    return this.cache.has(key);
  }

  delete(key: K): boolean {
    return this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  get size(): number {
    return this.cache.size;
  }

  // 添加遍历方法
  keys(): IterableIterator<K> {
    return this.cache.keys();
  }

  entries(): IterableIterator<[K, V]> {
    return this.cache.entries();
  }
}

// API缓存配置
interface CacheConfig {
  maxSize: number;
  ttl: number; // 生存时间（毫秒）
  staleWhileRevalidate: number; // 过期后仍可使用的时间
}

// 默认缓存配置
const DEFAULT_CACHE_CONFIG: CacheConfig = {
  maxSize: 100,
  ttl: 5 * 60 * 1000, // 5分钟
  staleWhileRevalidate: 2 * 60 * 1000, // 2分钟
};

// 缓存项接口
interface CacheItem<T> {
  data: T;
  timestamp: number;
  etag?: string;
  lastModified?: string;
}

// API缓存管理器
class ApiCacheManager {
  private cache: SimpleLRUCache<string, CacheItem<any>>;
  private config: CacheConfig;
  private pendingRequests: Map<string, Promise<any>> = new Map();

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = { ...DEFAULT_CACHE_CONFIG, ...config };
    this.cache = new SimpleLRUCache({
      max: this.config.maxSize,
      ttl: this.config.ttl,
    });
  }

  // 生成缓存键
  private generateKey(url: string, params?: Record<string, any>): string {
    const paramString = params ? JSON.stringify(params) : '';
    return `${url}:${paramString}`;
  }

  // 检查缓存是否有效
  private isValid(item: CacheItem<any>): boolean {
    const now = Date.now();
    const age = now - item.timestamp;
    return age < this.config.ttl;
  }

  // 检查缓存是否可以在重新验证时使用
  private isStaleButUsable(item: CacheItem<any>): boolean {
    const now = Date.now();
    const age = now - item.timestamp;
    return age < this.config.ttl + this.config.staleWhileRevalidate;
  }

  // 获取缓存
  get<T>(url: string, params?: Record<string, any>): T | null {
    const key = this.generateKey(url, params);
    const item = this.cache.get(key);

    if (!item) return null;

    if (this.isValid(item)) {
      return item.data;
    }

    // 如果缓存过期但仍可使用，返回数据但标记需要重新验证
    if (this.isStaleButUsable(item)) {
      // 异步重新验证
      this.revalidate(url, params).catch(console.error);
      return item.data;
    }

    // 缓存完全过期
    this.cache.delete(key);
    return null;
  }

  // 设置缓存
  set<T>(
    url: string,
    data: T,
    params?: Record<string, any>,
    headers?: Record<string, string>
  ): void {
    const key = this.generateKey(url, params);
    const item: CacheItem<T> = {
      data,
      timestamp: Date.now(),
      etag: headers?.etag,
      lastModified: headers?.['last-modified'],
    };

    this.cache.set(key, item);
  }

  // 删除缓存
  delete(url: string, params?: Record<string, any>): void {
    const key = this.generateKey(url, params);
    this.cache.delete(key);
  }

  // 清空所有缓存
  clear(): void {
    this.cache.clear();
    this.pendingRequests.clear();
  }

  // 按模式删除缓存
  deleteByPattern(pattern: string): void {
    const regex = new RegExp(pattern);
    // 使用keys()方法获取所有键
    const keys = Array.from(this.cache.keys());
    for (const key of keys) {
      if (regex.test(key)) {
        this.cache.delete(key);
      }
    }
  }

  // 重新验证缓存
  private async revalidate(url: string, params?: Record<string, any>): Promise<void> {
    const key = this.generateKey(url, params);
    
    // 避免重复请求
    if (this.pendingRequests.has(key)) {
      return this.pendingRequests.get(key);
    }

    const promise = this.fetchAndCache(url, params);
    this.pendingRequests.set(key, promise);

    try {
      await promise;
    } finally {
      this.pendingRequests.delete(key);
    }
  }

  // 获取数据并缓存
  private async fetchAndCache(url: string, params?: Record<string, any>): Promise<any> {
    try {
      // 使用配置好的axios实例，它会自动添加认证头
      const response = await apiClient.get(url, { params });

      // axios会自动解析JSON，response.data就是解析后的数据
      const data = response.data;
      const headers = {
        etag: response.headers.etag || undefined,
        'last-modified': response.headers['last-modified'] || undefined,
      };

      this.set(url, data, params, headers);
      return data;
    } catch (error: any) {
      // 如果是401错误，说明需要认证，抛出特定错误
      if (error.response?.status === 401) {
        throw new Error(`HTTP 401: Unauthorized`);
      }
      throw new Error(`HTTP ${error.response?.status || 'Unknown'}: ${error.response?.statusText || error.message}`);
    }
  }

  // 预加载数据
  async preload(url: string, params?: Record<string, any>): Promise<void> {
    const key = this.generateKey(url, params);
    
    // 如果已有有效缓存，不需要预加载
    const cached = this.get(url, params);
    if (cached) return;

    // 如果已有pending请求，等待完成
    if (this.pendingRequests.has(key)) {
      await this.pendingRequests.get(key);
      return;
    }

    await this.revalidate(url, params);
  }

  // 获取缓存统计信息
  getStats() {
    return {
      size: this.cache.size,
      maxSize: this.config.maxSize,
      pendingRequests: this.pendingRequests.size,
    };
  }
}

// 创建默认缓存实例
export const apiCache = new ApiCacheManager();

// 创建特定配置的缓存实例
export const createApiCache = (config: Partial<CacheConfig>) => {
  return new ApiCacheManager(config);
};

// 缓存装饰器
export function withCache<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  cacheConfig?: Partial<CacheConfig>
): T {
  const cache = cacheConfig ? createApiCache(cacheConfig) : apiCache;

  return (async (...args: Parameters<T>) => {
    const key = `${fn.name}:${JSON.stringify(args)}`;
    
    // 尝试从缓存获取
    const cached = cache.get(key);
    if (cached) return cached;

    // 执行函数并缓存结果
    const result = await fn(...args);
    cache.set(key, result);
    
    return result;
  }) as T;
}

// 请求去重装饰器
export function withDeduplication<T extends (...args: any[]) => Promise<any>>(fn: T): T {
  const pendingRequests = new Map<string, Promise<any>>();

  return (async (...args: Parameters<T>) => {
    const key = `${fn.name}:${JSON.stringify(args)}`;
    
    // 如果有pending请求，返回相同的Promise
    if (pendingRequests.has(key)) {
      return pendingRequests.get(key);
    }

    // 创建新请求
    const promise = fn(...args);
    pendingRequests.set(key, promise);

    try {
      const result = await promise;
      return result;
    } finally {
      pendingRequests.delete(key);
    }
  }) as T;
}

// 缓存失效策略
export class CacheInvalidationStrategy {
  private cache: ApiCacheManager;

  constructor(cache: ApiCacheManager = apiCache) {
    this.cache = cache;
  }

  // 基于时间的失效
  invalidateByTime(maxAge: number): void {
    // LRU缓存会自动处理TTL，这里可以添加额外逻辑
  }

  // 基于标签的失效
  invalidateByTags(tags: string[]): void {
    tags.forEach(tag => {
      this.cache.deleteByPattern(`.*:.*${tag}.*`);
    });
  }

  // 基于依赖的失效
  invalidateByDependency(dependency: string): void {
    this.cache.deleteByPattern(`.*${dependency}.*`);
  }

  // 手动失效特定缓存
  invalidateSpecific(url: string, params?: Record<string, any>): void {
    this.cache.delete(url, params);
  }

  // 失效所有缓存
  invalidateAll(): void {
    this.cache.clear();
  }
}

// 创建默认失效策略实例
export const cacheInvalidation = new CacheInvalidationStrategy();

// 缓存预热
export class CacheWarmer {
  private cache: ApiCacheManager;

  constructor(cache: ApiCacheManager = apiCache) {
    this.cache = cache;
  }

  // 预热常用数据
  async warmUp(urls: Array<{ url: string; params?: Record<string, any> }>): Promise<void> {
    const promises = urls.map(({ url, params }) => 
      this.cache.preload(url, params).catch(error => 
        console.warn(`Failed to preload ${url}:`, error)
      )
    );

    await Promise.allSettled(promises);
  }

  // 预热用户相关数据
  async warmUpUserData(userId: string): Promise<void> {
    const userUrls = [
      { url: `/api/users/${userId}` },
      { url: `/api/users/${userId}/courses` },
      { url: `/api/users/${userId}/schedule` },
    ];

    await this.warmUp(userUrls);
  }

  // 预热课程相关数据
  async warmUpCourseData(): Promise<void> {
    // 检查是否有认证token，没有则跳过需要认证的API预热
    const token = localStorage.getItem('token');
    if (!token) {
      if (process.env.NODE_ENV === 'development') {
        console.log('[Cache] Skipping authenticated API preloading - no token');
      }
      return;
    }

    // 使用更快的预热策略，不等待结果
    const courseUrls = [
      { url: '/courses/' },
      { url: '/classrooms/' },
    ];

    // 异步预热，不等待结果
    courseUrls.forEach(({ url }) => {
      this.cache.preload(url).catch(error => {
        // 静默失败，不影响用户体验
        if (process.env.NODE_ENV === 'development') {
          console.warn(`Failed to preload ${url}:`, error);
        }
      });
    });
  }
}

// 创建默认预热器实例
export const cacheWarmer = new CacheWarmer();

// 导出类型
export type { CacheConfig, CacheItem };
