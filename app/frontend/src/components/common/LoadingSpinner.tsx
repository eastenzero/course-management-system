import React from 'react';
import { Spin, Space } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

export interface LoadingSpinnerProps {
  /** 加载状态 */
  loading?: boolean;
  /** 加载文本 */
  tip?: string;
  /** 大小 */
  size?: 'small' | 'default' | 'large';
  /** 延迟显示加载效果的时间（防止闪烁） */
  delay?: number;
  /** 自定义指示符 */
  indicator?: React.ReactElement;
  /** 是否居中显示 */
  centered?: boolean;
  /** 最小高度 */
  minHeight?: number | string;
  /** 自定义样式 */
  style?: React.CSSProperties;
  /** 自定义类名 */
  className?: string;
  /** 子组件 */
  children?: React.ReactNode;
  /** 是否显示背景遮罩 */
  spinning?: boolean;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  loading = true,
  tip = '加载中...',
  size = 'default',
  delay = 0,
  indicator,
  centered = true,
  minHeight = 200,
  style,
  className,
  children,
  spinning = true,
}) => {
  // 自定义加载指示符
  const customIndicator = indicator || (
    <LoadingOutlined style={{ fontSize: size === 'large' ? 32 : size === 'small' ? 16 : 24 }} spin />
  );

  // 如果有子组件，使用Spin包装
  if (children) {
    return (
      <Spin
        spinning={loading && spinning}
        tip={tip}
        size={size}
        delay={delay}
        indicator={customIndicator}
        style={style}
        className={className}
      >
        {children}
      </Spin>
    );
  }

  // 独立的加载组件
  const containerStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: centered ? 'center' : 'flex-start',
    alignItems: centered ? 'center' : 'flex-start',
    minHeight: typeof minHeight === 'number' ? `${minHeight}px` : minHeight,
    width: '100%',
    ...style,
  };

  if (!loading) {
    return null;
  }

  return (
    <div className={className} style={containerStyle}>
      <Space direction="vertical" align="center">
        <Spin
          size={size}
          indicator={customIndicator}
          delay={delay}
        />
        {tip && (
          <div style={{ 
            marginTop: 8, 
            color: '#666', 
            fontSize: size === 'large' ? 16 : size === 'small' ? 12 : 14 
          }}>
            {tip}
          </div>
        )}
      </Space>
    </div>
  );
};

// 预设的加载组件
export const PageLoading: React.FC<{ tip?: string }> = ({ tip = '页面加载中...' }) => (
  <LoadingSpinner
    size="large"
    tip={tip}
    minHeight="50vh"
    style={{ background: '#fafafa' }}
  />
);

export const TableLoading: React.FC<{ tip?: string }> = ({ tip = '数据加载中...' }) => (
  <LoadingSpinner
    size="default"
    tip={tip}
    minHeight={300}
  />
);

export const ButtonLoading: React.FC<{ tip?: string }> = ({ tip }) => (
  <LoadingSpinner
    size="small"
    tip={tip}
    centered={false}
    minHeight="auto"
    style={{ display: 'inline-flex', alignItems: 'center' }}
  />
);

export const FullScreenLoading: React.FC<{ tip?: string }> = ({ tip = '系统加载中...' }) => (
  <div style={{
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(255, 255, 255, 0.8)',
    zIndex: 9999,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  }}>
    <LoadingSpinner
      size="large"
      tip={tip}
      minHeight="auto"
      style={{ background: 'transparent' }}
    />
  </div>
);

export default LoadingSpinner;
