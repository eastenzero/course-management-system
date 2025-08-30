/**
 * 玻璃效果性能优化器
 * 根据设备性能和浏览器支持情况自动调整玻璃效果
 */

interface DeviceCapabilities {
  supportsBackdropFilter: boolean;
  deviceMemory: number;
  hardwareConcurrency: number;
  connectionType: string;
  isLowEndDevice: boolean;
}

interface GlassOptimizationConfig {
  enableGlass: boolean;
  blurLevel: 'none' | 'low' | 'medium' | 'high';
  maxBlurLayers: number;
  enableNoise: boolean;
  enableAnimations: boolean;
  fallbackMode: 'transparent' | 'solid' | 'gradient';
}

class GlassEffectOptimizer {
  private static instance: GlassEffectOptimizer;
  private deviceCapabilities: DeviceCapabilities;
  private optimizationConfig: GlassOptimizationConfig;
  private performanceObserver: PerformanceObserver | null = null;
  private frameDropCount = 0;
  private lastFrameTime = 0;

  private constructor() {
    this.deviceCapabilities = this.detectDeviceCapabilities();
    this.optimizationConfig = this.generateOptimizationConfig();
    this.initPerformanceMonitoring();
    this.applyOptimizations();
  }

  public static getInstance(): GlassEffectOptimizer {
    if (!GlassEffectOptimizer.instance) {
      GlassEffectOptimizer.instance = new GlassEffectOptimizer();
    }
    return GlassEffectOptimizer.instance;
  }

  /**
   * 检测设备能力
   */
  private detectDeviceCapabilities(): DeviceCapabilities {
    const supportsBackdropFilter = this.checkBackdropFilterSupport();
    const deviceMemory = (navigator as any).deviceMemory || 4; // 默认4GB
    const hardwareConcurrency = navigator.hardwareConcurrency || 4;
    const connectionType = this.getConnectionType();
    
    // 判断是否为低端设备
    const isLowEndDevice = deviceMemory <= 2 || hardwareConcurrency <= 2 || 
                          connectionType === 'slow-2g' || connectionType === '2g';

    return {
      supportsBackdropFilter,
      deviceMemory,
      hardwareConcurrency,
      connectionType,
      isLowEndDevice
    };
  }

  /**
   * 检查backdrop-filter支持
   */
  private checkBackdropFilterSupport(): boolean {
    if (typeof window === 'undefined') return false;
    
    return CSS.supports('backdrop-filter', 'blur(1px)') || 
           CSS.supports('-webkit-backdrop-filter', 'blur(1px)');
  }

  /**
   * 获取网络连接类型
   */
  private getConnectionType(): string {
    const connection = (navigator as any).connection || 
                      (navigator as any).mozConnection || 
                      (navigator as any).webkitConnection;
    
    return connection?.effectiveType || 'unknown';
  }

  /**
   * 生成优化配置
   */
  private generateOptimizationConfig(): GlassOptimizationConfig {
    const { supportsBackdropFilter, isLowEndDevice, connectionType } = this.deviceCapabilities;

    // 低端设备或不支持backdrop-filter时的降级配置
    if (!supportsBackdropFilter || isLowEndDevice) {
      return {
        enableGlass: false,
        blurLevel: 'none',
        maxBlurLayers: 0,
        enableNoise: false,
        enableAnimations: false,
        fallbackMode: 'transparent'
      };
    }

    // 根据网络状况调整
    if (connectionType === 'slow-2g' || connectionType === '2g') {
      return {
        enableGlass: true,
        blurLevel: 'low',
        maxBlurLayers: 1,
        enableNoise: false,
        enableAnimations: false,
        fallbackMode: 'transparent'
      };
    }

    // 中等性能设备
    if (this.deviceCapabilities.deviceMemory <= 4) {
      return {
        enableGlass: true,
        blurLevel: 'medium',
        maxBlurLayers: 2,
        enableNoise: false,
        enableAnimations: true,
        fallbackMode: 'gradient'
      };
    }

    // 高性能设备
    return {
      enableGlass: true,
      blurLevel: 'high',
      maxBlurLayers: 3,
      enableNoise: true,
      enableAnimations: true,
      fallbackMode: 'gradient'
    };
  }

  /**
   * 初始化性能监控
   */
  private initPerformanceMonitoring(): void {
    if (typeof window === 'undefined' || !window.PerformanceObserver) return;

    try {
      this.performanceObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          if (entry.entryType === 'measure' && entry.name.includes('frame')) {
            this.checkFramePerformance(entry.duration);
          }
        });
      });

      this.performanceObserver.observe({ entryTypes: ['measure'] });
    } catch (error) {
      console.warn('Performance monitoring not available:', error);
    }

    // 监听用户偏好变化
    this.listenToUserPreferences();
  }

  /**
   * 监听用户偏好设置
   */
  private listenToUserPreferences(): void {
    // 监听减少动效偏好
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    prefersReducedMotion.addEventListener('change', (e) => {
      this.optimizationConfig.enableAnimations = !e.matches;
      this.applyOptimizations();
    });

    // 监听高对比度偏好
    const prefersHighContrast = window.matchMedia('(prefers-contrast: high)');
    prefersHighContrast.addEventListener('change', (e) => {
      if (e.matches) {
        this.optimizationConfig.enableGlass = false;
        this.optimizationConfig.fallbackMode = 'solid';
      }
      this.applyOptimizations();
    });
  }

  /**
   * 检查帧性能
   */
  private checkFramePerformance(frameDuration: number): void {
    const currentTime = performance.now();
    
    // 如果帧时间超过16.67ms (60fps)，认为是掉帧
    if (frameDuration > 16.67) {
      this.frameDropCount++;
    }

    // 每秒检查一次性能
    if (currentTime - this.lastFrameTime > 1000) {
      if (this.frameDropCount > 10) { // 如果1秒内掉帧超过10次
        this.degradePerformance();
      }
      
      this.frameDropCount = 0;
      this.lastFrameTime = currentTime;
    }
  }

  /**
   * 降级性能设置
   */
  private degradePerformance(): void {
    if (this.optimizationConfig.blurLevel === 'high') {
      this.optimizationConfig.blurLevel = 'medium';
      this.optimizationConfig.maxBlurLayers = Math.max(1, this.optimizationConfig.maxBlurLayers - 1);
    } else if (this.optimizationConfig.blurLevel === 'medium') {
      this.optimizationConfig.blurLevel = 'low';
      this.optimizationConfig.enableNoise = false;
    } else if (this.optimizationConfig.blurLevel === 'low') {
      this.optimizationConfig.enableGlass = false;
    }

    this.applyOptimizations();
    console.warn('Glass effect performance degraded due to frame drops');
  }

  /**
   * 应用优化设置
   */
  private applyOptimizations(): void {
    const root = document.documentElement;
    
    // 设置CSS变量
    root.style.setProperty('--glass-enabled', this.optimizationConfig.enableGlass ? '1' : '0');
    root.style.setProperty('--glass-blur-level', this.optimizationConfig.blurLevel);
    root.style.setProperty('--glass-max-layers', this.optimizationConfig.maxBlurLayers.toString());
    root.style.setProperty('--glass-noise-enabled', this.optimizationConfig.enableNoise ? '1' : '0');
    root.style.setProperty('--glass-animations-enabled', this.optimizationConfig.enableAnimations ? '1' : '0');
    
    // 设置数据属性
    root.setAttribute('data-glass-enabled', this.optimizationConfig.enableGlass.toString());
    root.setAttribute('data-glass-fallback', this.optimizationConfig.fallbackMode);
    
    // 触发自定义事件
    window.dispatchEvent(new CustomEvent('glassOptimizationChanged', {
      detail: this.optimizationConfig
    }));
  }

  /**
   * 获取当前优化配置
   */
  public getOptimizationConfig(): GlassOptimizationConfig {
    return { ...this.optimizationConfig };
  }

  /**
   * 获取设备能力信息
   */
  public getDeviceCapabilities(): DeviceCapabilities {
    return { ...this.deviceCapabilities };
  }

  /**
   * 手动设置优化级别
   */
  public setOptimizationLevel(level: 'auto' | 'high' | 'medium' | 'low' | 'off'): void {
    switch (level) {
      case 'high':
        this.optimizationConfig = {
          enableGlass: true,
          blurLevel: 'high',
          maxBlurLayers: 3,
          enableNoise: true,
          enableAnimations: true,
          fallbackMode: 'gradient'
        };
        break;
      case 'medium':
        this.optimizationConfig = {
          enableGlass: true,
          blurLevel: 'medium',
          maxBlurLayers: 2,
          enableNoise: false,
          enableAnimations: true,
          fallbackMode: 'gradient'
        };
        break;
      case 'low':
        this.optimizationConfig = {
          enableGlass: true,
          blurLevel: 'low',
          maxBlurLayers: 1,
          enableNoise: false,
          enableAnimations: false,
          fallbackMode: 'transparent'
        };
        break;
      case 'off':
        this.optimizationConfig = {
          enableGlass: false,
          blurLevel: 'none',
          maxBlurLayers: 0,
          enableNoise: false,
          enableAnimations: false,
          fallbackMode: 'solid'
        };
        break;
      case 'auto':
      default:
        this.optimizationConfig = this.generateOptimizationConfig();
        break;
    }
    
    this.applyOptimizations();
  }

  /**
   * 销毁优化器
   */
  public destroy(): void {
    if (this.performanceObserver) {
      this.performanceObserver.disconnect();
      this.performanceObserver = null;
    }
  }
}

// 导出单例实例
export const glassOptimizer = GlassEffectOptimizer.getInstance();
export default GlassEffectOptimizer;
