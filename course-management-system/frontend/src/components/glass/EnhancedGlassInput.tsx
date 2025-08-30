import React from 'react';
import { Input, InputProps } from 'antd';
import './EnhancedGlassInput.css';

export interface EnhancedGlassInputProps extends InputProps {
  /** 玻璃效果强度 */
  glassLevel?: 'sm' | 'md' | 'lg';
  /** 是否启用聚焦发光效果 */
  focusGlow?: boolean;
  /** 自定义玻璃背景颜色 */
  glassColor?: string;
  /** 是否禁用毛玻璃效果（兼容性降级） */
  disableGlass?: boolean;
  /** 是否启用浮动标签效果 */
  floatingLabel?: boolean;
}

const EnhancedGlassInput: React.FC<EnhancedGlassInputProps> = ({
  className = '',
  glassLevel = 'md',
  focusGlow = true,
  glassColor,
  disableGlass = false,
  floatingLabel = false,
  placeholder,
  ...rest
}) => {
  const getGlassClassName = () => {
    let baseClass = 'enhanced-glass-input';
    
    // 玻璃效果等级
    baseClass += ` glass-${glassLevel}`;
    
    // 聚焦发光
    if (focusGlow) {
      baseClass += ' glass-focus-glow';
    }
    
    // 禁用玻璃效果
    if (disableGlass) {
      baseClass += ' glass-disabled';
    }
    
    // 浮动标签
    if (floatingLabel) {
      baseClass += ' glass-floating-label';
    }
    
    return baseClass;
  };

  const customStyles: React.CSSProperties = {};
  
  // 自定义玻璃颜色
  if (glassColor) {
    customStyles['--glass-color' as any] = glassColor;
  }

  return (
    <div className="enhanced-glass-input-wrapper">
      <Input
        {...rest}
        placeholder={floatingLabel ? '' : placeholder}
        className={`${getGlassClassName()} ${className}`.trim()}
        style={{ ...customStyles, ...rest.style }}
      />
      {floatingLabel && placeholder && (
        <label className="glass-floating-label-text">
          {placeholder}
        </label>
      )}
    </div>
  );
};

// 密码输入框
const EnhancedGlassPasswordInput: React.FC<EnhancedGlassInputProps> = (props) => {
  return (
    <div className="enhanced-glass-input-wrapper">
      <Input.Password
        {...props}
        className={`enhanced-glass-input glass-${props.glassLevel || 'md'} ${
          props.focusGlow !== false ? 'glass-focus-glow' : ''
        } ${props.disableGlass ? 'glass-disabled' : ''} ${props.className || ''}`.trim()}
      />
    </div>
  );
};

// 文本域
const EnhancedGlassTextArea: React.FC<EnhancedGlassInputProps> = (props) => {
  return (
    <div className="enhanced-glass-input-wrapper">
      <Input.TextArea
        {...props}
        className={`enhanced-glass-input enhanced-glass-textarea glass-${props.glassLevel || 'md'} ${
          props.focusGlow !== false ? 'glass-focus-glow' : ''
        } ${props.disableGlass ? 'glass-disabled' : ''} ${props.className || ''}`.trim()}
      />
    </div>
  );
};

// 导出组合
EnhancedGlassInput.Password = EnhancedGlassPasswordInput;
EnhancedGlassInput.TextArea = EnhancedGlassTextArea;

export default EnhancedGlassInput;