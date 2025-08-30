import React from 'react';
import { Button, ButtonProps } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import './EnhancedGlassButton.css';

export interface EnhancedGlassButtonProps extends ButtonProps {
  /** 玻璃效果强度 */
  glassLevel?: 'sm' | 'md' | 'lg';
  /** 是否启用发光效果 */
  glow?: boolean;
  /** 自定义玻璃背景颜色 */
  glassColor?: string;
  /** 是否禁用毛玻璃效果（兼容性降级） */
  disableGlass?: boolean;
}

const EnhancedGlassButton: React.FC<EnhancedGlassButtonProps> = ({
  children,
  className = '',
  glassLevel = 'md',
  glow = false,
  glassColor,
  disableGlass = false,
  loading,
  type = 'default',
  ...rest
}) => {
  const getGlassClassName = () => {
    let baseClass = 'enhanced-glass-button';
    
    // 玻璃效果等级
    baseClass += ` glass-${glassLevel}`;
    
    // 按钮类型
    if (type === 'primary') {
      baseClass += ' glass-primary';
    } else if (type === 'dashed') {
      baseClass += ' glass-dashed';
    } else if (type === 'text') {
      baseClass += ' glass-text';
    } else if (type === 'link') {
      baseClass += ' glass-link';
    } else {
      baseClass += ' glass-default';
    }
    
    // 发光效果
    if (glow) {
      baseClass += ' glass-glow';
    }
    
    // 禁用玻璃效果
    if (disableGlass) {
      baseClass += ' glass-disabled';
    }
    
    return baseClass;
  };

  const customStyles: React.CSSProperties = {};
  
  // 自定义玻璃颜色
  if (glassColor) {
    customStyles['--glass-color' as any] = glassColor;
  }

  // 自定义加载图标
  const loadingIcon = loading ? <LoadingOutlined spin /> : null;

  return (
    <Button
      {...rest}
      type={type}
      loading={false} // 禁用默认loading，使用自定义
      className={`${getGlassClassName()} ${className}`.trim()}
      style={{ ...customStyles, ...rest.style }}
    >
      {loading && (
        <span className="glass-loading-icon">
          {loadingIcon}
        </span>
      )}
      <span className={`glass-content ${loading ? 'glass-loading' : ''}`}>
        {children}
      </span>
    </Button>
  );
};

export default EnhancedGlassButton;