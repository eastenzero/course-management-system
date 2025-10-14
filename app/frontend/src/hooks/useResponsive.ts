import { useState, useEffect } from 'react';

interface BreakpointValues {
  xs: boolean;  // < 576px
  sm: boolean;  // >= 576px
  md: boolean;  // >= 768px
  lg: boolean;  // >= 992px
  xl: boolean;  // >= 1200px
  xxl: boolean; // >= 1600px
}

interface DeviceInfo {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isTouch: boolean;
  orientation: 'portrait' | 'landscape';
  screenWidth: number;
  screenHeight: number;
}

interface ResponsiveInfo extends BreakpointValues, DeviceInfo {}

const breakpoints = {
  xs: 576,
  sm: 576,
  md: 768,
  lg: 992,
  xl: 1200,
  xxl: 1600,
};

export const useResponsive = (): ResponsiveInfo => {
  const [responsive, setResponsive] = useState<ResponsiveInfo>(() => {
    if (typeof window === 'undefined') {
      return {
        xs: false,
        sm: false,
        md: false,
        lg: false,
        xl: false,
        xxl: false,
        isMobile: false,
        isTablet: false,
        isDesktop: true,
        isTouch: false,
        orientation: 'landscape',
        screenWidth: 1200,
        screenHeight: 800,
      };
    }

    const width = window.innerWidth;
    const height = window.innerHeight;
    
    return {
      xs: width < breakpoints.xs,
      sm: width >= breakpoints.sm,
      md: width >= breakpoints.md,
      lg: width >= breakpoints.lg,
      xl: width >= breakpoints.xl,
      xxl: width >= breakpoints.xxl,
      isMobile: width < breakpoints.md,
      isTablet: width >= breakpoints.md && width < breakpoints.lg,
      isDesktop: width >= breakpoints.lg,
      isTouch: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
      orientation: width > height ? 'landscape' : 'portrait',
      screenWidth: width,
      screenHeight: height,
    };
  });

  useEffect(() => {
    const updateResponsive = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      
      setResponsive({
        xs: width < breakpoints.xs,
        sm: width >= breakpoints.sm,
        md: width >= breakpoints.md,
        lg: width >= breakpoints.lg,
        xl: width >= breakpoints.xl,
        xxl: width >= breakpoints.xxl,
        isMobile: width < breakpoints.md,
        isTablet: width >= breakpoints.md && width < breakpoints.lg,
        isDesktop: width >= breakpoints.lg,
        isTouch: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
        orientation: width > height ? 'landscape' : 'portrait',
        screenWidth: width,
        screenHeight: height,
      });
    };

    // 防抖处理
    let timeoutId: NodeJS.Timeout;
    const debouncedUpdate = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(updateResponsive, 150);
    };

    window.addEventListener('resize', debouncedUpdate);
    window.addEventListener('orientationchange', debouncedUpdate);

    return () => {
      window.removeEventListener('resize', debouncedUpdate);
      window.removeEventListener('orientationchange', debouncedUpdate);
      clearTimeout(timeoutId);
    };
  }, []);

  return responsive;
};

// 获取当前断点名称
export const useCurrentBreakpoint = (): string => {
  const responsive = useResponsive();
  
  if (responsive.xxl) return 'xxl';
  if (responsive.xl) return 'xl';
  if (responsive.lg) return 'lg';
  if (responsive.md) return 'md';
  if (responsive.sm) return 'sm';
  return 'xs';
};

// 检查是否为移动设备
export const useIsMobile = (): boolean => {
  const responsive = useResponsive();
  return responsive.isMobile;
};

// 检查是否为触摸设备
export const useIsTouch = (): boolean => {
  const responsive = useResponsive();
  return responsive.isTouch;
};

// 获取设备方向
export const useOrientation = (): 'portrait' | 'landscape' => {
  const responsive = useResponsive();
  return responsive.orientation;
};

// 根据断点返回不同的值
export const useBreakpointValue = <T>(values: {
  xs?: T;
  sm?: T;
  md?: T;
  lg?: T;
  xl?: T;
  xxl?: T;
}): T | undefined => {
  const responsive = useResponsive();
  
  if (responsive.xxl && values.xxl !== undefined) return values.xxl;
  if (responsive.xl && values.xl !== undefined) return values.xl;
  if (responsive.lg && values.lg !== undefined) return values.lg;
  if (responsive.md && values.md !== undefined) return values.md;
  if (responsive.sm && values.sm !== undefined) return values.sm;
  if (responsive.xs && values.xs !== undefined) return values.xs;
  
  // 返回最接近的值
  const breakpointOrder = ['xxl', 'xl', 'lg', 'md', 'sm', 'xs'] as const;
  for (const bp of breakpointOrder) {
    if (values[bp] !== undefined) return values[bp];
  }
  
  return undefined;
};

// 获取响应式的列数
export const useResponsiveColumns = (
  desktop: number = 4,
  tablet: number = 2,
  mobile: number = 1
): number => {
  const responsive = useResponsive();
  
  if (responsive.isMobile) return mobile;
  if (responsive.isTablet) return tablet;
  return desktop;
};

// 获取响应式的间距
export const useResponsiveGutter = (): [number, number] => {
  const responsive = useResponsive();
  
  if (responsive.isMobile) return [8, 8];
  if (responsive.isTablet) return [12, 12];
  return [16, 16];
};

// 获取响应式的卡片大小
export const useResponsiveCardSize = (): 'small' | 'default' => {
  const responsive = useResponsive();
  return responsive.isMobile ? 'small' : 'default';
};

// 获取响应式的表格滚动配置
export const useResponsiveTableScroll = (minWidth: number = 800) => {
  const responsive = useResponsive();
  
  return {
    x: responsive.isMobile ? minWidth : undefined,
    y: responsive.isMobile ? 400 : undefined,
  };
};

export default useResponsive;
