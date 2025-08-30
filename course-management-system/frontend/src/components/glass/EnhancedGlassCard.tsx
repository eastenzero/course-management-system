import React from 'react';
import { Card, CardProps } from 'antd';
import './EnhancedGlassCard.css';

export interface EnhancedGlassCardProps extends CardProps {
  /** 玻璃效果强度 */
  glassLevel?: 'sm' | 'md' | 'lg';
  /** 是否启用悬浮效果 */
  hoverable?: boolean;
  /** 是否启用边框发光 */
  borderGlow?: boolean;
  /** 自定义玻璃背景颜色 */
  glassColor?: string;
  /** 是否禁用毛玻璃效果（兼容性降级） */
  disableGlass?: boolean;
  /** 是否启用渐变背景 */
  gradientBg?: boolean;
}

const EnhancedGlassCard: React.FC<EnhancedGlassCardProps> = ({
  children,
  className = '',
  glassLevel = 'md',
  hoverable = true,
  borderGlow = false,
  glassColor,
  disableGlass = false,
  gradientBg = false,
  ...rest
}) => {
  const getGlassClassName = () => {
    let baseClass = 'enhanced-glass-card';
    
    // 玻璃效果等级
    baseClass += ` glass-${glassLevel}`;
    
    // 悬浮效果
    if (hoverable) {
      baseClass += ' glass-hoverable';
    }
    
    // 边框发光
    if (borderGlow) {
      baseClass += ' glass-border-glow';
    }
    
    // 禁用玻璃效果
    if (disableGlass) {
      baseClass += ' glass-disabled';
    }
    
    // 渐变背景
    if (gradientBg) {
      baseClass += ' glass-gradient';
    }
    
    return baseClass;
  };

  const customStyles: React.CSSProperties = {};
  
  // 自定义玻璃颜色
  if (glassColor) {
    customStyles['--glass-color' as any] = glassColor;
  }

  return (
    <Card
      {...rest}
      hoverable={false} // 禁用默认悬浮效果，使用自定义
      className={`${getGlassClassName()} ${className}`.trim()}
      style={{ ...customStyles, ...rest.style }}
    >
      {children}
    </Card>
  );
};

export default EnhancedGlassCard;