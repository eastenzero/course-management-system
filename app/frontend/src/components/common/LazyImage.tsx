import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Skeleton } from 'antd';

export interface LazyImageProps extends Omit<React.ImgHTMLAttributes<HTMLImageElement>, 'loading'> {
  /** 图片源 */
  src: string;
  /** 占位图片 */
  placeholder?: string;
  /** 错误时显示的图片 */
  fallback?: string;
  /** 是否启用懒加载 */
  lazy?: boolean;
  /** 根边距，用于提前加载 */
  rootMargin?: string;
  /** 加载状态组件 */
  loadingComponent?: React.ReactNode;
  /** 错误状态组件 */
  error?: React.ReactNode;
  /** 加载完成回调 */
  onLoad?: () => void;
  /** 加载错误回调 */
  onError?: () => void;
  /** 自定义样式 */
  style?: React.CSSProperties;
  /** 自定义类名 */
  className?: string;
}

const LazyImage: React.FC<LazyImageProps> = ({
  src,
  placeholder,
  fallback,
  lazy = true,
  rootMargin = '50px',
  loadingComponent,
  error,
  onLoad,
  onError,
  style,
  className,
  alt = '',
  ...props
}) => {
  const [imageState, setImageState] = useState<'loading' | 'loaded' | 'error'>('loading');
  const [imageSrc, setImageSrc] = useState<string>(placeholder || '');
  const [isInView, setIsInView] = useState(!lazy);
  const imgRef = useRef<HTMLImageElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);

  // 创建 Intersection Observer
  useEffect(() => {
    if (!lazy || isInView) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true);
            observer.disconnect();
          }
        });
      },
      {
        rootMargin,
        threshold: 0.1,
      }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    observerRef.current = observer;

    return () => {
      observer.disconnect();
    };
  }, [lazy, isInView, rootMargin]);

  // 加载图片
  useEffect(() => {
    if (!isInView || !src) return;

    const img = new Image();
    
    img.onload = () => {
      setImageState('loaded');
      setImageSrc(src);
      if (onLoad) {
        onLoad();
      }
    };

    img.onerror = () => {
      setImageState('error');
      if (fallback) {
        setImageSrc(fallback);
      }
      if (onError) {
        onError();
      }
    };

    img.src = src;

    return () => {
      img.onload = null;
      img.onerror = null;
    };
  }, [isInView, src, fallback, onLoad, onError]);

  // 渲染加载状态
  const renderLoading = useCallback(() => {
    if (loadingComponent) {
      return loadingComponent;
    }

    return (
      <Skeleton.Image
        style={{
          width: style?.width || props.width || '100%',
          height: style?.height || props.height || 'auto',
        }}
      />
    );
  }, [loadingComponent, style, props.width, props.height]);

  // 渲染错误状态
  const renderError = useCallback(() => {
    if (error) {
      return error;
    }

    return (
      <div
        style={{
          width: style?.width || props.width || '100%',
          height: style?.height || props.height || 'auto',
          backgroundColor: '#f5f5f5',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#999',
          fontSize: '12px',
          ...style,
        }}
        className={className}
      >
        图片加载失败
      </div>
    );
  }, [error, style, props.width, props.height, className]);

  // 如果还在加载中且不在视口内
  if (!isInView) {
    return (
      <div
        ref={imgRef}
        style={{
          width: style?.width || props.width || '100%',
          height: style?.height || props.height || 'auto',
          ...style,
        }}
        className={className}
      >
        {renderLoading()}
      </div>
    );
  }

  // 如果加载失败
  if (imageState === 'error' && !fallback) {
    return renderError();
  }

  // 如果还在加载中
  if (imageState === 'loading') {
    return (
      <div
        ref={imgRef}
        style={{
          width: style?.width || props.width || '100%',
          height: style?.height || props.height || 'auto',
          ...style,
        }}
        className={className}
      >
        {renderLoading()}
      </div>
    );
  }

  // 渲染图片
  return (
    <img
      ref={imgRef}
      src={imageSrc}
      alt={alt}
      style={style}
      className={className}
      {...props}
    />
  );
};

export default React.memo(LazyImage);
